"""
CyberShield XDR — User Model
Supports RBAC with three roles: admin, soc_analyst, viewer.
Includes account lockout, MFA readiness, and soft delete.
"""
import enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.session import Base
from backend.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from backend.models.alert import Alert
    from backend.models.audit_log import AuditLog


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SOC_ANALYST = "soc_analyst"
    VIEWER = "viewer"


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Platform user with role-based access control.

    Security considerations:
    - Password stored as bcrypt hash only
    - Failed login attempts tracked for lockout
    - Refresh tokens stored hashed
    """
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.VIEWER, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Account lockout
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Password reset
    reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reset_token_expires: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Profile
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Notification preferences (JSON stored as text)
    notification_prefs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="assigned_to", foreign_keys="Alert.assigned_to_id")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"
