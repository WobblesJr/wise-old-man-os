"""SheetTasks adapter — the 'G-Suite Dashboard' sheet (task source-of-truth).

Column order is taken verbatim from the spec and must match the real sheet:
  ! / Description / Start / Follow-up / Due / Owner / Ball in Court /
  Category / Subcategory / Action / Status
"""
from __future__ import annotations

import copy

from ..mock import mock_data as M

# Maps our task dict keys <-> sheet column headers, in sheet order.
COLUMNS = [
    ("bang", "!"),
    ("description", "Description"),
    ("start", "Start"),
    ("followup", "Follow-up"),
    ("due", "Due"),
    ("owner", "Owner"),
    ("ball_in_court", "Ball in Court"),
    ("category", "Category"),
    ("subcategory", "Subcategory"),
    ("action", "Action"),
    ("status", "Status"),
]


class MockSheetTasks:
    """In-memory mock of the sheet. add/update mutate the process copy so the UI
    reflects quick-adds during a session (resets on restart — it's mock)."""

    COLUMNS = [c[1] for c in COLUMNS]

    def __init__(self) -> None:
        # Deep copy so we don't mutate the canonical mock module.
        self._tasks = copy.deepcopy(M.TASKS)
        self._seq = 1000

    def list_tasks(self, scope: str) -> list[dict]:
        return self._tasks.get(scope, [])

    def add_task(self, scope: str, task: dict) -> dict:
        self._seq += 1
        row = {
            "id": f"{scope[0]}-t{self._seq}",
            "bang": task.get("bang", ""),
            "description": task.get("description", "(untitled)"),
            "start": task.get("start", ""),
            "followup": task.get("followup", ""),
            "due": task.get("due", ""),
            "owner": task.get("owner", "Gavin"),
            "ball_in_court": task.get("ball_in_court", "Me"),
            "category": task.get("category", "Inbox"),
            "subcategory": task.get("subcategory", ""),
            "action": task.get("action", "action"),
            "status": task.get("status", "not_started"),
        }
        self._tasks.setdefault(scope, []).insert(0, row)
        return {"ok": True, "mock": True, "task": row}

    def update_task(self, scope: str, task_id: str, patch: dict) -> dict:
        for r in self._tasks.get(scope, []):
            if r["id"] == task_id:
                r.update({k: v for k, v in patch.items() if k in r})
                return {"ok": True, "mock": True, "task": r}
        return {"ok": False, "mock": True, "error": "not_found", "task_id": task_id}


# --------------------------------------------------------------------------- #
# TODO(live): LiveSheetTasks
#   - Use Sheets API with GSUITE_DASHBOARD_SHEET_ID + GSUITE_DASHBOARD_TAB.
#   - list_tasks(): spreadsheets.values.get(range=f"{tab}!A:K"); map rows via COLUMNS.
#   - add_task(): spreadsheets.values.append(...).  <-- the quick-add write path.
#   - update_task(): batchUpdate / values.update on the matched row.
#   Same method names; select in registry.py. Scopes may be two tabs or a column.
# --------------------------------------------------------------------------- #
