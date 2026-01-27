from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()

# Try to use templates folder if it exists: backend/app/templates
TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _logged_in(request: Request) -> bool:
    # SessionMiddleware must be enabled in main.py (you already did that)
    return bool(request.session.get("user"))


def _fallback_html(user: str) -> str:
    return f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8"/>
      <meta name="viewport" content="width=device-width, initial-scale=1"/>
      <title>Konpanion Hub — Dashboard</title>
      <style>
        body {{
          background:#0b0e11; color:#eaeaea;
          font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
          margin:0; padding:24px;
        }}
        .row {{ display:flex; gap:12px; flex-wrap:wrap; }}
        .card {{
          background:#11151a; border-radius:14px; padding:18px;
          box-shadow: 0 0 0 1px rgba(255,255,255,0.05),
                      0 10px 30px rgba(0,0,0,0.6);
          min-width: 260px;
        }}
        a, button {{
          color:#0b0e11; text-decoration:none;
        }}
        .btn {{
          display:inline-block;
          padding:10px 14px; border-radius:10px;
          background: linear-gradient(135deg, #4ea1ff, #6b7cff);
          font-weight:600;
          border: none;
          cursor:pointer;
        }}
        .muted {{ color:#7a8596; }}
        form {{ display:inline; }}
      </style>
    </head>
    <body>
      <h2>Konpanion Hub — Dashboard</h2>
      <p class="muted">Logged in as <b>{user}</b></p>

      <div class="row">
        <div class="card">
          <h3>Hub</h3>
          <p class="muted">API health / hub snapshot lives under <code>/api</code></p>
          <p><a class="btn" href="/api/hub">View /api/hub</a></p>
        </div>

        <div class="card">
          <h3>Telemetry</h3>
          <p class="muted">WebSocket endpoint: <code>/ws/telemetry</code></p>
          <p class="muted">Once devices send data, you’ll see live updates.</p>
        </div>

        <div class="card">
          <h3>Session</h3>
          <form method="post" action="/logout">
            <button class="btn" type="submit">Logout</button>
          </form>
        </div>
      </div>
    </body>
    </html>
    """


@router.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    if not _logged_in(request):
        return RedirectResponse(url="/login", status_code=303)

    user = request.session.get("user", "admin")

    # If you have a template file, use it: backend/app/templates/dashboard.html
    if TEMPLATES_DIR.exists() and (TEMPLATES_DIR / "dashboard.html").exists():
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "user": user},
        )

    # Otherwise show a built-in dashboard page
    return HTMLResponse(_fallback_html(user))


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_alias(request: Request):
    return await dashboard_page(request)
