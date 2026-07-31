import enum
import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.session import Base
from backend.models.mixins import TimestampMixin, UUIDMixin


class NetworkAnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class NetworkAnalysis(Base, UUIDMixin, TimestampMixin):
    """
    Network PCAP analysis result.
    """
    __tablename__ = "network_analyses"

    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    
    status: Mapped[NetworkAnalysisStatus] = mapped_column(
        String(20), default=NetworkAnalysisStatus.PENDING, nullable=False
    )
    
    # Analysis Results
    total_packets: Mapped[int] = mapped_column(Integer, default=0)
    tcp_count: Mapped[int] = mapped_column(Integer, default=0)
    udp_count: Mapped[int] = mapped_column(Integer, default=0)
    icmp_count: Mapped[int] = mapped_column(Integer, default=0)
    other_count: Mapped[int] = mapped_column(Integer, default=0)
    
    anomalies_found: Mapped[int] = mapped_column(Integer, default=0)
    anomaly_details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # [{"type": "ping_flood", "description": "...", "severity": "high"}]

    error_message: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)

    analyzed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    def __repr__(self) -> str:
        return f"<NetworkAnalysis {self.filename} [{self.status}]>"
