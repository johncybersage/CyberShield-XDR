"""
CyberShield XDR — Scan Schemas
"""
from typing import Any, List, Optional

from pydantic import BaseModel, field_validator

from backend.models.scan import ScanType


class ScanCreate(BaseModel):
    target_ip: str
    scan_type: ScanType = ScanType.TCP
    target_ports: Optional[str] = None  # e.g. "22,80,443" or "1-1024"

    @field_validator("target_ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        import ipaddress
        try:
            ipaddress.ip_address(v.strip())
        except ValueError:
            # Allow CIDR ranges for network scans
            try:
                ipaddress.ip_network(v.strip(), strict=False)
            except ValueError:
                raise ValueError(f"Invalid IP address or CIDR: {v}")
        return v.strip()


class ScanResponse(BaseModel):
    id: str
    scan_type: str
    status: str
    target_ip: str
    target_ports: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    duration_seconds: Optional[int]
    findings: Optional[Any]
    open_ports_count: int
    vulnerabilities_count: int
    critical_count: int
    high_count: int
    risk_score: float
    cvss_max: float
    nmap_command: Optional[str]
    report_path: Optional[str]
    error_message: Optional[str]
    task_id: Optional[str]
    asset_id: Optional[str]
    created_at: str

    model_config = {"from_attributes": True}

    @field_validator("id", "created_at", mode="before")
    @classmethod
    def stringify(cls, v):
        return str(v)

    @field_validator("asset_id", mode="before")
    @classmethod
    def stringify_optional(cls, v):
        return str(v) if v else None


class ScanListResponse(BaseModel):
    items: List[ScanResponse]
    total: int
    page: int
    page_size: int
