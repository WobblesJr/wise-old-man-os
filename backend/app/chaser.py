"""Ball-in-Court chaser — the deadline-defense follow-up engine.

When the risk() scorer flips a ball you're WAITING ON (ball_in_court != "Me") into
amber/red, the chaser drafts the next nudge in an escalation ladder and surfaces it
as an approval. Rules from the roadmap, enforced here:

  - Outbound email is structurally locked to a human tap (it's an `email_send` approval;
    the chaser only ever DRAFTS).
  - The follow-up date is re-armed ONLY when the approval fires (see approvals.decide),
    never at draft time — so a rejected chase can't silently re-date the row.
  - Re-nudges are throttled: advancing the ladder requires the previous nudge to have
    been sent AND the task to have gone stale again. A visible "nudged ×N" counter +
    ladder level ride on the approval.
"""
from __future__ import annotations

import json

from . import db, risk
from .adapters import get_adapters

SCOPES = ("personal", "work")

LADDER = [
    {"level": 0, "label": "polite nudge"},
    {"level": 1, "label": "firmer + CC super"},
    {"level": 2, "label": "escalation to super"},
]


def _eligible(t: dict) -> bool:
    """Waiting on someone else, not done, and the clock is pressing."""
    if t.get("ball_in_court") == "Me":
        return False
    if t.get("status") == "completed":
        return False
    return t.get("risk", {}).get("band") in ("amber", "red")


def _draft(task: dict, level: int) -> dict:
    who = task.get("ball_in_court", "them")
    desc = task.get("description", "the item")
    due = task.get("due") or "soon"
    if level <= 0:
        return {"id": None, "kind": "email", "to": who, "subject": f"Quick nudge: {desc}",
                "body": f"Hi {who} — checking in on \"{desc}\" (due {due}). Anything you need from "
                        f"me to keep it moving? Thanks!"}
    if level == 1:
        return {"id": None, "kind": "email", "to": who, "cc": "super", "subject": f"2nd follow-up: {desc}",
                "body": f"{who}, following up again on \"{desc}\" — due {due} and now at risk. CC'ing my "
                        f"super for visibility. Can you confirm status today?"}
    return {"id": None, "kind": "email", "to": "super", "cc": who, "subject": f"Escalation: {desc} stalled",
            "body": f"Flagging \"{desc}\" (owed by {who}, due {due}) — nudged twice with no resolution; "
                    f"it's now threatening the date. Recommend we escalate. Paper trail attached."}


def run_all() -> dict:
    """Idempotent sweep across both scopes. Safe to call every refresh."""
    a = get_adapters()
    created = advanced = withdrawn = 0

    with db.get_conn() as conn:
        for scope in SCOPES:
            tasks = risk.stamp_tasks(a.sheet.list_tasks(scope))
            by_id = {t["id"]: t for t in tasks}

            # 1) Withdraw pending chases whose task is no longer eligible (e.g. you completed it).
            for row in conn.execute("SELECT * FROM chases WHERE scope=? AND status='pending'", (scope,)).fetchall():
                t = by_id.get(row["task_id"])
                if not t or not _eligible(t):
                    conn.execute("DELETE FROM approvals WHERE id=?", (row["approval_id"],))
                    conn.execute("DELETE FROM chases WHERE task_id=? AND scope=?", (row["task_id"], scope))
                    withdrawn += 1

            # 2) For each eligible task, ensure a chase approval exists at the right ladder level.
            for t in tasks:
                if not _eligible(t):
                    continue
                tid = t["id"]
                row = conn.execute("SELECT * FROM chases WHERE task_id=? AND scope=?", (tid, scope)).fetchone()
                if row and row["status"] == "pending":
                    continue  # already awaiting your tap — don't duplicate
                if row and row["status"] == "approved":
                    # Already nudged. Only advance the ladder once it goes STALE AGAIN
                    # (the re-armed follow-up has lapsed) — not just because the due date is near.
                    stale_again = (t.get("risk", {}).get("days_past_followup") or -999) > 0
                    if not stale_again:
                        continue
                    level = min(row["ladder_level"] + 1, len(LADDER) - 1)
                    nudges = row["nudge_count"]
                    advanced += 1
                else:
                    level = 0
                    nudges = 0
                    created += 1

                apid = f"chase-{scope[0]}-{tid}"
                draft_id = apid + "-draft"
                draft = _draft(t, level)
                draft["id"] = draft_id
                label = LADDER[level]["label"]
                ap = {
                    "id": apid, "kind": "email_send",
                    "title": f"Chase {t['ball_in_court']} — {t['description'][:42]}",
                    "summary": f"Auto-drafted {label} (step {level + 1}/3). Re-arms follow-up only on approve.",
                    "target": draft.get("to"), "draft_id": draft_id,
                    "risk": "medium" if level >= 1 else "low", "status": "pending",
                    "origin": "chaser", "chase_task_id": tid, "ladder_level": level,
                    "nudge_count": nudges, "effect_followup_days": 3,
                }
                conn.execute(
                    "INSERT OR REPLACE INTO approvals(id,scope,kind,title,summary,target,draft_id,risk,status,origin,data)"
                    " VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    (apid, scope, ap["kind"], ap["title"], ap["summary"], ap["target"], draft_id,
                     ap["risk"], "pending", "chaser", json.dumps(ap)),
                )
                conn.execute("INSERT OR REPLACE INTO drafts(id,kind,data) VALUES(?,?,?)",
                             (draft_id, "email", json.dumps(draft)))
                conn.execute(
                    "INSERT INTO chases(task_id,scope,nudge_count,ladder_level,last_nudged,status,approval_id)"
                    " VALUES(?,?,?,?,?,?,?) ON CONFLICT(task_id,scope) DO UPDATE SET "
                    "ladder_level=excluded.ladder_level, status='pending', approval_id=excluded.approval_id",
                    (tid, scope, nudges, level, None, "pending", apid),
                )

    return {"ok": True, "created": created, "advanced": advanced, "withdrawn": withdrawn}


def on_chase_approved(conn, scope: str, ap: dict) -> dict:
    """Called from approvals.decide when a chase email_send is approved.
    Marks the nudge sent, bumps the counter, and RE-ARMS the follow-up (the one place
    the follow-up date moves) so the task stops being stale until the new window lapses."""
    tid = ap.get("chase_task_id")
    days = ap.get("effect_followup_days", 3)
    new_followup = risk.today().fromordinal(risk.today().toordinal() + days).isoformat()

    a = get_adapters()
    a.sheet.update_task(scope, tid, {"followup": new_followup})  # re-arm via the sheet-write spine

    conn.execute(
        "UPDATE chases SET status='approved', nudge_count=nudge_count+1, last_nudged=? "
        "WHERE task_id=? AND scope=?",
        (risk.today().isoformat(), tid, scope),
    )
    row = conn.execute("SELECT nudge_count FROM chases WHERE task_id=? AND scope=?", (tid, scope)).fetchone()
    return {"ok": True, "mock": True, "chased": tid, "nudge_count": row["nudge_count"] if row else 1,
            "followup_rearmed_to": new_followup,
            "note": "Mock nudge — drafted + logged; nothing actually emailed."}
