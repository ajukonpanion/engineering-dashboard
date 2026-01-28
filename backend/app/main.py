# app/main.py
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from .state import store
from .routers import auth, dashboard, ingest, ws, hub, devices

app = FastAPI(title="Konpanion Hub", version="0.1.0")

# Sessions (needed for request.session) — ONLY ONCE
app.add_middleware(
    SessionMiddleware,
    secret_key="SOME_FIXED_SECRET_CHANGE_ME_ONCE_AND_KEEP_IT",
    same_site="lax",
    https_only=False,
)

# Static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers — include each ONCE
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(devices.router)
app.include_router(ingest.router)
app.include_router(ws.router)
app.include_router(hub.router, prefix="/api", tags=["api"])


# Root: handle BOTH GET + HEAD
@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
async def root():
    return RedirectResponse(url="/dashboard", status_code=307)


@app.get("/health")
async def health():
    return {"ok": True, "hub_id": store.hub_id}


@app.get("/_whoami")
async def whoami(request: Request):
    return JSONResponse(
        {
            "session": dict(request.session),
            "hub_id": store.hub_id,
        }
    )
