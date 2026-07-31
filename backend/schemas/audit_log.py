from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class AuditLogBase(BaseModel):
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    status: str
    details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    user_id: Optional[UUID] = None
    username: Optional[str] = None
    user_role: Optional[str] = None

class AuditLogResponse(AuditLogBase):
    id: UUID
    user_id: Optional[UUID] = None
    username: Optional[str] = None
    user_role: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
