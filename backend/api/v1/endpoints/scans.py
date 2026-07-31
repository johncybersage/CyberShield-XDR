"""
CyberShield XDR — Scans Endpoints
Trigger vulnerability scans and retrieve results.
"""
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import AnalystUser, CurrentUser
from backend.database.session import get_db
from backend.models.audit_log import AuditLog
from backend.models.scan import Scan, ScanStatus
from backend.schemas.scan import ScanCreate, ScanListResponse, ScanResponse
from backend.workers.scan_tasks import run_scan_task

router = APIRouter()


@router.post("", response_model=ScanResponse, status_code=status.HTTP_201_CREATED, summary="Trigger scan")
async def trigger_scan(
    data: ScanCreate,
    current_user: AnalystUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    scan = Scan(
        target_ip=data.target_ip,
        scan_type=data.scan_type.value,
        target_ports=data.target_ports,
        status=ScanStatus.PENDING,
    )
    db.add(scan)
    await db.flush()

    # Trigger Celery task
    task = run_scan_task.apply_async(args=[str(scan.id)])
    scan.task_id = task.id
    await db.flush()
    await db.refresh(scan)

    db.add(AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action="scan.trigger",
        resource_type="scan",
        resource_id=str(scan.id),
        status="success",
    ))

    return ScanResponse.model_validate(scan)


@router.get("", response_model=ScanListResponse, summary="List scans")
async def list_scans(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[ScanStatus] = None,
    target_ip: Optional[str] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|risk_score)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
):
    query = select(Scan)

    if status:
        query = query.where(Scan.status == status)
    if target_ip:
        query = query.where(Scan.target_ip.ilike(f"%{target_ip}%"))

    # Total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    # Sorting
    sort_col = getattr(Scan, sort_by, Scan.created_at)
    query = query.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    scans = result.scalars().all()

    return ScanListResponse(
        items=[ScanResponse.model_validate(s) for s in scans],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{scan_id}", response_model=ScanResponse, summary="Get scan by ID")
async def get_scan(
    scan_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return ScanResponse.model_validate(scan)


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete scan")
async def delete_scan(
    scan_id: UUID,
    current_user: AnalystUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    await db.delete(scan)
    db.add(AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action="scan.delete",
        resource_type="scan",
        resource_id=str(scan_id),
        status="success",
    ))
