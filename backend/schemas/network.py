from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel

from backend.models.network import NetworkAnalysisStatus


class NetworkAnomaly(BaseModel):
    type: str
    description: str
    severity: str


class NetworkAnalysisBase(BaseModel):
    filename: str
    file_size: int
    status: NetworkAnalysisStatus
    total_packets: int
    tcp_count: int
    udp_count: int
    icmp_count: int
    other_count: int
    anomalies_found: int
    anomaly_details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class NetworkAnalysisResponse(NetworkAnalysisBase):
    id: UUID
    storage_path: str
    analyzed_by_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
