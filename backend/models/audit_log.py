"""
CyberShield XDR — Audit Log Model
Immutable audit trail for all security-relevant actions.
Never updated or deleted — append-only for compliance.
"""
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.session import Base
from backend.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from backend.models.user import User


class AuditLog(Base, UUIDMixin, TimestampMixin):
    """
    Append-only audit log. No update/delete operations should ever be performed.
    Captures who did what, from where, and the outcome.
    """
    __tablename__ = "audit_logs"

    # Actor
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    user_role: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Action
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # e.g., "user.login", "alert.update", "scan.create", "report.download"

    resource_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Context
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Outcome
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    # "success", "failure", "error"

    # Details
    details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} by {self.username} [{self.status}]>"
