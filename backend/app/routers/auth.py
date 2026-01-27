from __future__ import annotations

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter()

LOGIN_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Konpanion Hub — Login</title>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>

  <style>
    body {
      background: #0b0e11;
      color: #eaeaea;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      margin: 0;
      padding: 0;
    }

    .card {
      max-width: 380px;
      margin: 12vh auto;
      padding: 24px;
      background: #11151a;
      border-radius: 14px;
      box-shadow: 0 0 0 1px rgba(255,255,255,0.05),
                  0 10px 30px rgba(0,0,0,0.6);
    }

    h2 {
      margin-top: 0;
      margin-bottom: 16px;
      font-weight: 600;
      text-align: center;
    }

    input {
      width: 100%;
      padding: 12px;
      margin: 10px 0;
      border-radius: 10px;
      border: 1px solid #2a2f36;
      background: #0f1318;
      color: #eaeaea;
      font-size: 14px;
    }

    input:focus {
      outline: none;
      border-color: #4ea1ff;
    }

    button {
      width: 100%;
      margin-top: 12px;
      padding: 12px;
      border-radius: 10px;
      border: none;
      background: linear-gradient(135deg, #4ea1ff, #6b7cff);
      color: #0b0e11;
      font-weight: 600;
      cursor: pointer;
      font-size: 15px;
    }

    button:hover {
      opacity: 0.92;
    }

    .error {
      background: rgba(255, 80, 80, 0.12);
      border: 1px solid rgba(255, 80, 80, 0.35);
      padding: 10px;
      border-radius: 10px;
      margin-bottom: 12px;
      color: #ffb3b3;
      font-size: 13px;
      text-align: center;
    }

    .footer {
      margin-top: 18px;
      text-align: center;
      font-size: 12px;
      color: #7a8596;
    }
  </style>
</head>

<body>
  <div class="card">
    <h2>Konpanion Hub</h2>

    __ERROR_BLOCK__

    <form method="post" action="/login">
      <input name="username" placeholder="Username" required />
      <input name="password" type="password" placeholder="Password" required />
      <button type="submit">Sign in</button>
    </form>

    <div class="footer">
      Local Engineering Dashboard
    </div>
  </div>
</body>
</html>
"""


def _render(error: str | None = None) -> HTMLResponse:
    error_block = ""
    if error:
        error_block = f"<div class='error'>{error}</div>"

    html = LOGIN_HTML.replace("__ERROR_BLOCK__", error_block)
    return HTMLResponse(html)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get("user"):
        return RedirectResponse(url="/", status_code=303)
    return _render()


@router.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    # 🔐 For now: simple local credentials
    # Later: replace with hashed user store
    if username != "admin" or password != "admin":
        return _render("Invalid username or password.")

    request.session["user"] = username
    return RedirectResponse(url="/", status_code=303)


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
