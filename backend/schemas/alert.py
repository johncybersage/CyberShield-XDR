"""
CyberShield XDR — Alert Schemas
"""
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from backend.models.alert import AlertSeverity, AlertSource, AlertStatus


class AlertCreate(BaseModel):
    title: str
    description: str
    severity: AlertSeverity = AlertSeverity.MEDIUM
    source: AlertSource
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    protocol: Optional[str] = None
    mitre_tactic: Optional[str] = None
    mitre_technique: Optional[str] = None
    mitre_technique_id: Optional[str] = None
    asset_id: Optional[UUID] = None
    risk_score: float = 0.0
    confidence: float = 1.0
    raw_data: Optional[dict] = None
    tags: Optional[dict] = None


class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    severity: Optional[AlertSeverity] = None
    assigned_to_id: Optional[UUID] = None
    notes: Optional[str] = None
    ai_summary: Optional[str] = None
    is_false_positive: Optional[bool] = None


class TimelineEntry(BaseModel):
    action: str
    note: Optional[str] = None


class AlertResponse(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    status: str
    source: str
    src_ip: Optional[str]
    dst_ip: Optional[str]
    src_port: Optional[int]
    dst_port: Optional[int]
    protocol: Optional[str]
    mitre_tactic: Optional[str]
    mitre_technique: Optional[str]
    mitre_technique_id: Optional[str]
    risk_score: float
    confidence: float
    ai_summary: Optional[str]
    ai_recommendations: Optional[str]
    notes: Optional[str]
    timeline: Optional[Any]
    tags: Optional[Any]
    is_false_positive: bool
    asset_id: Optional[str]
    assigned_to_id: Optional[str]
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}

    @field_validator("id", "created_at", "updated_at", mode="before")
    @classmethod
    def stringify(cls, v):
        return str(v)

    @field_validator("asset_id", "assigned_to_id", mode="before")
    @classmethod
    def stringify_optional(cls, v):
        return str(v) if v else None


class AlertListResponse(BaseModel):
    items: List[AlertResponse]
    total: int
    page: int
    page_size: int
