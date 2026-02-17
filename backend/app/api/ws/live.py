"""WebSocket live endpoint — /ws/live."""
from __future__ import annotations

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.services.ws_broadcaster import ws_broadcaster

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/live")
async def ws_live(
    ws: WebSocket,
    session_id: str = Query(...),
    token: str | None = Query(default=None),
):
    """WebSocket endpoint for live ECG monitoring.
    
    Clients connect with session_id and receive:
    - waveform: ECG waveform chunks for chart rendering
    - prediction: per-beat prediction badge updates
    - alert: new alert notifications
    """
    # Accept connection (token validation can be added here)
    await ws.accept()
    await ws_broadcaster.connect(session_id, ws)

    try:
        while True:
            # Keep connection alive, handle client messages if needed
            data = await ws.receive_text()
            # Client can send control messages (e.g., ping)
            if data == "ping":
                await ws.send_text('{"type":"pong"}')
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WS error: {e}")
    finally:
        await ws_broadcaster.disconnect(session_id, ws)
