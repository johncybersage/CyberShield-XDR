from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel

from backend.models.report import ReportFormat, ReportStatus, ReportType


class ReportBase(BaseModel):
    title: str
    report_type: ReportType
    report_format: ReportFormat
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    status: Optional[ReportStatus] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    download_url: Optional[str] = None
    executive_summary: Optional[str] = None
    error_message: Optional[str] = None
    task_id: Optional[str] = None

class ReportResponse(ReportBase):
    id: UUID
    status: ReportStatus
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    download_url: Optional[str] = None
    executive_summary: Optional[str] = None
    error_message: Optional[str] = None
    task_id: Optional[str] = None
    generated_by_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
