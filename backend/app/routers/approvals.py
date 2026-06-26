"""Approvals + drafts. Decisions are STUBBED — they never send/write for real."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Query, HTTPException

from .. import db, cache, chaser
from ..adapters import get_adapters
from ..models import ApproveIn

router = APIRouter(prefix="/api", tags=["approvals"])


@router.get("/approvals")
def list_approvals(scope: str = Query("personal", pattern="^(personal|work)$")):
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT data FROM approvals WHERE scope=? AND status='pending'", (scope,)
        ).fetchall()
    return {"scope": scope, "approvals": [json.loads(r["data"]) for r in rows]}


@router.get("/drafts/{draft_id}")
def get_draft(draft_id: str):
    with db.get_conn() as conn:
        row = conn.execute("SELECT data FROM drafts WHERE id=?", (draft_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="draft not found")
    return json.loads(row["data"])


@router.post("/approvals/decide")
def decide(payload: ApproveIn):
    """Approve/reject an approval. STUB: routes through the adapter in mock mode,
    which performs a no-op 'send'. Nothing leaves the machine."""
    with db.get_conn() as conn:
        row = conn.execute("SELECT scope, data FROM approvals WHERE id=?", (payload.approval_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="approval not found")
        ap = json.loads(row["data"])
        scope = row["scope"]

        result = {"ok": True, "mock": True, "decision": payload.decision, "approval": ap["id"]}
        if payload.decision == "approve":
            a = get_adapters()
            kind = ap["kind"]
            if kind == "email_send" and ap.get("draft_id"):
                draft_row = conn.execute("SELECT data FROM drafts WHERE id=?",
                                         (ap["draft_id"],)).fetchone()
                draft = json.loads(draft_row["data"]) if draft_row else {}
                result["effect"] = a.google.send_email(draft)        # mock no-op
                if ap.get("origin") == "chaser":
                    # advance the chase: bump nudge count + re-arm follow-up (the only place it moves)
                    result["chase"] = chaser.on_chase_approved(conn, scope, ap)
            elif kind == "calendar_create":
                result["effect"] = a.google.create_calendar_event({"title": ap["title"]})
            elif kind == "sheet_write":
                # SHEET-WRITE SPINE: actually route through the SheetTasks adapter
                # (mock append/update in mock mode — the live adapter swaps in unchanged).
                tgt = ap.get("effect_target") or {}
                task_id = tgt.get("task_id")
                patch = tgt.get("patch") or {}
                if task_id and patch:
                    result["effect"] = a.sheet.update_task(scope, task_id, patch)
                else:
                    result["effect"] = {"ok": False, "mock": True,
                                        "note": "sheet_write approval missing effect_target"}
            elif kind == "schedule_post":
                result["effect"] = a.discord.post(ap.get("target", "#general"), ap["summary"])
            else:
                result["effect"] = {"ok": True, "mock": True, "note": f"No-op for kind={kind}"}

        new_status = "approved" if payload.decision == "approve" else "rejected"
        conn.execute("UPDATE approvals SET status=? WHERE id=?", (new_status, ap["id"]))
        conn.execute(
            "INSERT INTO actions_log(kind, ref, scope, result, created_at) VALUES(?,?,?,?,?)",
            (f"approval:{payload.decision}", ap["id"], scope,
             json.dumps(result), datetime.now(timezone.utc).isoformat(timespec="seconds")),
        )

    # If we actually changed the sheet (direct write or a chase re-arming a follow-up),
    # re-cache so dashboards reflect it now. (Outside the block above so it's committed.)
    if payload.decision == "approve" and (
        (ap.get("kind") == "sheet_write" and result.get("effect", {}).get("ok"))
        or result.get("chase", {}).get("ok")
    ):
        cache.refresh_all()
    return result
