from __future__ import annotations
from fastapi import Request
from fastapi.responses import RedirectResponse
from itsdangerous import URLSafeSerializer, BadSignature
from .config import settings

COOKIE_NAME = "konpanion_session"

def _ser():
    return URLSafeSerializer(settings.session_secret, salt="konpanion-hub")

def create_session(username: str) -> str:
    return _ser().dumps({"u": username})

def read_session(token: str | None) -> str | None:
    if not token:
        return None
    try:
        data = _ser().loads(token)
        return data.get("u")
    except BadSignature:
        return None

def require_auth(request: Request) -> str | None:
    token = request.cookies.get(COOKIE_NAME)
    return read_session(token)

def redirect_to_login():
    return RedirectResponse(url="/login", status_code=302)
