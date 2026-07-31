import os
import uuid
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import AnalystUser, CurrentUser
from backend.config.logging_config import get_logger
from backend.database.session import get_db
from backend.models.phishing import PhishingAnalysis, PhishingVerdict
from backend.schemas.phishing import PhishingAnalysisResponse
from backend.services.phishing.service import phishing_service

logger = get_logger(__name__)
router = APIRouter()
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "phishing")

@router.get("", response_model=List[PhishingAnalysisResponse], summary="List phishing analyses")
async def list_analyses(
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    verdict: Optional[PhishingVerdict] = None
):
    query = select(PhishingAnalysis)
    if verdict:
        query = query.where(PhishingAnalysis.verdict == verdict)
        
    query = query.order_by(PhishingAnalysis.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/analyze", response_model=PhishingAnalysisResponse, summary="Analyze an email")
async def analyze_email(
    current_user: AnalystUser,
    db: AsyncSession = Depends(get_db),
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None)
):
    if not file and not raw_text:
        raise HTTPException(status_code=400, detail="Must provide either an EML file or raw_text")

    raw_bytes = b""
    if file:
        raw_bytes = await file.read()
    else:
        raw_bytes = raw_text.encode('utf-8')

    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Empty payload")

    try:
        analysis_data = phishing_service.analyze_email(raw_bytes)
    except Exception as e:
        logger.error(f"Phishing analysis failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    # Save EML for evidence
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
    email_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.eml")
    with open(email_path, "wb") as f:
        f.write(raw_bytes)
        
    analysis_data["email_path"] = email_path
    analysis_data["analyzed_by_id"] = current_user.id

    analysis = PhishingAnalysis(**analysis_data)
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    
    return analysis

@router.get("/{analysis_id}", response_model=PhishingAnalysisResponse, summary="Get phishing analysis details")
async def get_analysis(
    analysis_id: uuid.UUID,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(PhishingAnalysis).where(PhishingAnalysis.id == analysis_id))
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis
