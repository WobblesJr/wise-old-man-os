"""Quick-capture endpoint — note → captures table (+ memory adapter), or → task."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter

from .. import db, cache
from ..adapters import get_adapters
from ..models import CaptureIn

router = APIRouter(prefix="/api", tags=["capture"])


@router.post("/capture")
def capture(payload: CaptureIn):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    a = get_adapters()

    with db.get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO captures(scope, text, kind, created_at) VALUES(?,?,?,?)",
            (payload.scope, payload.text, payload.kind, now),
        )
        capture_id = cur.lastrowid

    result = {"ok": True, "mock": True, "capture_id": capture_id, "kind": payload.kind}

    if payload.kind == "task":
        # Promote the note straight into a task via the sheet adapter.
        res = a.sheet.add_task(payload.scope, {"description": payload.text})
        result["task"] = res.get("task")
        cache.refresh_all()
    else:
        # Default: also drop it into memory (Obsidian mock).
        mem = a.memory.capture(payload.scope, payload.text, payload.tag)
        result["memory"] = mem.get("note")
        cache.refresh_all()

    return result


@router.get("/captures")
def list_captures(scope: str = "personal", limit: int = 20):
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT id, scope, text, kind, created_at FROM captures "
            "WHERE scope=? ORDER BY id DESC LIMIT ?", (scope, limit),
        ).fetchall()
    return {"scope": scope, "captures": [dict(r) for r in rows]}
