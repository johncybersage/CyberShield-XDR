"""
CyberShield XDR — Phishing Detection Model
Stores email analysis results with ML-based phishing confidence scoring.
Analyzes headers, URLs, attachments, and sender reputation.
"""
import enum
import uuid
from typing import Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.session import Base
from backend.models.mixins import TimestampMixin, UUIDMixin


class PhishingVerdict(str, enum.Enum):
    CLEAN = "clean"
    SUSPICIOUS = "suspicious"
    PHISHING = "phishing"
    SPAM = "spam"
    UNKNOWN = "unknown"


class PhishingAnalysis(Base, UUIDMixin, TimestampMixin):
    """
    Phishing email analysis result.
    Combines ML model output with rule-based checks (SPF/DKIM/DMARC).
    """
    __tablename__ = "phishing_analyses"

    # Email metadata
    subject: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    sender: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, index=True)
    sender_domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    recipient: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    message_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Verdict
    verdict: Mapped[PhishingVerdict] = mapped_column(
        String(20), default=PhishingVerdict.UNKNOWN, nullable=False, index=True
    )
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    # 0.0 = definitely clean, 1.0 = definitely phishing

    # Authentication checks
    spf_pass: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dkim_pass: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    dmarc_pass: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # URL analysis
    urls_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    malicious_urls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    url_details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # Format: [{"url": "...", "is_malicious": true, "vt_score": 5, "features": {...}}]

    # Attachment analysis
    attachments_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    malicious_attachments: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    attachment_details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # ML features
    ml_features: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    ml_model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Header analysis
    header_anomalies: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # Format: [{"type": "reply_to_mismatch", "detail": "..."}]

    # Raw data
    raw_headers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # AI summary
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Storage
    email_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Foreign keys
    analyzed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    def __repr__(self) -> str:
        return f"<PhishingAnalysis {self.sender} [{self.verdict}] {self.confidence_score:.2f}>"
