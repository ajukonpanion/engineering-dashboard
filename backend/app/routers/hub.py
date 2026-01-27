# app/routers/hub.py
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from typing import Any

from ..state import store  # store should be your global HubStore instance

router = APIRouter()


@router.get("/hub")
async def hub_snapshot() -> Any:
    """
    Returns current hub snapshot.
    NOTE: Snapshot only shows devices that have actually sent telemetry.
    """
    # mark stale devices before returning snapshot (optional but useful)
    try:
        store.mark_stale_devices(stale_after_s=15)
    except Exception:
        # don't crash the API if stale marking fails
        pass
    return store.snapshot()


@router.get("/devices")
async def list_devices() -> Any:
    """List known devices (those that have sent telemetry)."""
    try:
        store.mark_stale_devices(stale_after_s=15)
    except Exception:
        pass
    snap = store.snapshot()
    return {"hub_id": snap.hub_id, "ts": snap.ts, "devices": list(snap.devices.values())}


@router.get("/device/{device_id}")
async def device_series(device_id: str) -> Any:
    """Return recent telemetry series for a device."""
    series = store.get_device_series(device_id)
    if not series:
        # device might exist in status but no buffered telemetry; check status
        if device_id in store.status:
            return {"device_id": device_id, "series": []}
        raise HTTPException(status_code=404, detail="Unknown device_id")
    return {"device_id": device_id, "series": series}
