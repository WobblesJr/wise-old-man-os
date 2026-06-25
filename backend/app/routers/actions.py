"""Action endpoints — one-tap suggestion actions + schedule. All STUBBED/no-op."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter

from .. import db
from ..adapters import get_adapters
from ..models import ScheduleIn

router = APIRouter(prefix="/api/actions", tags=["actions"])


def _log(kind: str, ref: str, scope: str, result: dict) -> None:
    with db.get_conn() as conn:
        conn.execute(
            "INSERT INTO actions_log(kind, ref, scope, result, created_at) VALUES(?,?,?,?,?)",
            (kind, ref, scope, json.dumps(result),
             datetime.now(timezone.utc).isoformat(timespec="seconds")),
        )


@router.post("/schedule")
def schedule(payload: ScheduleIn):
    """Stub: would create a calendar event. Mock returns a fake link."""
    a = get_adapters()
    res = a.google.create_calendar_event(payload.model_dump())
    _log("schedule", payload.title, payload.scope, res)
    return res


@router.post("/run/{suggestion_ref}")
def run_suggestion(suggestion_ref: str, scope: str = "personal"):
    """One-tap action behind a 'Suggested next step'. Stubbed dispatcher."""
    res = {"ok": True, "mock": True, "ref": suggestion_ref,
           "note": "Mock action executed — nothing left the machine."}
    _log("suggestion_run", suggestion_ref, scope, res)
    return res


@router.get("/log")
def action_log(limit: int = 25):
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT id, kind, ref, scope, result, created_at FROM actions_log "
            "ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["result"] = json.loads(d["result"]) if d.get("result") else None
        out.append(d)
    return {"log": out}
