from __future__ import annotations
from fastapi import APIRouter, Header, HTTPException
from datetime import datetime, timezone
from typing import Optional

from ..config import settings
from ..models import VAELTelemetry, SNUUTelemetry, NOOHTelemetry, TelemetryUnion
from ..state import store, ws_broker

router = APIRouter(prefix="/ingest", tags=["ingest"])

def _check_token(x_konpanion_token: Optional[str]) -> None:
    if settings.ingest_token:
        if not x_konpanion_token or x_konpanion_token != settings.ingest_token:
            raise HTTPException(status_code=401, detail="Invalid ingest token.")

def _ensure_ts(evt: TelemetryUnion) -> TelemetryUnion:
    # If device doesn't provide ts, set hub-received time (still not fake; it's real receipt time).
    if evt.ts is None:
        evt.ts = datetime.now(timezone.utc)
    return evt

@router.post("/vael")
async def ingest_vael(evt: VAELTelemetry, x_konpanion_token: Optional[str] = Header(default=None)):
    _check_token(x_konpanion_token)
    evt = _ensure_ts(evt)
    store.upsert_telemetry(evt)
    await ws_broker.broadcast(store.last_event)
    return {"ok": True}

@router.post("/snuu")
async def ingest_snuu(evt: SNUUTelemetry, x_konpanion_token: Optional[str] = Header(default=None)):
    _check_token(x_konpanion_token)
    evt = _ensure_ts(evt)
    store.upsert_telemetry(evt)
    await ws_broker.broadcast(store.last_event)
    return {"ok": True}

@router.post("/nooh")
async def ingest_nooh(evt: NOOHTelemetry, x_konpanion_token: Optional[str] = Header(default=None)):
    _check_token(x_konpanion_token)
    evt = _ensure_ts(evt)
    store.upsert_telemetry(evt)
    await ws_broker.broadcast(store.last_event)
    return {"ok": True}
