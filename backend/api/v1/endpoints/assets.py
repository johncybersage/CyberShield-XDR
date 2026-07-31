"""
CyberShield XDR — Assets Endpoints
Full CRUD for network assets with filtering, search, and pagination.
"""
from datetime import datetime, timezone
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import AnalystUser, CurrentUser
from backend.database.session import get_db
from backend.models.asset import Asset, AssetStatus, AssetType
from backend.models.audit_log import AuditLog
from backend.schemas.asset import (
    AssetCreate,
    AssetListResponse,
    AssetResponse,
    AssetUpdate,
)

router = APIRouter()


@router.get("", response_model=AssetListResponse, summary="List assets")
async def list_assets(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by IP, hostname, or owner"),
    asset_type: Optional[AssetType] = None,
    status: Optional[AssetStatus] = None,
    criticality: Optional[str] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|risk_score|ip_address|hostname)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
):
    query = select(Asset)

    if search:
        query = query.where(
            or_(
                Asset.ip_address.ilike(f"%{search}%"),
                Asset.hostname.ilike(f"%{search}%"),
                Asset.owner.ilike(f"%{search}%"),
            )
        )
    if asset_type:
        query = query.where(Asset.asset_type == asset_type)
    if status:
        query = query.where(Asset.status == status)
    if criticality:
        query = query.where(Asset.criticality == criticality)

    # Total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    # Sorting
    sort_col = getattr(Asset, sort_by, Asset.created_at)
    query = query.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    assets = result.scalars().all()

    return AssetListResponse(
        items=[AssetResponse.model_validate(a) for a in assets],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED, summary="Create asset")
async def create_asset(
    data: AssetCreate,
    current_user: AnalystUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Check for duplicate IP
    existing = await db.execute(select(Asset).where(Asset.ip_address == data.ip_address))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Asset with IP {data.ip_address} already exists")

    now_str = datetime.now(timezone.utc).isoformat()
    asset = Asset(
        **data.model_dump(),
        first_seen=now_str,
        last_seen=now_str,
    )
    db.add(asset)
    await db.flush()
    await db.refresh(asset)

    db.add(AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action="asset.create",
        resource_type="asset",
        resource_id=str(asset.id),
        status="success",
    ))

    return AssetResponse.model_validate(asset)


@router.get("/{asset_id}", response_model=AssetResponse, summary="Get asset by ID")
async def get_asset(
    asset_id: UUID,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AssetResponse.model_validate(asset)


@router.patch("/{asset_id}", response_model=AssetResponse, summary="Update asset")
async def update_asset(
    asset_id: UUID,
    data: AssetUpdate,
    current_user: AnalystUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(asset, field, value)
    await db.flush()
    await db.refresh(asset)

    db.add(AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action="asset.update",
        resource_type="asset",
        resource_id=str(asset_id),
        status="success",
    ))
    return AssetResponse.model_validate(asset)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete asset")
async def delete_asset(
    asset_id: UUID,
    current_user: AnalystUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    await db.delete(asset)
    db.add(AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        user_role=current_user.role.value,
        action="asset.delete",
        resource_type="asset",
        resource_id=str(asset_id),
        status="success",
    ))
