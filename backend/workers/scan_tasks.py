"""
CyberShield XDR — Scan Tasks
Celery background workers for network and vulnerability scanning.
"""
import asyncio
from uuid import UUID

from backend.config.logging_config import get_logger
from backend.database.session import AsyncSessionLocal
from backend.services.scanner.service import ScannerService
from backend.workers.celery_app import celery_app

logger = get_logger(__name__)

async def _run_scan_async(scan_id: str):
    async_session = AsyncSessionLocal()
    async with async_session() as db:
        scanner = ScannerService(db)
        await scanner.run_scan(UUID(scan_id))


@celery_app.task(name="scans.run_scan", queue="scans")
def run_scan_task(scan_id: str):
    """
    Celery task to run a vulnerability scan asynchronously.
    """
    logger.info(f"Starting scan task for scan_id: {scan_id}")
    # Run the async service method inside an event loop
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(_run_scan_async(scan_id))
    logger.info(f"Completed scan task for scan_id: {scan_id}")

@celery_app.task(name="scans.cleanup_old_scans", queue="scans")
def cleanup_old_scans():
    """
    Periodic task to clean up old scans.
    """
    logger.info("Cleaning up old scans...")
    # Mock implementation
    pass

