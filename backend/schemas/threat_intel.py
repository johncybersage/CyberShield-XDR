from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel

from backend.models.threat_intel import IOCType, ThreatCategory


class ThreatIntelligenceBase(BaseModel):
    ioc_type: IOCType
    value: str

class ThreatIntelligenceCreate(ThreatIntelligenceBase):
    pass

class ThreatIntelligenceUpdate(BaseModel):
    abuse_confidence_score: Optional[int] = None
    vt_malicious_count: Optional[int] = None
    vt_total_count: Optional[int] = None
    otx_pulse_count: Optional[int] = None
    threat_category: Optional[ThreatCategory] = None
    threat_score: Optional[float] = None
    is_malicious: Optional[bool] = None
    country_code: Optional[str] = None
    country_name: Optional[str] = None
    asn: Optional[str] = None
    isp: Optional[str] = None
    mitre_techniques: Optional[Dict[str, Any]] = None
    abuseipdb_data: Optional[Dict[str, Any]] = None
    virustotal_data: Optional[Dict[str, Any]] = None
    otx_data: Optional[Dict[str, Any]] = None
    tags: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    last_checked: Optional[str] = None
    expires_at: Optional[str] = None
    source: Optional[str] = None

class ThreatIntelligenceResponse(ThreatIntelligenceBase):
    id: UUID
    abuse_confidence_score: int
    vt_malicious_count: int
    vt_total_count: int
    otx_pulse_count: int
    threat_category: ThreatCategory
    threat_score: float
    is_malicious: bool
    country_code: Optional[str] = None
    country_name: Optional[str] = None
    asn: Optional[str] = None
    isp: Optional[str] = None
    mitre_techniques: Optional[Dict[str, Any]] = None
    abuseipdb_data: Optional[Dict[str, Any]] = None
    virustotal_data: Optional[Dict[str, Any]] = None
    otx_data: Optional[Dict[str, Any]] = None
    tags: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    last_checked: Optional[str] = None
    expires_at: Optional[str] = None
    source: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
