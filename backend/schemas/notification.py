from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel

from backend.models.notification import NotificationChannel, NotificationStatus


class NotificationBase(BaseModel):
    title: str
    message: str
    channel: NotificationChannel
    ref_type: Optional[str] = None
    ref_id: Optional[str] = None

class NotificationCreate(NotificationBase):
    user_id: Optional[UUID] = None
    payload: Optional[Dict[str, Any]] = None

class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None
    sent_at: Optional[str] = None
    read_at: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: Optional[int] = None
    is_read: Optional[bool] = None

class NotificationResponse(NotificationBase):
    id: UUID
    status: NotificationStatus
    sent_at: Optional[str] = None
    read_at: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int
    payload: Optional[Dict[str, Any]] = None
    is_read: bool
    user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
