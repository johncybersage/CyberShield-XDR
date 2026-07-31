from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import AnalystUser, CurrentUser
from backend.database.session import get_db
from backend.models.threat_intel import ThreatIntelligence
from backend.schemas.threat_intel import ThreatIntelligenceResponse
from backend.services.threat_intel.service import threat_intel_service

router = APIRouter()

@router.get("", response_model=List[ThreatIntelligenceResponse], summary="List IOCs")
async def list_iocs(
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None
):
    query = select(ThreatIntelligence)
    if search:
        query = query.where(ThreatIntelligence.value.ilike(f"%{search}%"))
        
    query = query.order_by(ThreatIntelligence.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/lookup", response_model=ThreatIntelligenceResponse, summary="Lookup IOC")
async def lookup_ioc(
    current_user: AnalystUser,
    value: str = Query(..., description="The IP, domain, URL, or hash to lookup"),
    db: AsyncSession = Depends(get_db)
):
    """
    On-demand threat intelligence lookup.
    Queries AbuseIPDB, VirusTotal, and OTX concurrently.
    """
    if not value.strip():
        raise HTTPException(status_code=400, detail="IOC value cannot be empty")
        
    try:
        intel = await threat_intel_service.lookup_ioc(db, value.strip())
        return intel
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ioc_id}", response_model=ThreatIntelligenceResponse, summary="Get IOC details")
async def get_ioc(
    ioc_id: UUID,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(ThreatIntelligence).where(ThreatIntelligence.id == ioc_id))
    intel = result.scalar_one_or_none()
    if not intel:
        raise HTTPException(status_code=404, detail="IOC not found")
    return intel
