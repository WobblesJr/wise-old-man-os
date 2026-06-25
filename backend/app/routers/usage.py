"""Usage-ledger endpoint — token volume + Max plan-usage."""
from __future__ import annotations

import json

from fastapi import APIRouter

from .. import db

router = APIRouter(prefix="/api", tags=["usage"])


@router.get("/usage")
def usage():
    p = db.get_panel("usage", "both")
    summary = p["data"] if p else {}
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT id, ts, agent, model, tokens, cost_note, scope FROM usage ORDER BY ts DESC"
        ).fetchall()
    ledger = [dict(r) for r in rows] or summary.get("ledger", [])
    return {
        "plan": summary.get("plan"),
        "plan_usage_pct": summary.get("plan_usage_pct"),
        "window_resets_in": summary.get("window_resets_in"),
        "tokens_today": summary.get("tokens_today"),
        "tokens_week": summary.get("tokens_week"),
        "by_day": summary.get("by_day", []),
        "ledger": ledger,
    }
