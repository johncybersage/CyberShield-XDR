import csv
import os
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.logging_config import get_logger
from backend.models.alert import Alert
from backend.models.asset import Asset
from backend.models.report import Report, ReportType
from backend.models.threat_intel import ThreatIntelligence

logger = get_logger(__name__)

class ReportGeneratorService:
    def __init__(self):
        self.upload_dir = os.path.join(os.getcwd(), "uploads", "reports")
        os.makedirs(self.upload_dir, exist_ok=True)

    async def generate_csv_report(self, report: Report, db: AsyncSession) -> Dict[str, Any]:
        """
        Generates a CSV report based on the ReportType and saves it to disk.
        """
        logger.info(f"Generating CSV for Report: {report.id} ({report.report_type})")
        
        file_name = f"report_{report.id}.csv"
        file_path = os.path.join(self.upload_dir, file_name)
        
        # Determine headers and data fetching strategy based on report type
        headers = []
        data_rows = []

        if report.report_type == ReportType.INCIDENT:
            headers = ["ID", "Title", "Severity", "Status", "Created At"]
            # Fetch alerts (Incidents)
            result = await db.execute(select(Alert).order_by(Alert.created_at.desc()).limit(1000))
            alerts = result.scalars().all()
            for a in alerts:
                data_rows.append([str(a.id), a.title, a.severity.value, a.status.value, str(a.created_at)])
                
        elif report.report_type == ReportType.THREAT_INTEL:
            headers = ["ID", "Indicator", "Type", "Confidence", "Source", "Created At"]
            result = await db.execute(select(ThreatIntelligence).order_by(ThreatIntelligence.created_at.desc()).limit(1000))
            intel = result.scalars().all()
            for i in intel:
                data_rows.append([str(i.id), i.indicator, i.ioc_type.value, str(i.confidence_score), i.source, str(i.created_at)])
                
        elif report.report_type == ReportType.ASSET_INVENTORY:
            headers = ["ID", "Hostname", "IP Address", "OS", "Risk Score", "Status"]
            result = await db.execute(select(Asset).order_by(Asset.created_at.desc()).limit(1000))
            assets = result.scalars().all()
            for a in assets:
                data_rows.append([str(a.id), a.hostname, a.ip_address, a.os_type, str(a.risk_score), a.status.value])
                
        else:
            # Fallback for empty or unsupported types currently
            headers = ["Message"]
            data_rows = [["Report type not fully implemented in MVP, but file generated successfully."]]

        # Write to CSV
        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data_rows)
            
        file_size = os.path.getsize(file_path)
        
        return {
            "file_path": file_path,
            "file_size": file_size,
            "download_url": f"/api/v1/reports/{report.id}/download"
        }

report_service = ReportGeneratorService()
