import hashlib
import os
import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import AnalystUser, CurrentUser
from backend.config.logging_config import get_logger
from backend.database.session import get_db
from backend.models.network import NetworkAnalysis
from backend.schemas.network import NetworkAnalysisResponse
from backend.workers.network_tasks import analyze_pcap

logger = get_logger(__name__)
router = APIRouter()
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "network")

@router.get("", response_model=List[NetworkAnalysisResponse], summary="List network analyses")
async def list_analyses(
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    query = select(NetworkAnalysis).order_by(NetworkAnalysis.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/upload", response_model=NetworkAnalysisResponse, summary="Upload a PCAP file for analysis")
async def upload_pcap(
    current_user: AnalystUser,
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...)
):
    # Enforce file size limits for the MVP so scapy doesn't blow up memory
    # 50MB max
    MAX_SIZE = 50 * 1024 * 1024
    
    raw_bytes = await file.read()
    if len(raw_bytes) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 50MB for MVP.")

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
    # Hash filename to prevent traversal and execution
    file_hash = hashlib.sha256(raw_bytes).hexdigest()
    storage_path = os.path.join(UPLOAD_DIR, f"{file_hash}.pcap")
    
    with open(storage_path, "wb") as f:
        f.write(raw_bytes)

    analysis = NetworkAnalysis(
        filename=file.filename,
        storage_path=storage_path,
        file_size=len(raw_bytes),
        analyzed_by_id=current_user.id
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    
    # Trigger Celery task
    analyze_pcap.delay(str(analysis.id))
    
    return analysis

@router.get("/{analysis_id}", response_model=NetworkAnalysisResponse, summary="Get network analysis details")
async def get_analysis(
    analysis_id: uuid.UUID,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(NetworkAnalysis).where(NetworkAnalysis.id == analysis_id))
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis
