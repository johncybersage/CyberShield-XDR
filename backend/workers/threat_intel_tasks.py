import asyncio

from backend.config.logging_config import get_logger
from backend.database.session import AsyncSessionLocal
from backend.services.threat_intel.service import threat_intel_service
from backend.workers.celery_app import celery_app

logger = get_logger(__name__)

async def _refresh_threat_feeds_async():
    logger.info("Starting daily threat feed refresh")
    # This would pull a list of IOCs and update them
    # For now, we'll just log
    logger.info("Daily threat feed refresh completed")

@celery_app.task(name="backend.workers.threat_intel_tasks.refresh_threat_feeds")
def refresh_threat_feeds():
    asyncio.run(_refresh_threat_feeds_async())

async def _enrich_ioc_async(ioc_value: str):
    async_session = AsyncSessionLocal()
    async with async_session() as db:
        await threat_intel_service.lookup_ioc(db, ioc_value)

@celery_app.task(name="backend.workers.threat_intel_tasks.enrich_ioc")
def enrich_ioc(ioc_value: str):
    asyncio.run(_enrich_ioc_async(ioc_value))
