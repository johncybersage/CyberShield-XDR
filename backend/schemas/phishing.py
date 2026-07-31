from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel

from backend.models.phishing import PhishingVerdict


class PhishingAnalysisBase(BaseModel):
    subject: Optional[str] = None
    sender: Optional[str] = None
    sender_domain: Optional[str] = None
    recipient: Optional[str] = None
    message_id: Optional[str] = None

class PhishingAnalysisCreate(PhishingAnalysisBase):
    pass

class PhishingAnalysisUpdate(BaseModel):
    verdict: Optional[PhishingVerdict] = None
    confidence_score: Optional[float] = None
    spf_pass: Optional[bool] = None
    dkim_pass: Optional[bool] = None
    dmarc_pass: Optional[bool] = None
    urls_found: Optional[int] = None
    malicious_urls: Optional[int] = None
    url_details: Optional[Dict[str, Any]] = None
    attachments_count: Optional[int] = None
    malicious_attachments: Optional[int] = None
    attachment_details: Optional[Dict[str, Any]] = None
    ml_features: Optional[Dict[str, Any]] = None
    ml_model_version: Optional[str] = None
    header_anomalies: Optional[Dict[str, Any]] = None
    raw_headers: Optional[str] = None
    body_text: Optional[str] = None
    ai_summary: Optional[str] = None
    email_path: Optional[str] = None

class PhishingAnalysisResponse(PhishingAnalysisBase):
    id: UUID
    verdict: PhishingVerdict
    confidence_score: float
    spf_pass: Optional[bool] = None
    dkim_pass: Optional[bool] = None
    dmarc_pass: Optional[bool] = None
    urls_found: int
    malicious_urls: int
    url_details: Optional[Dict[str, Any]] = None
    attachments_count: int
    malicious_attachments: int
    attachment_details: Optional[Dict[str, Any]] = None
    ml_features: Optional[Dict[str, Any]] = None
    ml_model_version: Optional[str] = None
    header_anomalies: Optional[Dict[str, Any]] = None
    raw_headers: Optional[str] = None
    body_text: Optional[str] = None
    ai_summary: Optional[str] = None
    email_path: Optional[str] = None
    analyzed_by_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
