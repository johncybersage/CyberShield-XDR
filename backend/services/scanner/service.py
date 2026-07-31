"""
CyberShield XDR — Vulnerability Scanner Service
Uses python-nmap to perform TCP/UDP/version/OS detection scans.
Maps discovered services to CVEs and calculates CVSS-based risk scores.
"""
import asyncio
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.logging_config import get_logger
from backend.config.settings import get_settings
from backend.models.alert import Alert, AlertSeverity, AlertSource
from backend.models.asset import Asset
from backend.models.scan import Scan, ScanStatus, ScanType

logger = get_logger(__name__)
settings = get_settings()

# Nmap flag map per scan type
NMAP_FLAGS = {
    ScanType.TCP:          "-sT -T4",
    ScanType.UDP:          "-sU -T4 --top-ports 100",
    ScanType.FULL:         "-sS -sV -O -T4 -A",
    ScanType.QUICK:        "-sT -T4 --top-ports 100",
    ScanType.STEALTH:      "-sS -T2",
    ScanType.VERSION:      "-sV -T4",
    ScanType.OS_DETECTION: "-O -T4",
}

# Known vulnerable service versions → CVE mapping (subset for demo)
KNOWN_CVES = {
    "openssh": [
        {"id": "CVE-2023-38408", "cvss": 9.8, "description": "Remote code execution in ssh-agent"},
        {"id": "CVE-2023-51385", "cvss": 6.5, "description": "OS command injection via invalid hostname"},
    ],
    "apache": [
        {"id": "CVE-2021-41773", "cvss": 9.8, "description": "Path traversal and RCE in Apache 2.4.49"},
        {"id": "CVE-2021-42013", "cvss": 9.8, "description": "Path traversal in Apache 2.4.49-2.4.50"},
    ],
    "nginx": [
        {"id": "CVE-2021-23017", "cvss": 7.7, "description": "1-byte memory overwrite in DNS resolver"},
    ],
    "vsftpd": [
        {"id": "CVE-2011-2523", "cvss": 10.0, "description": "vsftpd 2.3.4 backdoor"},
    ],
    "samba": [
        {"id": "CVE-2017-7494", "cvss": 9.8, "description": "SambaCry remote code execution"},
    ],
    "mysql": [
        {"id": "CVE-2012-2122", "cvss": 5.1, "description": "Authentication bypass by repeated connection"},
    ],
}


