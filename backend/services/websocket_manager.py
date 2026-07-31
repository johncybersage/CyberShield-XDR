"""
CyberShield XDR — WebSocket Connection Manager
Manages connected clients and broadcasts real-time events.
Used by alert creation, IDS detections, and scan completions.
"""
import json
from typing import Dict, Set

from fastapi import WebSocket

from backend.config.logging_config import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """
    Thread-safe WebSocket connection manager.
    Supports per-user connections and broadcast to all clients.
    """

    def __init__(self):
        # user_id -> set of active WebSocket connections
        self._connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        await websocket.accept()
        if user_id not in self._connections:
            self._connections[user_id] = set()
        self._connections[user_id].add(websocket)
        logger.debug(f"WebSocket connected: user={user_id}, total={self.total_connections}")

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        if user_id in self._connections:
            self._connections[user_id].discard(websocket)
            if not self._connections[user_id]:
                del self._connections[user_id]
        logger.debug(f"WebSocket disconnected: user={user_id}, total={self.total_connections}")

    async def send_to_user(self, user_id: str, event: dict) -> None:
        """Send an event to all connections for a specific user."""
        if user_id not in self._connections:
            return
        dead: Set[WebSocket] = set()
        for ws in self._connections[user_id]:
            try:
                await ws.send_text(json.dumps(event))
            except Exception:
                dead.add(ws)
        for ws in dead:
            self._connections[user_id].discard(ws)

    async def broadcast(self, event: dict) -> None:
        """Broadcast an event to ALL connected clients."""
        message = json.dumps(event)
        dead: list = []
        for user_id, connections in self._connections.items():
            for ws in connections:
                try:
                    await ws.send_text(message)
                except Exception:
                    dead.append((user_id, ws))
        for user_id, ws in dead:
            if user_id in self._connections:
                self._connections[user_id].discard(ws)

    @property
    def total_connections(self) -> int:
        return sum(len(v) for v in self._connections.values())


# Module-level singleton shared across the app
manager = ConnectionManager()
