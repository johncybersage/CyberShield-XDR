"""
CyberShield XDR — Notification Model
Tracks notification delivery across channels: email, Slack, Discord, browser, webhook.
"""
import enum
import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.session import Base
from backend.models.mixins import TimestampMixin, UUIDMixin


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SLACK = "slack"
    DISCORD = "discord"
    BROWSER = "browser"
    WEBHOOK = "webhook"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"


class Notification(Base, UUIDMixin, TimestampMixin):
    """Notification record with delivery status tracking per channel."""
    __tablename__ = "notifications"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[NotificationStatus] = mapped_column(
        String(20), default=NotificationStatus.PENDING, nullable=False, index=True
    )

    # Reference to the triggering entity
    ref_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ref_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Delivery metadata
    sent_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    read_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(default=0, nullable=False)

    # Payload (channel-specific data)
    payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Foreign keys
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )

    def __repr__(self) -> str:
        return f"<Notification [{self.channel}] {self.title[:50]} [{self.status}]>"
