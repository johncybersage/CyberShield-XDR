"""
CyberShield XDR — Dashboard Endpoints
Returns aggregated live metrics for the main dashboard.
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import CurrentUser
from backend.database.session import get_db
from backend.schemas.dashboard import DashboardStats
from backend.services.dashboard.service import DashboardService

router = APIRouter()


@router.get("", response_model=DashboardStats, summary="Get live dashboard metrics")
async def get_dashboard(
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Returns all dashboard metrics in a single request:
    - Summary cards (assets, alerts, scans, IOCs, risk score)
    - Severity breakdown, 7-day time series
    - Top attacked assets, countries, MITRE techniques
    - Recent alerts
    """
    service = DashboardService(db)
    return await service.get_stats()
