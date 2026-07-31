"""
CyberShield XDR — Alerts Endpoints
Full alert lifecycle management with real-time WebSocket broadcast.
"""
from datetime import datetime, timezone
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import AnalystUser, CurrentUser
from backend.database.session import get_db
from backend.models.alert import Alert, AlertSeverity, AlertSource, AlertStatus
from backend.models.audit_log import AuditLog
from backend.schemas.alert import (
    AlertCreate,
    AlertListResponse,
    AlertResponse,
    AlertUpdate,
    TimelineEntry,
)
from backend.services.websocket_manager import manager

router = APIRouter()


@router.get("", response_model=AlertListResponse, summary="List alerts")
async def list_alerts(
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: Optional[AlertSeverity] = None,
    status: Optional[AlertStatus] = None,
    source: Optional[AlertSource] = None,
    search: Optional[str] = None,
    asset_id: Optional[UUID] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|severity|risk_score|status)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
):
    query = select(Alert)

    if severity:
        query = query.where(Alert.severity == severity)
    if status:
        query = query.where(Alert.status == status)
    if source:
        query = query.where(Alert.source == source)
    if asset_id:
        query = query.where(Alert.asset_id == asset_id)
    if search:
        query = query.where(
            or_(Alert.title.ilike(f"%{search}%"), Alert.src_ip.ilike(f"%{search}%"))
        )

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    sort_col = getattr(Alert, sort_by, Alert.created_at)
    query = query.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    alerts = result.scalars().all()

    return AlertListResponse(
        items=[AlertResponse.model_validate(a) for a in alerts],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=AlertResponse, status_code=201, summary="Create alert")
async def create_alert(
    data: AlertCreate,
    current_user: AnalystUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    now = datetime.now(timezone.utc)
    alert = Alert(
        **data.model_dump(),
        created_by_id=current_user.id,
        timeline=[{
            "timestamp": now.isoformat(),
            "action": "created",
            "user": current_user.username,
        }],
    )
    db.add(alert)
    await db.flush()
    await db.refresh(alert)

    db.add(AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action="alert.create",
        resource_type="alert",
        resource_id=str(alert.id),
        status="success",
    ))

    # Broadcast to all connected WebSocket clients
    await manager.broadcast({
        "type": "alert.new",
        "data": {
            "id": str(alert.id),
            "title": alert.title,
            "severity": alert.severity,
            "source": alert.source,
            "created_at": now.isoformat(),
        },
    })

    return AlertResponse.model_validate(alert)


@router.get("/{alert_id}", response_model=AlertResponse, summary="Get alert by ID")
async def get_alert(
    alert_id: UUID,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse.model_validate(alert)


@router.patch("/{alert_id}", response_model=AlertResponse, summary="Update alert")
async def update_alert(
    alert_id: UUID,
    data: AlertUpdate,
    current_user: AnalystUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    now = datetime.now(timezone.utc)
    updates = data.model_dump(exclude_none=True)

    for field, value in updates.items():
        setattr(alert, field, value)

    # Append to timeline
    timeline = list(alert.timeline or [])
    timeline.append({
        "timestamp": now.isoformat(),
        "action": "updated",
        "user": current_user.username,
        "changes": list(updates.keys()),
    })
    alert.timeline = timeline

    if data.status == AlertStatus.RESOLVED:
        alert.resolved_at = now.isoformat()

    await db.flush()
    await db.refresh(alert)

    db.add(AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action="alert.update",
        resource_type="alert",
        resource_id=str(alert_id),
        status="success",
        details=updates,
    ))

    await manager.broadcast({
        "type": "alert.updated",
        "data": {"id": str(alert_id), "status": alert.status, "severity": alert.severity},
    })

    return AlertResponse.model_validate(alert)


@router.post("/{alert_id}/timeline", response_model=AlertResponse, summary="Add timeline note")
async def add_timeline_note(
    alert_id: UUID,
    entry: TimelineEntry,
    current_user: AnalystUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    timeline = list(alert.timeline or [])
    timeline.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": entry.action,
        "note": entry.note,
        "user": current_user.username,
    })
    alert.timeline = timeline
    await db.flush()
    await db.refresh(alert)
    return AlertResponse.model_validate(alert)


@router.delete("/{alert_id}", status_code=204, summary="Delete alert")
async def delete_alert(
    alert_id: UUID,
    current_user: AnalystUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    await db.delete(alert)
    db.add(AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action="alert.delete",
        resource_type="alert",
        resource_id=str(alert_id),
        status="success",
    ))
