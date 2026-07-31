"""
CyberShield XDR — WebSocket Endpoint
Authenticated WebSocket for real-time event streaming.
Clients receive: new alerts, scan completions, IDS detections, system notifications.
"""
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from jose import JWTError

from backend.auth.security import decode_token
from backend.config.logging_config import get_logger
from backend.services.websocket_manager import manager

router = APIRouter()
logger = get_logger(__name__)


@router.websocket("/events")
async def websocket_events(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token for authentication"),
):
    """
    Authenticated WebSocket endpoint.
    Connect with: ws://host/api/v1/ws/events?token=<access_token>

    Events pushed to client:
    - {"type": "alert.new", "data": {...}}
    - {"type": "scan.completed", "data": {...}}
    - {"type": "ids.detection", "data": {...}}
    - {"type": "notification", "data": {...}}
    - {"type": "ping"} — keepalive every 30s
    """
    # Authenticate before accepting the connection
    try:
        payload = decode_token(token, expected_type="access")
        user_id = payload["sub"]
    except (JWTError, KeyError):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, user_id)
    try:
        # Send welcome event
        await websocket.send_json({
            "type": "connected",
            "data": {"message": "Real-time event stream active", "user_id": user_id},
        })

        # Keep connection alive — client sends pings, we echo pongs
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.debug(f"WebSocket client disconnected: user={user_id}")
    except Exception as exc:
        logger.error(f"WebSocket error for user {user_id}: {exc}")
        manager.disconnect(websocket, user_id)
