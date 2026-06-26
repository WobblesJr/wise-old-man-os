"""Refresh service — pulls from adapters and writes cached panels into SQLite.

In production this is what the Hermes cron jobs call on a schedule. Here it runs
once at startup (and on demand via POST /api/refresh) so read endpoints always
have data. Scope-aware: caches personal + work slices.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from . import db
from . import risk
from . import chaser
from . import warboard
from .adapters import get_adapters
from .mock import mock_data as M

SCOPES = ("personal", "work")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def refresh_all() -> dict:
    """Pull everything from adapters into the panel cache + base tables."""
    from .routers import agent as _agent
    _agent.load_priorities_from_file()   # pick up any priorities.json edits (Hermes-owned), validated
    a = get_adapters()
    ts = _now()
    counts = {}

    # --- scoped panels ---
    for scope in SCOPES:
        # stamp the deadline-defense risk verdict on every task (single source of urgency)
        tasks = risk.stamp_tasks(a.sheet.list_tasks(scope))
        tasks_by_id = {t["id"]: t for t in tasks}

        # rank suggestions by the SAME risk engine (hero shows the most-at-risk first)
        suggestions = sorted(
            M.scope_get(M.SUGGESTIONS, scope),
            key=lambda s: risk.suggestion_score(s, tasks_by_id),
            reverse=True,
        )

        db.put_panel("suggestions", scope, suggestions, ts)
        db.put_panel("today", scope, a.google.today(scope), ts)
        db.put_panel("inbox", scope, a.google.inbox(scope), ts)
        db.put_panel("tasks", scope, tasks, ts)
        db.put_panel("task_counts", scope, M.task_counts(scope), ts)
        db.put_panel("memory", scope, a.memory.recent(scope), ts)
        db.put_panel("approvals", scope, M.scope_get(M.APPROVALS, scope), ts)
        db.put_panel("drive_files", scope, a.drive.list_files(scope), ts)

    # --- global panels ---
    db.put_panel("usage", "both", M.USAGE, ts)
    db.put_panel("connections", "both", M.CONNECTIONS, ts)
    db.put_panel("scheduled_jobs", "both", M.SCHEDULED_JOBS, ts)
    db.put_panel("skills", "both", M.SKILLS, ts)
    db.put_panel("feeds", "both", a.feeds.all_feeds(), ts)

    # --- base tables (approvals/drafts/usage/tasks) for non-panel queries ---
    with db.get_conn() as conn:
        conn.execute("DELETE FROM approvals WHERE origin='seed'")  # keep chaser-generated chases
        conn.execute("DELETE FROM drafts")
        conn.execute("DELETE FROM tasks")
        conn.execute("DELETE FROM usage")

        for scope in SCOPES:
            for ap in M.scope_get(M.APPROVALS, scope):
                # stamp lifecycle fields the chaser/ledger rely on (Phase-2 ready)
                ap = {**ap, "created_at": ap.get("created_at", ts),
                      "last_nudged": ap.get("last_nudged"), "nudge_count": ap.get("nudge_count", 0)}
                conn.execute(
                    "INSERT INTO approvals(id,scope,kind,title,summary,target,draft_id,risk,status,data)"
                    " VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (ap["id"], scope, ap["kind"], ap["title"], ap["summary"], ap["target"],
                     ap.get("draft_id"), ap.get("risk"), ap.get("status", "pending"), json.dumps(ap)),
                )
            for t in a.sheet.list_tasks(scope):
                conn.execute(
                    "INSERT OR REPLACE INTO tasks(id,scope,description,bang,start,followup,due,owner,"
                    "ball_in_court,category,subcategory,action,status,data) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (t["id"], scope, t["description"], t.get("bang"), t.get("start"), t.get("followup"),
                     t.get("due"), t.get("owner"), t.get("ball_in_court"), t.get("category"),
                     t.get("subcategory"), t.get("action"), t.get("status"), json.dumps(t)),
                )
        for d in M.DRAFTS.values():
            conn.execute("INSERT INTO drafts(id,kind,data) VALUES(?,?,?)",
                         (d["id"], d["kind"], json.dumps(d)))
        for u in M.USAGE["ledger"]:
            conn.execute(
                "INSERT INTO usage(id,ts,agent,model,tokens,cost_note,scope) VALUES(?,?,?,?,?,?,?)",
                (u["id"], u["ts"], u["agent"], u["model"], u["tokens"], u["cost_note"], u["scope"]),
            )
        counts = {
            "approvals": conn.execute("SELECT COUNT(*) c FROM approvals").fetchone()["c"],
            "tasks": conn.execute("SELECT COUNT(*) c FROM tasks").fetchone()["c"],
            "drafts": conn.execute("SELECT COUNT(*) c FROM drafts").fetchone()["c"],
        }

    # Ball-in-Court chaser: draft escalation nudges for stale balls (idempotent sweep),
    # then rebuild the approvals panels from the DB so chases show on the dashboard tile.
    chase_res = chaser.run_all()
    for scope in SCOPES:
        with db.get_conn() as conn:
            rows = [json.loads(r["data"]) for r in conn.execute(
                "SELECT data FROM approvals WHERE scope=? AND status='pending' ORDER BY origin DESC",
                (scope,)).fetchall()]
        db.put_panel("approvals", scope, rows, ts)

    # Morning War-Board: one risk() pass per scope -> the brief the hero band renders.
    # (Data only; the 6am cron calls /api/warboard/run to fan out to Discord + Memory.)
    for scope in SCOPES:
        db.put_panel("warboard", scope, warboard.build(scope), ts)

    counts["chaser"] = chase_res
    return {"ok": True, "refreshed_at": ts, "counts": counts}
