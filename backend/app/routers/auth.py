"""Auth endpoints: /auth/login, /auth/callback, /auth/logout, /auth/me.

Sign in with Google, locked to ALLOWED_EMAILS. Without real Google creds, a localhost
dev sign-in keeps things usable. Hermes uses the bearer token (no browser) — see guard.py.
"""
from __future__ import annotations

import secrets
import urllib.parse

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from ..config import settings
from ..auth import guard
from ..auth.session import sign, COOKIE, MAX_AGE

router = APIRouter(prefix="/auth", tags=["auth"])
GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"


def _google_real() -> bool:
    return bool(settings.GOOGLE_CLIENT_ID) and not settings.GOOGLE_CLIENT_ID.startswith("__STUB")


def _login_page(msg: str = "") -> str:
    btn = ('<a class="b" href="/auth/login">Sign in with Google</a>' if _google_real()
           else '<a class="b" href="/auth/callback?dev=1">Dev sign-in (localhost)</a>')
    note = ("" if _google_real() else
            '<p class="m">Google creds not set — using local dev sign-in. See docs/GO-LIVE.md.</p>')
    err = f'<p class="e">{msg}</p>' if msg else ""
    return f"""<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Wise Old Man — Sign in</title>
<style>body{{margin:0;height:100vh;display:grid;place-items:center;background:#070910;color:#e7ebf2;
font-family:Inter,system-ui,sans-serif}}.c{{text-align:center}}.g{{width:56px;height:56px;border-radius:16px;
display:grid;place-items:center;margin:0 auto 16px;font-weight:900;color:#070910;background:#34d399;font-size:28px}}
.b{{display:inline-block;margin-top:18px;padding:10px 18px;border-radius:10px;background:#34d399;color:#070910;
font-weight:600;text-decoration:none}}.m{{color:#8a94a6;font-size:12px;margin-top:14px}}.e{{color:#ef4444;font-size:13px}}
h1{{font-size:18px;margin:0}}.s{{color:#8a94a6;font-size:11px;text-transform:uppercase;letter-spacing:.18em}}</style>
<div class=c><div class=g>W</div><div class=s>command center</div><h1>Wise Old Man</h1>{err}{btn}{note}</div>"""


@router.get("/login")
def login(request: Request):
    if _google_real():
        state = secrets.token_urlsafe(16)
        params = {"client_id": settings.GOOGLE_CLIENT_ID,
                  "redirect_uri": settings.WOM_PUBLIC_URL.rstrip("/") + "/auth/callback",
                  "response_type": "code", "scope": "openid email profile",
                  "state": state, "access_type": "online", "prompt": "select_account"}
        resp = RedirectResponse(GOOGLE_AUTH + "?" + urllib.parse.urlencode(params))
        resp.set_cookie("wom_oauth_state", state, httponly=True, max_age=600, samesite="lax")
        return resp
    return HTMLResponse(_login_page())


@router.get("/callback")
def callback(request: Request, code: str = None, state: str = None, dev: int = 0):
    if dev and settings.AUTH_DEV_BYPASS and guard.is_loopback(request):
        email = settings.ALLOWED_EMAILS[0] if settings.ALLOWED_EMAILS else "dev@localhost"
    elif _google_real() and code:
        # TODO(live): verify `state` cookie, exchange code->tokens, validate id_token -> email.
        # Needs google-auth-oauthlib (or an httpx call to the token + userinfo endpoints).
        return JSONResponse({"error": "google_token_exchange_not_wired",
                             "hint": "see docs/GO-LIVE.md — add google-auth-oauthlib + creds"}, status_code=501)
    else:
        return HTMLResponse(_login_page("Sign-in unavailable."), status_code=400)

    if email.lower() not in settings.ALLOWED_EMAILS:
        return HTMLResponse(_login_page("Not authorized."), status_code=403)
    resp = RedirectResponse("/")
    resp.set_cookie(COOKIE, sign(email), httponly=True, samesite="lax", max_age=MAX_AGE,
                    secure=settings.WOM_PUBLIC_URL.startswith("https"))
    return resp


@router.post("/logout")
def logout():
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(COOKIE)
    return resp


@router.get("/me")
def me(request: Request):
    ident = guard.resolve_identity(request)
    if not ident:
        return JSONResponse({"authed": False, "mode": settings.AUTH_MODE})
    return {"authed": True, "kind": ident[0], "email": ident[1], "mode": settings.AUTH_MODE}
