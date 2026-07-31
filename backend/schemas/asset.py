"""
CyberShield XDR — Asset Schemas
"""
from typing import Any, List, Optional

from pydantic import BaseModel, field_validator

from backend.models.asset import AssetStatus, AssetType


class AssetCreate(BaseModel):
    ip_address: str
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    asset_type: AssetType = AssetType.UNKNOWN
    criticality: str = "medium"
    owner: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[dict] = None

    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        import ipaddress
        try:
            ipaddress.ip_address(v.strip())
        except ValueError:
            raise ValueError(f"Invalid IP address: {v}")
        return v.strip()


class AssetUpdate(BaseModel):
    hostname: Optional[str] = None
    asset_type: Optional[AssetType] = None
    criticality: Optional[str] = None
    owner: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[dict] = None
    status: Optional[AssetStatus] = None


class AssetResponse(BaseModel):
    id: str
    ip_address: str
    hostname: Optional[str]
    mac_address: Optional[str]
    vendor: Optional[str]
    asset_type: str
    status: str
    os_name: Optional[str]
    os_version: Optional[str]
    open_ports: Optional[Any]
    running_services: Optional[Any]
    risk_score: float
    criticality: str
    owner: Optional[str]
    location: Optional[str]
    tags: Optional[Any]
    notes: Optional[str]
    first_seen: Optional[str]
    last_seen: Optional[str]
    scan_count: int
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}

    @field_validator("id", "created_at", "updated_at", mode="before")
    @classmethod
    def stringify(cls, v):
        return str(v)


class AssetListResponse(BaseModel):
    items: List[AssetResponse]
    total: int
    page: int
    page_size: int
