# app/main.py
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .state import store
from .routers import auth, dashboard, ingest, ws, hub

app = FastAPI(title="Konpanion Hub", version="0.1.0")

# Sessions (needed for request.session)
app.add_middleware(
    SessionMiddleware,
    secret_key=getattr(settings, "SECRET_KEY", None) or "konpanion-hub-dev-secret",
    same_site="lax",
    https_only=False,  # set True if you serve behind HTTPS
)

# Static (optional - only if app/static exists)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(ingest.router)
app.include_router(ws.router)
app.include_router(hub.router, prefix="/api", tags=["api"])


@app.get("/health")
async def health():
    return {"ok": True, "hub_id": store.hub_id}


@app.get("/_whoami")
async def whoami(request: Request):
    return {"session": dict(request.session), "hub_id": store.hub_id}
