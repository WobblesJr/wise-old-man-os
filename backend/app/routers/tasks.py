"""Task endpoints — list (filterable), quick-add (writes via sheet adapter), patch."""
from __future__ import annotations

from fastapi import APIRouter, Query

from .. import cache
from ..adapters import get_adapters
from ..models import QuickAddTask, TaskPatch

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# filter -> matches the UI tabs: All / Mine / each action type
_ACTION_TYPES = {"action", "wait", "hold", "read", "event"}


@router.get("")
def list_tasks(
    scope: str = Query("personal", pattern="^(personal|work)$"),
    filter: str = Query("all"),
):
    a = get_adapters()
    rows = a.sheet.list_tasks(scope)
    f = filter.lower()
    if f == "mine":
        rows = [r for r in rows if r.get("ball_in_court") == "Me" and r["status"] != "completed"]
    elif f in _ACTION_TYPES:
        rows = [r for r in rows if r.get("action") == f]
    return {"scope": scope, "filter": f, "count": len(rows), "tasks": rows}


@router.post("")
def quick_add(payload: QuickAddTask):
    """Quick-add bar → writes a row via the SheetTasks adapter (mock append)."""
    a = get_adapters()
    res = a.sheet.add_task(payload.scope, payload.model_dump(exclude={"scope"}))
    cache.refresh_all()  # re-cache so dashboards reflect it immediately
    return res


@router.patch("/{task_id}")
def patch_task(task_id: str, patch: TaskPatch,
               scope: str = Query("personal", pattern="^(personal|work)$")):
    a = get_adapters()
    res = a.sheet.update_task(scope, task_id, patch.model_dump(exclude_none=True))
    cache.refresh_all()
    return res