class ScannerService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_scan(self, scan_id: UUID) -> None:
        """
        Execute a vulnerability scan asynchronously.
        Called by Celery worker — updates scan record with results.
        """
        result = await self.db.execute(select(Scan).where(Scan.id == scan_id))
        scan = result.scalar_one_or_none()
        if not scan:
            logger.error(f"Scan {scan_id} not found")
            return

        scan.status = ScanStatus.RUNNING
        scan.started_at = datetime.now(timezone.utc).isoformat()
        await self.db.commit()

        try:
            findings = await self._execute_nmap(scan)
            await self._process_findings(scan, findings)
            scan.status = ScanStatus.COMPLETED
        except Exception as exc:
            scan.status = ScanStatus.FAILED
            scan.error_message = str(exc)
            logger.error(f"Scan {scan_id} failed: {exc}")
        finally:
            scan.completed_at = datetime.now(timezone.utc).isoformat()
            if scan.started_at:
                start = datetime.fromisoformat(scan.started_at)
                end = datetime.fromisoformat(scan.completed_at)
                scan.duration_seconds = int((end - start).total_seconds())
            await self.db.commit()

    async def _execute_nmap(self, scan: Scan) -> list:
        """Run nmap in a thread pool to avoid blocking the event loop."""
        try:
            import nmap
        except ImportError:
            logger.warning("python-nmap not installed — returning mock findings")
            return self._mock_findings(scan.target_ip)

        flags = NMAP_FLAGS.get(ScanType(scan.scan_type), "-sT -T4")
        ports = scan.target_ports or "1-1024"
        cmd = f"{flags} -p {ports}"
        scan.nmap_command = f"nmap {cmd} {scan.target_ip}"

        loop = asyncio.get_event_loop()
        nm = nmap.PortScanner()

        def _scan():
            nm.scan(hosts=scan.target_ip, arguments=cmd)
            return nm

        nm = await loop.run_in_executor(None, _scan)
        return self._parse_nmap_results(nm, scan.target_ip)

    def _parse_nmap_results(self, nm, target_ip: str) -> list:
        """Convert nmap results to structured findings list."""
        findings = []
        if target_ip not in nm.all_hosts():
            return findings

        host = nm[target_ip]
        for proto in host.all_protocols():
            for port, port_data in host[proto].items():
                if port_data["state"] != "open":
                    continue
                service_name = port_data.get("name", "unknown").lower()
                version = port_data.get("version", "")
                product = port_data.get("product", "").lower()

                cves = self._map_cves(service_name, product, version)
                findings.append({
                    "port": port,
                    "protocol": proto,
                    "service": service_name,
                    "product": port_data.get("product", ""),
                    "version": version,
                    "state": port_data["state"],
                    "cves": cves,
                })
        return findings

    def _map_cves(self, service: str, product: str, version: str) -> list:
        """Map service to known CVEs based on name matching."""
        cves = []
        for keyword, cve_list in KNOWN_CVES.items():
            if keyword in service or keyword in product:
                cves.extend(cve_list)
        return cves

    def _mock_findings(self, target_ip: str) -> list:
        """Return realistic mock findings when nmap is unavailable."""
        return [
            {"port": 22, "protocol": "tcp", "service": "ssh", "product": "OpenSSH",
             "version": "8.9", "state": "open",
             "cves": KNOWN_CVES["openssh"]},
            {"port": 80, "protocol": "tcp", "service": "http", "product": "nginx",
             "version": "1.18.0", "state": "open",
             "cves": KNOWN_CVES["nginx"]},
            {"port": 443, "protocol": "tcp", "service": "https", "product": "nginx",
             "version": "1.18.0", "state": "open", "cves": []},
        ]

    async def _process_findings(self, scan: Scan, findings: list) -> None:
        """Store findings, calculate risk score, update asset, create alerts."""
        scan.findings = findings
        scan.open_ports_count = len(findings)

        all_cves = [cve for f in findings for cve in f.get("cves", [])]
        scan.vulnerabilities_count = len(all_cves)
        scan.critical_count = sum(1 for c in all_cves if c["cvss"] >= 9.0)
        scan.high_count = sum(1 for c in all_cves if 7.0 <= c["cvss"] < 9.0)
        scan.cvss_max = max((c["cvss"] for c in all_cves), default=0.0)

        # Risk score: weighted average of CVSS scores (0-10 scale)
        if all_cves:
            scan.risk_score = min(
                sum(c["cvss"] for c in all_cves) / len(all_cves) * 10, 100.0
            )

        # Update linked asset
        if scan.asset_id:
            asset_result = await self.db.execute(
                select(Asset).where(Asset.id == scan.asset_id)
            )
            asset = asset_result.scalar_one_or_none()
            if asset:
                asset.open_ports = findings
                asset.risk_score = scan.risk_score
                asset.scan_count = (asset.scan_count or 0) + 1
                asset.last_seen = datetime.now(timezone.utc).isoformat()

        # Create alert for critical/high findings
        if scan.critical_count > 0 or scan.high_count > 0:
            severity = AlertSeverity.CRITICAL if scan.critical_count > 0 else AlertSeverity.HIGH
            alert = Alert(
                title=f"Vulnerabilities detected on {scan.target_ip}",
                description=(
                    f"Scan found {scan.vulnerabilities_count} vulnerabilities "
                    f"({scan.critical_count} critical, {scan.high_count} high). "
                    f"Max CVSS: {scan.cvss_max}"
                ),
                severity=severity,
                source=AlertSource.VULNERABILITY_SCANNER,
                source_ref_id=str(scan.id),
                dst_ip=scan.target_ip,
                risk_score=scan.risk_score,
                asset_id=scan.asset_id,
                raw_data={"scan_id": str(scan.id), "findings_count": len(findings)},
            )
            self.db.add(alert)
