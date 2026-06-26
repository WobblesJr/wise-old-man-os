"""Identity resolution shared by the middleware and /auth/me.

Two credentials, one check: a browser session (Google login / Cloudflare Access email) OR a
Hermes service bearer token. Plus a localhost dev-bypass so local dev needs no login.
"""
from __future__ import annotations

import secrets
from typing import Optional, Tuple

from ..config import settings
from .session import verify, COOKIE

OPEN_PATHS = {"/api/health", "/favicon.ico"}
OPEN_PREFIXES = ("/auth/",)


def is_open(path: str) -> bool:
    return path in OPEN_PATHS or any(path.startswith(p) for p in OPEN_PREFIXES)


def is_loopback(request) -> bool:
    host = request.client.host if request.client else ""
    return host in ("127.0.0.1", "::1", "localhost")


def _bearer_ok(request) -> bool:
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        tok = auth[7:].strip()
        real = settings.SERVICE_TOKEN and not settings.SERVICE_TOKEN.startswith("__STUB")
        return bool(real) and secrets.compare_digest(tok, settings.SERVICE_TOKEN)
    return False


def resolve_identity(request) -> Optional[Tuple[str, Optional[str]]]:
    """('machine', None) | ('human', email) | None."""
    if _bearer_ok(request):
        return ("machine", None)
    cf = (request.headers.get("cf-access-authenticated-user-email") or "").lower()
    if cf and cf in settings.ALLOWED_EMAILS:
        return ("human", cf)
    data = verify(request.cookies.get(COOKIE))
    if data and str(data.get("email", "")).lower() in settings.ALLOWED_EMAILS:
        return ("human", data["email"])
    if settings.AUTH_DEV_BYPASS and settings.AUTH_MODE != "cloudflare" and is_loopback(request):
        return ("human", "dev@localhost")
    return None
