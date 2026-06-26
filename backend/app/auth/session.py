"""Stateless signed session cookie (stdlib only — no extra deps).

Token = base64(payload_json).base64(hmac_sha256(payload, SESSION_SECRET)). Single-user, so
no sessions table; the cookie carries {email, iat} and is verified on every request.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Optional

from ..config import settings

COOKIE = "wom_session"
MAX_AGE = 60 * 60 * 24 * 30  # 30 days (PWA convenience)


def _b64e(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def _b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _sig(payload_b64: str) -> str:
    mac = hmac.new(settings.SESSION_SECRET.encode(), payload_b64.encode(), hashlib.sha256)
    return _b64e(mac.digest())


def sign(email: str) -> str:
    payload = _b64e(json.dumps({"email": email, "iat": int(time.time())}).encode())
    return f"{payload}.{_sig(payload)}"


def verify(token: Optional[str]) -> Optional[dict]:
    if not token or "." not in token:
        return None
    payload, sig = token.rsplit(".", 1)
    if not hmac.compare_digest(sig, _sig(payload)):
        return None
    try:
        data = json.loads(_b64d(payload))
    except Exception:
        return None
    if int(time.time()) - int(data.get("iat", 0)) > MAX_AGE:
        return None
    return data
