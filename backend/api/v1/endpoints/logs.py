import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import AdminUser, CurrentUser
from backend.config.logging_config import get_logger
from backend.database.session import get_db
from backend.models.audit_log import AuditLog
from backend.schemas.audit_log import AuditLogCreate, AuditLogResponse

logger = get_logger(__name__)
router = APIRouter()

@router.get("", response_model=List[AuditLogResponse], summary="List audit logs (Admin only)")
async def list_logs(
    _: AdminUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    action: Optional[str] = None,
    user_id: Optional[uuid.UUID] = None
):
    query = select(AuditLog).order_by(AuditLog.created_at.desc())
    
    if action:
        query = query.where(AuditLog.action == action)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
        
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("", response_model=AuditLogResponse, summary="Append a manual client-side audit log")
async def create_log(
    request: Request,
    log_data: AuditLogCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    # Auto-fill context
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    audit_log = AuditLog(
        user_id=current_user.id,
        username=current_user.email,
        user_role=current_user.role.value,
        action=log_data.action,
        resource_type=log_data.resource_type,
        resource_id=log_data.resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        status=log_data.status,
        details=log_data.details,
        error_message=log_data.error_message
    )
    
    db.add(audit_log)
    await db.commit()
    await db.refresh(audit_log)
    
    return audit_log
