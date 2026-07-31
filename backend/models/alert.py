"""
CyberShield XDR — Alert Model
Central alert entity linking detections from all modules (IDS, scanner, threat intel, etc.).
Supports full incident lifecycle: triage → investigation → resolution.
"""
import enum
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.session import Base
from backend.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from backend.models.asset import Asset
    from backend.models.user import User


class AlertSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    SUPPRESSED = "suppressed"


class AlertSource(str, enum.Enum):
    IDS = "ids"
    VULNERABILITY_SCANNER = "vulnerability_scanner"
    THREAT_INTEL = "threat_intel"
    MALWARE_ANALYSIS = "malware_analysis"
    PHISHING_DETECTOR = "phishing_detector"
    MANUAL = "manual"
    SYSTEM = "system"


class Alert(Base, UUIDMixin, TimestampMixin):
    """
    Security alert with full incident management lifecycle.
    MITRE ATT&CK mapping stored for threat context.
    """
    __tablename__ = "alerts"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(
        String(20), default=AlertSeverity.MEDIUM, nullable=False, index=True
    )
    status: Mapped[AlertStatus] = mapped_column(
        String(20), default=AlertStatus.OPEN, nullable=False, index=True
    )
    source: Mapped[AlertSource] = mapped_column(String(30), nullable=False, index=True)

    # Source reference (e.g., scan ID, packet capture ID)
    source_ref_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # MITRE ATT&CK
    mitre_tactic: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    mitre_technique: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    mitre_technique_id: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Network context
    src_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True, index=True)
    dst_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    src_port: Mapped[Optional[int]] = mapped_column(nullable=True)
    dst_port: Mapped[Optional[int]] = mapped_column(nullable=True)
    protocol: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Risk
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # AI-generated content
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_recommendations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Incident management
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timeline: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # Format: [{"timestamp": "...", "action": "...", "user": "...", "note": "..."}]

    attachments: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    is_false_positive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Foreign keys
    asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    asset: Mapped[Optional["Asset"]] = relationship("Asset", back_populates="alerts")
    assigned_to: Mapped[Optional["User"]] = relationship(
        "User", back_populates="alerts", foreign_keys=[assigned_to_id]
    )

    def __repr__(self) -> str:
        return f"<Alert [{self.severity}] {self.title[:50]}>"
