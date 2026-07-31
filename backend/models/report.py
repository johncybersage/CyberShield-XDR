"""
CyberShield XDR — Report Model
Tracks generated reports (PDF, CSV, Excel) with metadata and download links.
"""
import enum
import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.session import Base
from backend.models.mixins import TimestampMixin, UUIDMixin


class ReportType(str, enum.Enum):
    EXECUTIVE_SUMMARY = "executive_summary"
    VULNERABILITY = "vulnerability"
    INCIDENT = "incident"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    THREAT_INTEL = "threat_intel"
    MALWARE = "malware"
    PHISHING = "phishing"
    ASSET_INVENTORY = "asset_inventory"


class ReportFormat(str, enum.Enum):
    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class Report(Base, UUIDMixin, TimestampMixin):
    """Generated report with metadata, storage path, and generation parameters."""
    __tablename__ = "reports"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    report_type: Mapped[ReportType] = mapped_column(String(30), nullable=False, index=True)
    report_format: Mapped[ReportFormat] = mapped_column(String(10), nullable=False)
    status: Mapped[ReportStatus] = mapped_column(
        String(20), default=ReportStatus.PENDING, nullable=False
    )

    # Date range for the report
    period_start: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    period_end: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Generation parameters
    parameters: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Output
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    download_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # AI-generated content
    executive_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    task_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Foreign keys
    generated_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    def __repr__(self) -> str:
        return f"<Report {self.report_type} [{self.status}]>"
