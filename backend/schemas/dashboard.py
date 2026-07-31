"""
CyberShield XDR — Dashboard Schemas
Typed response models for all dashboard metrics and chart data.
"""
from typing import List

from pydantic import BaseModel


class MetricCard(BaseModel):
    label: str
    value: int | float
    change_pct: float = 0.0   # % change vs previous period
    trend: str = "neutral"    # "up" | "down" | "neutral"


class SeverityBreakdown(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0


class TimeSeriesPoint(BaseModel):
    timestamp: str
    value: int


class TopItem(BaseModel):
    label: str
    count: int
    percentage: float = 0.0


class RecentAlert(BaseModel):
    id: str
    title: str
    severity: str
    source: str
    created_at: str
    status: str


class DashboardStats(BaseModel):
    # Summary cards
    total_assets: MetricCard
    open_alerts: MetricCard
    active_scans: MetricCard
    threat_intel_iocs: MetricCard
    risk_score: MetricCard

    # Breakdowns
    alerts_by_severity: SeverityBreakdown
    assets_by_status: dict

    # Time series (last 7 days)
    alerts_over_time: List[TimeSeriesPoint]
    scans_over_time: List[TimeSeriesPoint]

    # Top lists
    top_attacked_assets: List[TopItem]
    top_threat_countries: List[TopItem]
    top_mitre_techniques: List[TopItem]

    # Recent activity
    recent_alerts: List[RecentAlert]
