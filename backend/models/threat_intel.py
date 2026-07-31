"""
CyberShield XDR — Threat Intelligence Model
Stores Indicators of Compromise (IOCs) from multiple threat feeds.
Supports IP, domain, URL, file hash, and email IOC types.
"""
import enum
from typing import Optional

from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.session import Base
from backend.models.mixins import TimestampMixin, UUIDMixin


class IOCType(str, enum.Enum):
    IP = "ip"
    DOMAIN = "domain"
    URL = "url"
    FILE_HASH_MD5 = "file_hash_md5"
    FILE_HASH_SHA256 = "file_hash_sha256"
    EMAIL = "email"
    CVE = "cve"


class ThreatCategory(str, enum.Enum):
    MALWARE = "malware"
    PHISHING = "phishing"
    BOTNET = "botnet"
    RANSOMWARE = "ransomware"
    APT = "apt"
    SPAM = "spam"
    SCANNER = "scanner"
    EXPLOIT = "exploit"
    UNKNOWN = "unknown"


class ThreatIntelligence(Base, UUIDMixin, TimestampMixin):
    """
    IOC record enriched from multiple threat intelligence sources.
    Deduplication is enforced via unique constraint on (ioc_type, value).
    """
    __tablename__ = "threat_intelligence"

    ioc_type: Mapped[IOCType] = mapped_column(String(20), nullable=False, index=True)
    value: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)

    # Reputation scores (0-100, higher = more malicious)
    abuse_confidence_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vt_malicious_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vt_total_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    otx_pulse_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Classification
    threat_category: Mapped[ThreatCategory] = mapped_column(
        String(20), default=ThreatCategory.UNKNOWN, nullable=False
    )
    threat_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_malicious: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Geo (for IPs)
    country_code: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    country_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    asn: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    isp: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # MITRE ATT&CK
    mitre_techniques: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Raw API responses
    abuseipdb_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    virustotal_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    otx_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Tags and description
    tags: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Freshness
    last_checked: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    expires_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    def __repr__(self) -> str:
        return f"<ThreatIntel [{self.ioc_type}] {self.value[:50]}>"
