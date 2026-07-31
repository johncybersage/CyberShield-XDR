"""
CyberShield XDR — Dashboard Service
Aggregates live metrics from all platform modules.
Uses a single DB session with parallel queries for performance.
"""
from datetime import datetime, timedelta, timezone
from typing import List

import sqlalchemy as sa
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.logging_config import get_logger
from backend.models.alert import Alert, AlertSeverity, AlertStatus
from backend.models.asset import Asset
from backend.models.scan import Scan, ScanStatus
from backend.models.threat_intel import ThreatIntelligence
from backend.schemas.dashboard import (
    DashboardStats,
    MetricCard,
    RecentAlert,
    SeverityBreakdown,
    TimeSeriesPoint,
    TopItem,
)

logger = get_logger(__name__)


class DashboardService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_stats(self) -> DashboardStats:
        """Fetch all dashboard metrics in one service call."""
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        prev_week = now - timedelta(days=14)

        # Run all count queries
        total_assets = await self._count(Asset)
        prev_assets = await self._count_before(Asset, prev_week, week_ago)

        open_alerts = await self._count(Alert, Alert.status == AlertStatus.OPEN)
        prev_open = await self._count_before(Alert, prev_week, week_ago, Alert.status == AlertStatus.OPEN)

        active_scans = await self._count(Scan, Scan.status == ScanStatus.RUNNING)
        total_iocs = await self._count(ThreatIntelligence)

        # Risk score: average of asset risk scores
        risk_result = await self.db.execute(select(func.avg(Asset.risk_score)))
        avg_risk = round(float(risk_result.scalar_one() or 0.0), 1)

        # Severity breakdown
        sev_rows = await self.db.execute(
            select(Alert.severity, func.count(Alert.id))
            .where(Alert.status == AlertStatus.OPEN)
            .group_by(Alert.severity)
        )
        sev_map = {row[0]: row[1] for row in sev_rows}

        # Asset status breakdown
        status_rows = await self.db.execute(
            select(Asset.status, func.count(Asset.id)).group_by(Asset.status)
        )
        asset_status = {str(row[0]): row[1] for row in status_rows}

        # Alerts over time (last 7 days, daily buckets)
        alerts_ts = await self._time_series(Alert, week_ago)
        scans_ts = await self._time_series(Scan, week_ago)

        # Top attacked assets
        top_assets_rows = await self.db.execute(
            select(Asset.ip_address, func.count(Alert.id).label("cnt"))
            .join(Alert, Alert.asset_id == Asset.id, isouter=True)
            .group_by(Asset.ip_address)
            .order_by(func.count(Alert.id).desc())
            .limit(5)
        )
        top_assets = [
            TopItem(label=row[0], count=row[1], percentage=0.0)
            for row in top_assets_rows
        ]

        # Top threat countries
        country_rows = await self.db.execute(
            select(ThreatIntelligence.country_name, func.count(ThreatIntelligence.id).label("cnt"))
            .where(ThreatIntelligence.country_name.isnot(None))
            .group_by(ThreatIntelligence.country_name)
            .order_by(func.count(ThreatIntelligence.id).desc())
            .limit(5)
        )
        top_countries = [
            TopItem(label=row[0] or "Unknown", count=row[1])
            for row in country_rows
        ]

        # Top MITRE techniques
        mitre_rows = await self.db.execute(
            select(Alert.mitre_technique_id, func.count(Alert.id).label("cnt"))
            .where(Alert.mitre_technique_id.isnot(None))
            .group_by(Alert.mitre_technique_id)
            .order_by(func.count(Alert.id).desc())
            .limit(5)
        )
        top_mitre = [
            TopItem(label=row[0] or "Unknown", count=row[1])
            for row in mitre_rows
        ]

        # Recent alerts
        recent_rows = await self.db.execute(
            select(Alert)
            .order_by(Alert.created_at.desc())
            .limit(10)
        )
        recent_alerts = [
            RecentAlert(
                id=str(a.id),
                title=a.title,
                severity=a.severity,
                source=a.source,
                created_at=a.created_at.isoformat(),
                status=a.status,
            )
            for a in recent_rows.scalars()
        ]

        def _card(value, prev, label, fmt=None) -> MetricCard:
            change = ((value - prev) / prev * 100) if prev else 0.0
            trend = "up" if change > 0 else ("down" if change < 0 else "neutral")
            return MetricCard(label=label, value=value, change_pct=round(change, 1), trend=trend)

        return DashboardStats(
            total_assets=_card(total_assets, prev_assets, "Total Assets"),
            open_alerts=_card(open_alerts, prev_open, "Open Alerts"),
            active_scans=MetricCard(label="Active Scans", value=active_scans),
            threat_intel_iocs=MetricCard(label="Threat IOCs", value=total_iocs),
            risk_score=MetricCard(label="Avg Risk Score", value=avg_risk),
            alerts_by_severity=SeverityBreakdown(
                critical=sev_map.get(AlertSeverity.CRITICAL, 0),
                high=sev_map.get(AlertSeverity.HIGH, 0),
                medium=sev_map.get(AlertSeverity.MEDIUM, 0),
                low=sev_map.get(AlertSeverity.LOW, 0),
                info=sev_map.get(AlertSeverity.INFO, 0),
            ),
            assets_by_status=asset_status,
            alerts_over_time=alerts_ts,
            scans_over_time=scans_ts,
            top_attacked_assets=top_assets,
            top_threat_countries=top_countries,
            top_mitre_techniques=top_mitre,
            recent_alerts=recent_alerts,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _count(self, model, *filters) -> int:
        q = select(func.count(model.id))
        for f in filters:
            q = q.where(f)
        result = await self.db.execute(q)
        return result.scalar_one() or 0

    async def _count_before(self, model, start, end, *filters) -> int:
        q = select(func.count(model.id)).where(
            and_(model.created_at >= start, model.created_at < end)
        )
        for f in filters:
            q = q.where(f)
        result = await self.db.execute(q)
        return result.scalar_one() or 0

    async def _time_series(self, model, since: datetime) -> List[TimeSeriesPoint]:
        """Daily counts for the last 7 days."""
        day_col = func.date_trunc(sa.literal_column("'day'"), model.created_at).label("day")
        rows = await self.db.execute(
            select(
                day_col,
                func.count(model.id).label("cnt"),
            )
            .where(model.created_at >= since)
            .group_by(day_col)
            .order_by(day_col)
        )
        return [
            TimeSeriesPoint(timestamp=str(row[0])[:10], value=row[1])
            for row in rows
        ]
