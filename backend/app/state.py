# app/state.py
from __future__ import annotations

import asyncio
from typing import Set, Optional, Any

from .config import settings
from .store import HubStore


class WebSocketBroker:
    def __init__(self):
        self.clients: Set[Any] = set()
        self._lock = asyncio.Lock()

    def add(self, ws: Any) -> None:
        self.clients.add(ws)

    def remove(self, ws: Any) -> None:
        if ws in self.clients:
            self.clients.remove(ws)

    async def broadcast(self, msg: Optional[dict]) -> None:
        if not msg:
            return
        dead = []
        async with self._lock:
            for ws in list(self.clients):
                try:
                    await ws.send_json(msg)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self.remove(ws)


# Shared singletons live here (NOT in main.py)
store = HubStore(hub_id=settings.hub_id, max_samples=settings.max_samples)
ws_broker = WebSocketBroker()
