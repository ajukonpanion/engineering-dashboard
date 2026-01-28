# backend/app/routers/devices.py
from __future__ import annotations

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from pathlib import Path

from app.auth import require_auth, redirect_to_login
from app.config import settings
from app.users import load_users
from app.discovery.wifi import scan_and_update_registry
from app.device_registry import registry, DeviceState

router = APIRouter(prefix="/api/devices", tags=["devices"])


def _wants_html(request: Request) -> bool:
    accept = (request.headers.get("accept") or "").lower()
    return "text/html" in accept


def _users_path() -> str:
    """
    Your config may expose this differently. We try a few safe options.
    """
    # 1) preferred: settings.users_path
    p = getattr(settings, "users_path", None)
    if p:
        return str(p)

    # 2) fallback: backend/users.json (your tree shows it exists here)
    # This file lives at backend/app/routers/devices.py -> parents[2] == backend
    backend_dir = Path(__file__).resolve().parents[2]
    return str(backend_dir / "users.json")


def _require_admin_like_access(request: Request) -> str:
    """
    Admin-only gate for now:
    - must have a valid session username
    - username must be present in users.json (loaded via load_users)
    No fake roles are introduced.
    """
    username = require_auth(request)
    if not username:
        if _wants_html(request):
            # for browser navigation
            raise HTTPException(status_code=401, detail="Not logged in")
        raise HTTPException(status_code=401, detail="Not logged in")

    db = load_users(_users_path())
    if username not in db.users:
        raise HTTPException(status_code=403, detail="Forbidden")

    return username


class ConnectRequest(BaseModel):
    device_id: str


@router.get("/discover")
def discover(request: Request):
    _require_admin_like_access(request)

    devices = scan_and_update_registry()
    return {
        "count": len(devices),
        "devices": [
            {
                "device_id": d.device_id,
                "device_type": d.device_type,
                "ssid": d.ssid,
                "rssi": d.rssi,
                "state": d.state,
                "last_seen": d.last_seen,
                "last_error": d.last_error,
            }
            for d in devices
        ],
    }


@router.post("/connect")
def connect_intent(request: Request, body: ConnectRequest):
    _require_admin_like_access(request)

    d = registry.get(body.device_id)
    if not d:
        raise HTTPException(status_code=404, detail="Device not found (discover first)")

    # Step 2: logical connect state only (no OS wifi switching yet)
    registry.set_state(body.device_id, DeviceState.CONNECTING)
    registry.set_state(body.device_id, DeviceState.CONNECTED)

    d2 = registry.get(body.device_id)
    return {"success": True, "device": d2.__dict__ if d2 else None}
