# backend/app/routers/dashboard.py

from __future__ import annotations

from fastapi import APIRouter, Request, Form
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    Response,
)
from fastapi.templating import Jinja2Templates
from starlette.status import (
    HTTP_200_OK,
    HTTP_302_FOUND,
    HTTP_303_SEE_OTHER,
    HTTP_307_TEMPORARY_REDIRECT,
)

router = APIRouter()

# Templates live in backend/app/templates (your WorkingDirectory is backend/)
templates = Jinja2Templates(directory="app/templates")

# ---------------------------------------------------------------------
# Simple auth (TEMP): admin/admin via cookie
# Later replace with real auth + hashed passwords + DB.
# ---------------------------------------------------------------------
AUTH_COOKIE = "konpanion_auth"
AUTH_COOKIE_VALUE = "admin"  # minimal marker
TEMP_USERNAME = "admin"
TEMP_PASSWORD = "admin"


def _is_authed(request: Request) -> bool:
    return request.cookies.get(AUTH_COOKIE) == AUTH_COOKIE_VALUE


def _require_auth(request: Request) -> RedirectResponse | None:
    """Return redirect response if not authed, else None."""
    if _is_authed(request):
        return None
    # Preserve destination so login can bring you back
    dest = request.url.path
    return RedirectResponse(url=f"/login?next={dest}", status_code=HTTP_303_SEE_OTHER)


def _set_auth_cookie(resp: Response) -> None:
    # Cookie scoped to whole site. Use SameSite=Lax so it works on phones.
    # Secure=False because we're serving HTTP on a local AP.
    resp.set_cookie(
        key=AUTH_COOKIE,
        value=AUTH_COOKIE_VALUE,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
        max_age=60 * 60 * 24 * 7,  # 7 days
    )


def _clear_auth_cookie(resp: Response) -> None:
    resp.delete_cookie(key=AUTH_COOKIE, path="/")


# ---------------------------------------------------------------------
# Root + HEAD handlers (fixes 405 noise from phones / captive checks)
# ---------------------------------------------------------------------
@router.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    # Always land users on the dashboard page
    return RedirectResponse(url="/dashboard", status_code=HTTP_307_TEMPORARY_REDIRECT)


@router.head("/", include_in_schema=False)
def head_root() -> Response:
    return Response(status_code=HTTP_200_OK)


@router.head("/dashboard", include_in_schema=False)
def head_dashboard() -> Response:
    return Response(status_code=HTTP_200_OK)


@router.head("/telemetry", include_in_schema=False)
def head_telemetry() -> Response:
    return Response(status_code=HTTP_200_OK)


@router.head("/settings", include_in_schema=False)
def head_settings() -> Response:
    return Response(status_code=HTTP_200_OK)


# ---------------------------------------------------------------------
# Captive portal / OS connectivity probes (reduce "Invalid HTTP request")
# ---------------------------------------------------------------------
_CAPTIVE_PATHS = (
    "/generate_204",          # Android
    "/hotspot-detect.html",   # Apple
    "/ncsi.txt",              # Windows
    "/connecttest.txt",       # Windows
    "/redirect",              # Some captive flows
)

@router.get("/generate_204", include_in_schema=False)
@router.get("/hotspot-detect.html", include_in_schema=False)
@router.get("/ncsi.txt", include_in_schema=False)
@router.get("/connecttest.txt", include_in_schema=False)
@router.get("/redirect", include_in_schema=False)
def captive_probe_get() -> RedirectResponse:
    # Send them somewhere predictable
    return RedirectResponse(url="/dashboard", status_code=HTTP_302_FOUND)


@router.head("/generate_204", include_in_schema=False)
@router.head("/hotspot-detect.html", include_in_schema=False)
@router.head("/ncsi.txt", include_in_schema=False)
@router.head("/connecttest.txt", include_in_schema=False)
@router.head("/redirect", include_in_schema=False)
def captive_probe_head() -> Response:
    return Response(status_code=HTTP_200_OK)


# ---------------------------------------------------------------------
# Login / Logout
# ---------------------------------------------------------------------
@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login_page(request: Request, next: str = "/dashboard"):
    # If already authed, skip
    if _is_authed(request):
        return RedirectResponse(url=next or "/dashboard", status_code=HTTP_303_SEE_OTHER)

    # IMPORTANT: This expects app/templates/login.html
    # If you don't have it yet, create a basic one, or tell me and I’ll paste it.
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "next": next,
            "error": None,
        },
    )


@router.post("/login", include_in_schema=False)
def login_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form("/dashboard"),
):
    if username == TEMP_USERNAME and password == TEMP_PASSWORD:
        resp = RedirectResponse(url=next or "/dashboard", status_code=HTTP_303_SEE_OTHER)
        _set_auth_cookie(resp)
        return resp

    # invalid creds → render page with error
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "next": next,
            "error": "Invalid credentials (try admin/admin).",
        },
        status_code=200,
    )


@router.get("/logout", include_in_schema=False)
def logout():
    resp = RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    _clear_auth_cookie(resp)
    return resp


# ---------------------------------------------------------------------
# Dashboard pages
# ---------------------------------------------------------------------
@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard(request: Request):
    guard = _require_auth(request)
    if guard:
        return guard

    # If your dashboard expects variables, pass them in this dict
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
        },
    )


@router.get("/telemetry", response_class=HTMLResponse, include_in_schema=False)
def telemetry(request: Request):
    guard = _require_auth(request)
    if guard:
        return guard

    return templates.TemplateResponse(
        "telemetry.html",
        {
            "request": request,
        },
    )


@router.get("/settings", response_class=HTMLResponse, include_in_schema=False)
def settings(request: Request):
    guard = _require_auth(request)
    if guard:
        return guard

    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
        },
    )
