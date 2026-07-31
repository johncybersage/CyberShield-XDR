"""
CyberShield XDR — Asset Model
Represents a discovered network asset (host, server, IoT device, etc.).
Tracks OS, open ports, services, and risk posture over time.
"""
import enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.session import Base
from backend.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from backend.models.alert import Alert
    from backend.models.scan import Scan


class AssetType(str, enum.Enum):
    SERVER = "server"
    WORKSTATION = "workstation"
    NETWORK_DEVICE = "network_device"
    IOT = "iot"
    CLOUD = "cloud"
    UNKNOWN = "unknown"


class AssetStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class Asset(Base, UUIDMixin, TimestampMixin):
    """
    Network asset discovered via active or passive scanning.
    JSONB columns store flexible port/service data without schema migrations.
    """
    __tablename__ = "assets"

    # Identity
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False, index=True)  # IPv4/IPv6
    hostname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    mac_address: Mapped[Optional[str]] = mapped_column(String(17), nullable=True)
    vendor: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Classification
    asset_type: Mapped[AssetType] = mapped_column(SAEnum(AssetType), default=AssetType.UNKNOWN)
    status: Mapped[AssetStatus] = mapped_column(SAEnum(AssetStatus), default=AssetStatus.UNKNOWN)

    # OS Detection
    os_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    os_version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    os_family: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Network
    network_segment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Discovered data (flexible JSONB)
    open_ports: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # Format: [{"port": 80, "protocol": "tcp", "service": "http", "version": "nginx 1.24"}]

    running_services: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # Format: [{"name": "nginx", "version": "1.24", "port": 80}]

    # Risk
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    criticality: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)

    # Metadata
    tags: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Tracking
    first_seen: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_seen: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    scan_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    scans: Mapped[List["Scan"]] = relationship("Scan", back_populates="asset")
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="asset")

    def __repr__(self) -> str:
        return f"<Asset {self.ip_address} ({self.hostname or 'unknown'})>"
