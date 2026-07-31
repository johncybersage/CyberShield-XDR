"""
CyberShield XDR — Users Endpoints
User management with RBAC enforcement.
- Admins: full CRUD on all users
- Analysts/Viewers: read/update own profile only
"""
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import AdminUser, CurrentUser
from backend.database.session import get_db
from backend.models.user import User, UserRole
from backend.schemas.auth import UserResponse

router = APIRouter()


# ---------------------------------------------------------------------------
# Request schemas (users-specific)
# ---------------------------------------------------------------------------

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class AdminUpdateUserRequest(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    full_name: Optional[str] = None
    department: Optional[str] = None


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    page_size: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=UserListResponse, summary="List all users (admin only)")
async def list_users(
    _: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = None,
    search: Optional[str] = None,
):
    """Paginated user list with optional role filter and search. Admin only."""
    query = select(User).where(User.deleted_at.is_(None))

    if role:
        query = query.where(User.role == role)
    if search:
        query = query.where(
            User.email.ilike(f"%{search}%") | User.username.ilike(f"%{search}%")
        )

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar_one()

    query = query.offset((page - 1) * page_size).limit(page_size).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = result.scalars().all()

    return UserListResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/me", response_model=UserResponse, summary="Get own profile")
async def get_own_profile(current_user: CurrentUser):
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse, summary="Update own profile")
async def update_own_profile(
    data: UpdateProfileRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update mutable profile fields. Role and active status cannot be self-modified."""
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    await db.flush()
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID (admin only)")
async def get_user(
    user_id: UUID,
    _: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse, summary="Update user (admin only)")
async def update_user(
    user_id: UUID,
    data: AdminUpdateUserRequest,
    _: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Admin can update role, active status, and profile fields."""
    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    await db.flush()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Soft-delete user (admin only)")
async def delete_user(
    user_id: UUID,
    current_admin: AdminUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Soft-delete a user. Cannot delete yourself."""
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )
    result = await db.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    from datetime import datetime, timezone
    user.deleted_at = datetime.now(timezone.utc)
    user.is_active = False
    await db.flush()
