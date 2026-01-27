# backend/app/routers/ws.py
from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..auth import read_session, COOKIE_NAME
from ..state import ws_broker

router = APIRouter(prefix="/ws", tags=["ws"])

@router.websocket("/telemetry")
async def telemetry_ws(ws: WebSocket):
    # cookie-based session auth
    token = ws.cookies.get(COOKIE_NAME)
    if not read_session(token):
        await ws.close(code=4401)
        return

    await ws.accept()
    ws_broker.add(ws)
    try:
        while True:
            # keepalive pings (client sends "ping")
            await ws.receive_text()
    except WebSocketDisconnect:
        ws_broker.remove(ws)
