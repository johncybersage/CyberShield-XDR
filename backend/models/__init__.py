"""
CyberShield XDR — Models Package
Import all models here so Alembic's autogenerate can discover them.
"""
from backend.models.alert import Alert, AlertSeverity, AlertSource, AlertStatus
from backend.models.asset import Asset, AssetStatus, AssetType
from backend.models.audit_log import AuditLog
from backend.models.malware import AnalysisStatus, MalwareAnalysis, MalwareVerdict
from backend.models.network import NetworkAnalysis
from backend.models.notification import (
    Notification,
    NotificationChannel,
    NotificationStatus,
)
from backend.models.phishing import PhishingAnalysis, PhishingVerdict
from backend.models.report import Report, ReportFormat, ReportStatus, ReportType
from backend.models.scan import Scan, ScanStatus, ScanType
from backend.models.threat_intel import IOCType, ThreatCategory, ThreatIntelligence
from backend.models.user import User, UserRole

__all__ = [
    "User", "UserRole",
    "Asset", "AssetType", "AssetStatus",
    "NetworkAnalysis",
    "Alert", "AlertSeverity", "AlertStatus", "AlertSource",
    "Scan", "ScanType", "ScanStatus",
    "ThreatIntelligence", "IOCType", "ThreatCategory",
    "MalwareAnalysis", "AnalysisStatus", "MalwareVerdict",
    "PhishingAnalysis", "PhishingVerdict",
    "Report", "ReportType", "ReportFormat", "ReportStatus",
    "AuditLog",
    "Notification", "NotificationChannel", "NotificationStatus",
]
