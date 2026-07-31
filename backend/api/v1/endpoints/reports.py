import os
import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import AnalystUser, CurrentUser
from backend.config.logging_config import get_logger
from backend.database.session import get_db
from backend.models.report import Report, ReportStatus
from backend.schemas.report import ReportCreate, ReportResponse
from backend.workers.report_tasks import generate_report

logger = get_logger(__name__)
router = APIRouter()

@router.get("", response_model=List[ReportResponse], summary="List generated reports")
async def list_reports(
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    query = select(Report).order_by(Report.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("", response_model=ReportResponse, summary="Request a new report")
async def create_report(
    request: ReportCreate,
    current_user: AnalystUser,
    db: AsyncSession = Depends(get_db)
):
    report = Report(
        title=request.title,
        report_type=request.report_type,
        report_format=request.report_format,
        period_start=request.period_start,
        period_end=request.period_end,
        parameters=request.parameters,
        generated_by_id=current_user.id
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    # Trigger Celery Task
    generate_report.delay(str(report.id))
    
    return report

@router.get("/{report_id}/download", summary="Download a generated report")
async def download_report(
    report_id: uuid.UUID,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    if report.status != ReportStatus.COMPLETED or not report.file_path:
        raise HTTPException(status_code=400, detail="Report is not ready for download")
        
    if not os.path.exists(report.file_path):
        raise HTTPException(status_code=500, detail="Report file missing from disk")
        
    return FileResponse(
        path=report.file_path, 
        filename=os.path.basename(report.file_path),
        media_type="text/csv"
    )
