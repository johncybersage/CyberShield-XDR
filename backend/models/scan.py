"""
CyberShield XDR — Scan Model
Tracks vulnerability scan jobs, their status, and structured findings.
Each scan links to an asset and stores CVE/CVSS data in JSONB.
"""
import enum
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.session import Base
from backend.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from backend.models.asset import Asset


class ScanType(str, enum.Enum):
    TCP = "tcp"
    UDP = "udp"
    FULL = "full"
    QUICK = "quick"
    STEALTH = "stealth"
    VERSION = "version"
    OS_DETECTION = "os_detection"


class ScanStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Scan(Base, UUIDMixin, TimestampMixin):
    """
    Vulnerability scan job with Nmap results and CVE mappings.
    JSONB findings store structured vulnerability data for flexible querying.
    """
    __tablename__ = "scans"

    scan_type: Mapped[ScanType] = mapped_column(String(20), nullable=False)
    status: Mapped[ScanStatus] = mapped_column(
        String(20), default=ScanStatus.PENDING, nullable=False, index=True
    )

    # Target
    target_ip: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    target_ports: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    # e.g., "22,80,443,8080-8090" or "1-65535"

    # Timing
    started_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    completed_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Results
    findings: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # Format: [{"port": 22, "service": "ssh", "version": "OpenSSH 8.9",
    #           "cves": [{"id": "CVE-2023-...", "cvss": 7.5, "description": "..."}]}]

    open_ports_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vulnerabilities_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    critical_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    high_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Risk
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    cvss_max: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Raw Nmap output
    raw_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    nmap_command: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Report
    report_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Celery task tracking
    task_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Foreign keys
    asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True, index=True
    )
    initiated_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    asset: Mapped[Optional["Asset"]] = relationship("Asset", back_populates="scans")

    def __repr__(self) -> str:
        return f"<Scan {self.scan_type} → {self.target_ip} [{self.status}]>"
