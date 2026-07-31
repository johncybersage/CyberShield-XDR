import asyncio

from sqlalchemy import select

from backend.config.logging_config import get_logger
from backend.database.session import AsyncSessionLocal
from backend.models.network import NetworkAnalysis, NetworkAnalysisStatus
from backend.services.network.service import network_service
from backend.workers.celery_app import celery_app

logger = get_logger(__name__)

async def _analyze_pcap_async(analysis_id: str):
    async_session = AsyncSessionLocal()
    async with async_session() as db:
        result = await db.execute(select(NetworkAnalysis).where(NetworkAnalysis.id == analysis_id))
        analysis = result.scalar_one_or_none()
        
        if not analysis:
            logger.error(f"NetworkAnalysis {analysis_id} not found in database")
            return
            
        try:
            analysis.status = NetworkAnalysisStatus.RUNNING
            await db.commit()
            
            logger.info(f"Starting PCAP analysis for {analysis_id}")
            stats = network_service.analyze_pcap(analysis.storage_path)
            
            for k, v in stats.items():
                setattr(analysis, k, v)
                
            analysis.status = NetworkAnalysisStatus.COMPLETED
            await db.commit()
            logger.info(f"Analysis {analysis_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Analysis {analysis_id} failed: {e}")
            analysis.status = NetworkAnalysisStatus.FAILED
            analysis.error_message = str(e)
            await db.commit()

@celery_app.task(name="backend.workers.network_tasks.analyze_pcap")
def analyze_pcap(analysis_id: str):
    asyncio.run(_analyze_pcap_async(analysis_id))
