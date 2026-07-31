import asyncio

from sqlalchemy import select

from backend.config.logging_config import get_logger
from backend.database.session import AsyncSessionLocal
from backend.models.report import Report, ReportFormat, ReportStatus
from backend.services.reports.service import report_service
from backend.workers.celery_app import celery_app

logger = get_logger(__name__)

async def _generate_report_async(report_id: str):
    async_session = AsyncSessionLocal()
    async with async_session() as db:
        result = await db.execute(select(Report).where(Report.id == report_id))
        report = result.scalar_one_or_none()
        
        if not report:
            logger.error(f"Report {report_id} not found in database")
            return
            
        try:
            report.status = ReportStatus.GENERATING
            await db.commit()
            
            # Currently only CSV is supported for MVP robustness
            if report.report_format == ReportFormat.CSV:
                result_data = await report_service.generate_csv_report(report, db)
                
                report.file_path = result_data["file_path"]
                report.file_size = result_data["file_size"]
                report.download_url = result_data["download_url"]
            else:
                raise ValueError("Only CSV format is currently supported.")
                
            report.status = ReportStatus.COMPLETED
            await db.commit()
            logger.info(f"Report {report_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Report {report_id} failed: {e}")
            report.status = ReportStatus.FAILED
            report.error_message = str(e)
            await db.commit()

@celery_app.task(name="backend.workers.report_tasks.generate_report")
def generate_report(report_id: str):
    asyncio.run(_generate_report_async(report_id))
