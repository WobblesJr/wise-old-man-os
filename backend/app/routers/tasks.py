"""Task endpoints — list (filterable), quick-add (writes via sheet adapter), patch."""
from __future__ import annotations

from fastapi import APIRouter, Query, HTTPException

from .. import cache, risk, qc
from ..adapters import get_adapters
from ..routers import agent
from ..models import QuickAddTask, TaskPatch

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# filter -> matches the UI tabs: All / Mine / each action type
_ACTION_TYPES = {"action", "wait", "hold", "read", "event"}
# rules fallback for the priority overlay when Hermes hasn't assigned one (P4 highest).
_BAND_TO_PRIO = {"red": 4, "amber": 3, "green": 1, "done": 0}


def _attach_priority(rows: list, scope: str) -> None:
    """Layer the P0..P4 priority on each task: Hermes override, else rules-derived."""
    hermes = agent.get_priorities(scope)
    for r in rows:
        if r["id"] in hermes:
            h = hermes[r["id"]]
            r["priority"] = {"level": h["level"], "source": "hermes", "why": h.get("why")}
        else:
            band = r.get("risk", {}).get("band", "green")
            r["priority"] = {"level": _BAND_TO_PRIO.get(band, 2), "source": "rules",
                             "why": f"derived from risk band: {band}"}


def _sort_rows(rows: list, sort: str) -> list:
    s = (sort or "none").lower()
    if s in ("az", "za"):
        rows = sorted(rows, key=lambda r: (r.get("description") or "").lower(), reverse=(s == "za"))
    elif s in ("prio", "prio_desc"):   # P4 first (highest), tie-break by risk score
        rows = sorted(rows, key=lambda r: (r["priority"]["level"], r.get("risk", {}).get("score", 0)),
                      reverse=True)
    elif s == "prio_asc":
        rows = sorted(rows, key=lambda r: (r["priority"]["level"], r.get("risk", {}).get("score", 0)))
    elif s == "due":
        rows = sorted(rows, key=lambda r: (r.get("due") or "9999-99-99"))
    return rows


@router.get("")
def list_tasks(
    scope: str = Query("personal", pattern="^(personal|work)$"),
    filter: str = Query("all"),
    sort: str = Query("none"),
):
    a = get_adapters()
    rows = risk.stamp_tasks(a.sheet.list_tasks(scope))  # deadline-defense risk on every row
    _attach_priority(rows, scope)
    f = filter.lower()
    if f == "mine":
        rows = [r for r in rows if r.get("ball_in_court") == "Me" and r["status"] != "completed"]
    elif f in _ACTION_TYPES:
        rows = [r for r in rows if r.get("action") == f]
    rows = _sort_rows(rows, sort)
    return {"scope": scope, "filter": f, "sort": sort, "count": len(rows), "tasks": rows}


@router.post("")
def quick_add(payload: QuickAddTask):
    """Quick-add bar → writes a row via the SheetTasks adapter (mock append).
    A user-picked priority is stored in the overlay (not the sheet)."""
    from datetime import datetime, timezone
    from .. import db
    a = get_adapters()
    # QC bouncer: clean/repair the row; refuse what can't be safely fixed.
    g = qc.gate(payload.model_dump(exclude={"scope", "priority"}), partial=False)
    qc.log_qc(payload.scope, "quick_add", g)
    if not g["ok"]:
        raise HTTPException(status_code=422, detail={"error": "qc_blocked", "issues": g["blocks"]})
    res = a.sheet.add_task(payload.scope, g["cleaned"])
    if payload.priority is not None and res.get("task"):
        tid = res["task"]["id"]
        with db.get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO task_priorities(task_id,scope,level,source,why,ts) "
                "VALUES(?,?,?, 'you', 'set at quick-add', ?)",
                (tid, payload.scope, payload.priority,
                 datetime.now(timezone.utc).isoformat(timespec="seconds")))
    cache.refresh_all()  # re-cache so dashboards reflect it immediately
    return res


@router.patch("/{task_id}")
def patch_task(task_id: str, patch: TaskPatch,
               scope: str = Query("personal", pattern="^(personal|work)$")):
    a = get_adapters()
    # QC bouncer on inline grid edits (partial = only the fields being changed).
    g = qc.gate(patch.model_dump(exclude_none=True), partial=True)
    qc.log_qc(scope, "grid_edit", g)
    if not g["ok"]:
        raise HTTPException(status_code=422, detail={"error": "qc_blocked", "issues": g["blocks"]})
    res = a.sheet.update_task(scope, task_id, g["cleaned"])
    cache.refresh_all()
    return res
