import os
import re
from datetime import datetime, timezone
from typing import Tuple

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.logging_config import get_logger
from backend.models.threat_intel import IOCType, ThreatCategory, ThreatIntelligence

logger = get_logger(__name__)

class ThreatIntelService:
    def __init__(self):
        self.abuseipdb_key = os.getenv("ABUSEIPDB_API_KEY", "")
        self.vt_key = os.getenv("VT_API_KEY", "")
        self.otx_key = os.getenv("OTX_API_KEY", "")

    def _determine_ioc_type(self, value: str) -> IOCType:
        # Basic regexes for identification
        if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", value):
            return IOCType.IP
        if re.match(r"^[a-fA-F0-9]{32}$", value):
            return IOCType.FILE_HASH_MD5
        if re.match(r"^[a-fA-F0-9]{64}$", value):
            return IOCType.FILE_HASH_SHA256
        if "@" in value:
            return IOCType.EMAIL
        if value.startswith("http"):
            return IOCType.URL
        return IOCType.DOMAIN

    async def _fetch_abuseipdb(self, ip: str) -> dict:
        if not self.abuseipdb_key:
            return {"mock": True, "abuseConfidenceScore": 50, "countryCode": "US", "isp": "Mock ISP"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://api.abuseipdb.com/api/v2/check",
                    headers={"Key": self.abuseipdb_key, "Accept": "application/json"},
                    params={"ipAddress": ip, "maxAgeInDays": 90},
                    timeout=5.0
                )
                if response.status_code == 200:
                    return response.json().get("data", {})
            except Exception as e:
                logger.error(f"AbuseIPDB error: {e}")
        return {}

    async def _fetch_virustotal(self, ioc: str, ioc_type: IOCType) -> dict:
        if not self.vt_key:
            return {"mock": True, "last_analysis_stats": {"malicious": 3, "undetected": 85}}
            
        endpoint_map = {
            IOCType.IP: f"ip_addresses/{ioc}",
            IOCType.DOMAIN: f"domains/{ioc}",
            IOCType.FILE_HASH_MD5: f"files/{ioc}",
            IOCType.FILE_HASH_SHA256: f"files/{ioc}",
            IOCType.URL: f"urls/{httpx.URL(ioc).path}" # Naive mapping for URL
        }
        
        if ioc_type not in endpoint_map:
            return {}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"https://www.virustotal.com/api/v3/{endpoint_map[ioc_type]}",
                    headers={"x-apikey": self.vt_key},
                    timeout=5.0
                )
                if response.status_code == 200:
                    return response.json().get("data", {}).get("attributes", {})
            except Exception as e:
                logger.error(f"VirusTotal error: {e}")
        return {}

    async def _fetch_otx(self, ioc: str, ioc_type: IOCType) -> dict:
        if not self.otx_key:
            return {"mock": True, "pulse_info": {"count": 1}}

        endpoint_map = {
            IOCType.IP: f"IPv4/{ioc}",
            IOCType.DOMAIN: f"domain/{ioc}",
            IOCType.FILE_HASH_MD5: f"file/{ioc}",
            IOCType.FILE_HASH_SHA256: f"file/{ioc}"
        }
        
        if ioc_type not in endpoint_map:
            return {}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"https://otx.alienvault.com/api/v1/indicators/{endpoint_map[ioc_type]}/general",
                    headers={"X-OTX-API-KEY": self.otx_key},
                    timeout=5.0
                )
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                logger.error(f"OTX error: {e}")
        return {}

    def _calculate_threat_score(self, abuse_data: dict, vt_data: dict, otx_data: dict) -> Tuple[float, bool]:
        score = 0.0
        
        # AbuseIPDB (0-100 score) - Weight 40%
        abuse_score = abuse_data.get("abuseConfidenceScore", 0)
        score += (abuse_score * 0.4)
        
        # VirusTotal (usually 0-90 engines) - Weight 40%
        vt_stats = vt_data.get("last_analysis_stats", {})
        vt_malicious = vt_stats.get("malicious", 0)
        vt_total = sum(vt_stats.values()) if vt_stats else 1
        if vt_total > 0:
            vt_score = min(100, (vt_malicious / max(1, min(10, vt_total))) * 100) # Normalize
            score += (vt_score * 0.4)
            
        # OTX (pulse count) - Weight 20%
        otx_pulses = otx_data.get("pulse_info", {}).get("count", 0)
        otx_score = min(100, otx_pulses * 10) # 10 pulses = 100 score
        score += (otx_score * 0.2)
        
        return min(100.0, score), score > 30.0

    async def lookup_ioc(self, db: AsyncSession, value: str) -> ThreatIntelligence:
        # Check if recently cached (last 24 hours)
        result = await db.execute(select(ThreatIntelligence).where(ThreatIntelligence.value == value))
        existing = result.scalar_one_or_none()
        
        # If exists and not expired, return it
        # (For simplicity here we just do a fresh lookup if the user requested it, or return it if it's there. Let's do a fresh lookup on explicit request)
        
        ioc_type = self._determine_ioc_type(value)
        
        # Parallel fetch would be better, but doing sequential for simplicity
        abuse_data = await self._fetch_abuseipdb(value) if ioc_type == IOCType.IP else {}
        vt_data = await self._fetch_virustotal(value, ioc_type)
        otx_data = await self._fetch_otx(value, ioc_type)
        
        score, is_malicious = self._calculate_threat_score(abuse_data, vt_data, otx_data)
        
        vt_stats = vt_data.get("last_analysis_stats", {})
        
        ti_data = {
            "ioc_type": ioc_type,
            "value": value,
            "abuse_confidence_score": abuse_data.get("abuseConfidenceScore", 0),
            "vt_malicious_count": vt_stats.get("malicious", 0),
            "vt_total_count": sum(vt_stats.values()) if vt_stats else 0,
            "otx_pulse_count": otx_data.get("pulse_info", {}).get("count", 0),
            "threat_category": ThreatCategory.MALWARE if is_malicious else ThreatCategory.UNKNOWN,
            "threat_score": score,
            "is_malicious": is_malicious,
            "country_code": abuse_data.get("countryCode") or otx_data.get("country_code"),
            "asn": abuse_data.get("isp"),
            "isp": abuse_data.get("isp"),
            "abuseipdb_data": abuse_data,
            "virustotal_data": vt_data,
            "otx_data": otx_data,
            "last_checked": datetime.now(timezone.utc).isoformat(),
            "source": "Enriched (AbuseIPDB, VT, OTX)"
        }
        
        if existing:
            for k, v in ti_data.items():
                setattr(existing, k, v)
            intel = existing
        else:
            intel = ThreatIntelligence(**ti_data)
            db.add(intel)
            
        await db.commit()
        await db.refresh(intel)
        return intel

threat_intel_service = ThreatIntelService()
