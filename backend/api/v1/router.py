"""
CyberShield XDR — API v1 Router
Aggregates all endpoint routers. Adding a new module = one line here.
"""
from fastapi import APIRouter

from backend.api.v1.endpoints import (
    ai_assistant,
    alerts,
    assets,
    auth,
    dashboard,
    logs,
    malware,
    notifications,
    phishing,
    reports,
    scans,
    threat_intel,
    users,
    websocket,
    network,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(scans.router, prefix="/scans", tags=["Vulnerability Scanner"])
api_router.include_router(threat_intel.router, prefix="/threat-intel", tags=["Threat Intelligence"])
api_router.include_router(malware.router, prefix="/malware", tags=["Malware Analysis"])
api_router.include_router(phishing.router, prefix="/phishing", tags=["Phishing Detection"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(logs.router, prefix="/logs", tags=["Logs"])
api_router.include_router(ai_assistant.router, prefix="/ai", tags=["AI Assistant"])
api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
api_router.include_router(network.router, prefix="/network", tags=["Network IDS"])
