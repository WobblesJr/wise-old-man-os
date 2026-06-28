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
from ..models import AgentSignalIn, ConsoleMessageIn, PriorityIn

router = APIRouter(prefix="/api/agent", tags=["agent"])
console_router = APIRouter(prefix="/api/console", tags=["console"])

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


@console_router.post("/message")
async def post_console(msg: ConsoleMessageIn):
    """Write one line into the shared multi-agent console and broadcast it to live clients.

    No auto-reply: real agents answer by POSTing their own lines (see tools/console_worker.py,
    which a live agent runs to watch this console and reply). That keeps the chat honest — a reply
    only appears when an actual agent is connected and responding.
    """
    now = _now()
    with db.get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO console_messages(ts,scope,agent,to_agent,text) VALUES(?,?,?,?,?)",
            (now, msg.scope, msg.agent, msg.to_agent, msg.text))
        mid = cur.lastrowid
    rec = {"id": mid, "ts": now, "scope": msg.scope, "agent": msg.agent,
           "to_agent": msg.to_agent, "text": msg.text}
    await _broadcast({"type": "console_message", "msg": rec})
    return {"ok": True, "msg": rec}


@console_router.get("/messages")
def list_console(scope: str = Query("work"), limit: int = 40):
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT id, ts, scope, agent, to_agent, text FROM console_messages "
            "ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return {"messages": [dict(r) for r in reversed(rows)]}


@router.post("/priority")
async def set_priority(p: PriorityIn):
    """Hermes assigns/updates a task's P0..P4 priority (overlay, not the sheet)."""
    with db.get_conn() as conn:
        conn.execute(
            "INSERT INTO task_priorities(task_id,scope,level,source,why,ts) VALUES(?,?,?, 'hermes',?,?) "
            "ON CONFLICT(task_id,scope) DO UPDATE SET level=excluded.level, source='hermes', "
            "why=excluded.why, ts=excluded.ts",
            (p.task_id, p.scope, p.level, p.why, _now()))
    sync_priorities_to_file()        # mirror to the durable vault file
    rec = {"task_id": p.task_id, "scope": p.scope, "level": p.level, "source": "hermes", "why": p.why}
    await _broadcast({"type": "priority", "priority": rec})
    return {"ok": True, "priority": rec}


def get_priorities(scope: str) -> dict:
    """task_id -> {level, source, why} for Hermes-assigned priorities in this scope."""
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT task_id, level, source, why FROM task_priorities WHERE scope=?", (scope,)).fetchall()
    return {r["task_id"]: {"level": r["level"], "source": r["source"], "why": r["why"]} for r in rows}


# --- Priority round-trip with the vault file (Milestone 3) ---------------------------- #
def _priorities_file():
    from pathlib import Path
    from ..config import settings
    return Path(settings.BACKEND_DIR) / "data" / "vault" / "overlay" / "priorities.json"


def sync_priorities_to_file() -> None:
    """Mirror the DB overlay → overlay/priorities.json (so the file is the durable truth)."""
    try:
        with db.get_conn() as conn:
            rows = conn.execute("SELECT task_id, scope, level, source, why, ts FROM task_priorities").fetchall()
        data = {r["task_id"]: {"scope": r["scope"], "level": r["level"], "source": r["source"],
                               "why": r["why"], "ts": r["ts"]} for r in rows}
        p = _priorities_file(); p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


def load_priorities_from_file() -> None:
    """Read overlay/priorities.json → DB (Hermes can edit the file directly). Validates 0..4.
    An empty/invalid file NEVER wipes live priorities (it just no-ops), and we never delete."""
    p = _priorities_file()
    if not p.exists():
        return
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return
    if not isinstance(data, dict) or not data:
        return
    with db.get_conn() as conn:
        for tid, v in data.items():
            try:
                lvl = int(v.get("level"))
            except (TypeError, ValueError):
                continue
            if lvl < 0 or lvl > 4:
                continue
            conn.execute(
                "INSERT INTO task_priorities(task_id,scope,level,source,why,ts) VALUES(?,?,?,?,?,?) "
                "ON CONFLICT(task_id,scope) DO UPDATE SET level=excluded.level, source=excluded.source, "
                "why=excluded.why, ts=excluded.ts",
                (tid, v.get("scope", "work"), lvl, v.get("source", "hermes"), v.get("why"), v.get("ts")))


def seed_priorities_if_empty() -> None:
    """Seed a few Hermes-decided priorities so the overlay is populated (mock)."""
    with db.get_conn() as conn:
        if conn.execute("SELECT COUNT(*) c FROM task_priorities").fetchone()["c"]:
            return
        seeds = [
            ("w-t1", "work", 4, "RFI blocks the L2 rough-in sequence — top of the stack"),
            ("w-t4", "work", 4, "Manpower deliverable due in 3d and gates the crew plan"),
            ("w-t2", "work", 3, "GC response drives schedule recovery"),
            ("p-t4", "personal", 3, "Quarterly taxes — hard external deadline"),
            ("p-t1", "personal", 2, "Passport has runway but is trip-critical"),
        ]
        for tid, scope, lvl, why in seeds:
            conn.execute("INSERT INTO task_priorities(task_id,scope,level,source,why,ts) "
                         "VALUES(?,?,?, 'hermes',?,?)", (tid, scope, lvl, why, _now()))


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
