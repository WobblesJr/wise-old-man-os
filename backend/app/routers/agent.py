"""The HERMES layer — agent-authored signals + a real-time SSE stream.

This is how Hermes (the LLM orchestrator in the Ubuntu VM) interacts with the board:
it POSTs beliefs/decisions and they appear here LIVE, tagged as Hermes, distinct from
the deterministic rules engine (risk/chaser/warboard). The dashboard subscribes to
/api/agent/stream and renders signals the instant they land.
"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse

from .. import db
from ..models import AgentSignalIn

router = APIRouter(prefix="/api/agent", tags=["agent"])

# In-process pub/sub. Each SSE client gets a Queue; POSTs broadcast to all.
_subscribers: set[asyncio.Queue] = set()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


async def _broadcast(event: dict) -> None:
    for q in list(_subscribers):
        try:
            q.put_nowait(event)
        except Exception:
            _subscribers.discard(q)


def _row_to_signal(r) -> dict:
    return {k: r[k] for k in ("id", "ts", "scope", "kind", "title", "body",
                              "target_task_id", "confidence", "provenance", "status")}


@router.post("/signal")
async def post_signal(sig: AgentSignalIn):
    """Hermes posts a belief/decision. Stored + broadcast to live dashboards."""
    now = _now()
    with db.get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO agent_signals(ts,scope,kind,title,body,target_task_id,confidence,provenance,status)"
            " VALUES(?,?,?,?,?,?,?,?, 'active')",
            (now, sig.scope, sig.kind, sig.title, sig.body, sig.target_task_id,
             sig.confidence, sig.provenance or "hermes"),
        )
        sid = cur.lastrowid
    rec = {"id": sid, "ts": now, "scope": sig.scope, "kind": sig.kind, "title": sig.title,
           "body": sig.body, "target_task_id": sig.target_task_id, "confidence": sig.confidence,
           "provenance": sig.provenance or "hermes", "status": "active"}
    await _broadcast({"type": "agent_signal", "signal": rec})
    return {"ok": True, "signal": rec}


@router.get("/signals")
def list_signals(scope: str = Query("personal", pattern="^(personal|work|both)$")):
    with db.get_conn() as conn:
        if scope == "both":
            rows = conn.execute("SELECT * FROM agent_signals WHERE status='active' ORDER BY id DESC").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM agent_signals WHERE status='active' AND scope=? ORDER BY id DESC",
                (scope,)).fetchall()
    return {"scope": scope, "signals": [_row_to_signal(r) for r in rows]}


@router.post("/signal/{sid}/{decision}")
async def resolve_signal(sid: int, decision: str):
    """Dismiss or mark-acted a signal (decision in {dismiss, act})."""
    status = "acted" if decision == "act" else "dismissed"
    with db.get_conn() as conn:
        conn.execute("UPDATE agent_signals SET status=? WHERE id=?", (status, sid))
    await _broadcast({"type": "agent_resolve", "id": sid, "status": status})
    return {"ok": True, "id": sid, "status": status}


@router.get("/stream")
async def stream(request: Request, scope: str = Query("both")):
    """SSE stream of Hermes signals (+ keepalives). The dashboard's live wire."""
    q: asyncio.Queue = asyncio.Queue()
    _subscribers.add(q)

    async def gen():
        try:
            yield "event: ping\ndata: connected\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    ev = await asyncio.wait_for(q.get(), timeout=15)
                except asyncio.TimeoutError:
                    yield "event: ping\ndata: keepalive\n\n"
                    continue
                sig = ev.get("signal")
                if ev.get("type") == "agent_signal" and scope != "both" and sig and sig["scope"] != scope:
                    continue
                yield f"data: {json.dumps(ev)}\n\n"
        finally:
            _subscribers.discard(q)

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


def seed_if_empty() -> None:
    """Seed a couple of Hermes beliefs so the layer isn't empty on first boot (mock)."""
    with db.get_conn() as conn:
        n = conn.execute("SELECT COUNT(*) c FROM agent_signals").fetchone()["c"]
        if n:
            return
        seeds = [
            ("work", "reprioritize", "Bank the manpower schedule before the RFI today",
             "GC rarely replies before noon — you'll be blocked on the RFI anyway. Lock the L3 "
             "manpower deliverable in your morning window while you wait, then chase the GC after lunch.",
             "w-t4", 72),
            ("personal", "insight", "Your week is front-loaded — guard Thursday morning",
             "4 of 5 hard dates land Mon–Wed. Thursday's only clear block is the recovery window; "
             "don't let a meeting eat it.", None, 64),
        ]
        for scope, kind, title, body, tid, conf in seeds:
            conn.execute(
                "INSERT INTO agent_signals(ts,scope,kind,title,body,target_task_id,confidence,provenance,status)"
                " VALUES(?,?,?,?,?,?,?, 'hermes','active')",
                (_now(), scope, kind, title, body, tid, conf),
            )
