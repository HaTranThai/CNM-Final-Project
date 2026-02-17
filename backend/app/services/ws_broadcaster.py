"""WebSocket broadcaster — manages WS connections per session."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WSBroadcaster:
    """Manage WebSocket connections and broadcast messages by session_id."""

    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, session_id: str, ws: WebSocket):
        async with self._lock:
            if session_id not in self._connections:
                self._connections[session_id] = set()
            self._connections[session_id].add(ws)
        logger.info(f"WS client connected to session {session_id[:8]}... (total: {len(self._connections.get(session_id, set()))})")

    async def disconnect(self, session_id: str, ws: WebSocket):
        async with self._lock:
            if session_id in self._connections:
                self._connections[session_id].discard(ws)
                if not self._connections[session_id]:
                    del self._connections[session_id]
        logger.info(f"WS client disconnected from session {session_id[:8]}...")

    async def broadcast(self, session_id: str, message_type: str, data: dict):
        """Broadcast a message to all WS clients for a session."""
        if session_id not in self._connections:
            return

        payload = json.dumps({"type": message_type, "data": data})
        dead = set()

        for ws in self._connections.get(session_id, set()).copy():
            try:
                await ws.send_text(payload)
            except Exception:
                dead.add(ws)

        # Clean up dead connections
        if dead:
            async with self._lock:
                if session_id in self._connections:
                    self._connections[session_id] -= dead

    async def broadcast_all(self, message_type: str, data: dict):
        """Broadcast to all sessions."""
        for session_id in list(self._connections.keys()):
            await self.broadcast(session_id, message_type, data)

    @property
    def active_sessions(self) -> list[str]:
        return list(self._connections.keys())


# Global singleton
ws_broadcaster = WSBroadcaster()
