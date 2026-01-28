# app/main.py
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .state import store
from .routers import auth, dashboard, ingest, ws, hub, devices

app = FastAPI(title="Konpanion Hub", version="0.1.0")

# Sessions (needed for request.session)
app.add_middleware(
    SessionMiddleware,
    secret_key=getattr(settings, "SECRET_KEY", None) or "konpanion-hub-dev-secret",
    same_site="lax",
    https_only=False,
)

# Static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(devices.router)
app.include_router(auth.router)
app.include_router(dashboard.router)   # <-- dashboard routes live here
app.include_router(ingest.router)
app.include_router(ws.router)
app.include_router(hub.router, prefix="/api", tags=["api"])


# ✅ FIX 1: Make "/" handle BOTH GET and HEAD
# and redirect to your dashboard page
@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
async def root():
    # change "/dashboard" if your dashboard URL is different
    return RedirectResponse(url="/dashboard", status_code=307)


# (optional) health check
@app.get("/health")
async def health():
    return {"ok": True, "hub_id": store.hub_id}


# ✅ FIX 2: whoami endpoint
# Your JS should call "/_whoami" (not "/api/_whoami")
@app.get("/_whoami")
async def whoami(request: Request):
    # If you store user data in session, this will show it
    return JSONResponse(
        {
            "session": dict(request.session),
            "hub_id": store.hub_id,
        }
    )
