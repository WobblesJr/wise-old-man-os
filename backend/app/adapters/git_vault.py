"""GitVaultStore — durable, git-backed task store (the buildable-now storage slice).

Source of truth = markdown tables under a git `vault/` (GitHub + Obsidian friendly). The
website reads/writes these files for fast local manipulation; each write commits to the
vault repo. `push` is stubbed for now (Hermes owns remote sync later). Same interface as
MockSheetTasks so routers/cache don't change.

Layout (under backend/data/vault/, its own git repo):
  tasks/personal.md, tasks/work.md   — one GFM table per scope (id + the sheet columns)
  overlay/priorities.json            — P0..P4 overlay mirror (Hermes-owned)
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ..config import settings
from ..mock import mock_data as M
from .. import qc
from .sheet_tasks import COLUMNS  # single-sourced column contract

# File table columns: id first, then the sheet columns in order.
_KEYS = [k for k, _ in COLUMNS]
_HEADERS = ["id"] + [h for _, h in COLUMNS]


def _vault_dir() -> Path:
    return Path(settings.BACKEND_DIR) / "data" / "vault"


def _git(args: list[str], cwd: Path) -> tuple[int, str]:
    try:
        p = subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True, text=True, timeout=20)
        return p.returncode, (p.stdout + p.stderr).strip()
    except Exception as e:  # git missing / timeout — degrade gracefully
        return 1, str(e)


def _esc(v) -> str:
    return str(v if v is not None else "").replace("|", "\\|").replace("\n", " ")


def _serialize(tasks: list[dict]) -> str:
    head = "| " + " | ".join(_HEADERS) + " |"
    sep = "| " + " | ".join(["---"] * len(_HEADERS)) + " |"
    lines = [head, sep]
    for t in tasks:
        # the '!' column is left blank in the file — priority is a derived overlay
        cells = [_esc(t.get("id"))] + [("" if k == "bang" else _esc(t.get(k, ""))) for k in _KEYS]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def _parse(md: str) -> list[dict]:
    out = []
    for ln in md.splitlines():
        ln = ln.strip()
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if not cells or cells[0] in ("id", "---") or set(cells[0]) == {"-"}:
            continue
        if len(cells) < len(_HEADERS):
            cells += [""] * (len(_HEADERS) - len(cells))
        row = {"id": cells[0]}
        for i, k in enumerate(_KEYS, start=1):
            row[k] = cells[i]
        out.append(row)
    return out


class GitVaultStore:
    """Reads/writes vault/tasks/*.md; commits on write (push stubbed)."""

    COLUMNS = [h for _, h in COLUMNS]

    def __init__(self) -> None:
        self.dir = _vault_dir()
        ensure_vault()  # seed + git init on first use
        self._seq = 5000

    def _file(self, scope: str) -> Path:
        return self.dir / "tasks" / f"{scope}.md"

    def list_tasks(self, scope: str) -> list[dict]:
        f = self._file(scope)
        return _parse(f.read_text(encoding="utf-8")) if f.exists() else []

    def _write(self, scope: str, tasks: list[dict], msg: str) -> str:
        f = self._file(scope)
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(_serialize(tasks), encoding="utf-8")
        _git(["add", "-A"], self.dir)
        code, out = _git(["commit", "-m", msg], self.dir)
        # push is intentionally NOT done here (Hermes owns remote sync) — see runbook.
        return "committed" if code == 0 else "nochange"

    def add_task(self, scope: str, task: dict) -> dict:
        self._seq += 1
        task = qc.clean(task)            # last-line sanitize (idempotent after the router gate)
        rows = self.list_tasks(scope)
        row = {"id": f"{scope[0]}-t{self._seq}", "bang": task.get("bang", ""),
               "description": task.get("description", "(untitled)"),
               "start": task.get("start", ""), "followup": task.get("followup", ""),
               "due": task.get("due", ""), "owner": task.get("owner", "Gavin"),
               "ball_in_court": task.get("ball_in_court", "Me"),
               "category": task.get("category", "Inbox"), "subcategory": task.get("subcategory", ""),
               "action": task.get("action", "action"), "status": task.get("status", "not_started")}
        rows.insert(0, row)
        state = self._write(scope, rows, f"web: add {row['id']} {row['description'][:40]}")
        return {"ok": True, "mock": False, "committed": state, "task": row}

    def update_task(self, scope: str, task_id: str, patch: dict) -> dict:
        patch = qc.clean(patch)          # last-line sanitize
        rows = self.list_tasks(scope)
        for r in rows:
            if r["id"] == task_id:
                r.update({k: v for k, v in patch.items() if k in r})
                state = self._write(scope, rows, f"web: update {task_id} " +
                                    ",".join(f"{k}={v}" for k, v in patch.items()))
                return {"ok": True, "mock": False, "committed": state, "task": r}
        return {"ok": False, "mock": False, "error": "not_found", "task_id": task_id}


def ensure_vault() -> None:
    """Seed the vault from mock data + git init on first run. Idempotent."""
    d = _vault_dir()
    (d / "tasks").mkdir(parents=True, exist_ok=True)
    (d / "overlay").mkdir(parents=True, exist_ok=True)
    if not (d / ".git").exists():
        _git(["init", "-q"], d)
        _git(["config", "user.email", "wom@local"], d)
        _git(["config", "user.name", "Wise Old Man"], d)
    seeded = False
    for scope in ("personal", "work"):
        f = d / "tasks" / f"{scope}.md"
        if not f.exists():
            f.write_text(_serialize(M.TASKS.get(scope, [])), encoding="utf-8")
            seeded = True
    pj = d / "overlay" / "priorities.json"
    if not pj.exists():
        pj.write_text(json.dumps({}, indent=2), encoding="utf-8")
        seeded = True
    if seeded:
        _git(["add", "-A"], d)
        _git(["commit", "-m", "seed: vault from mock"], d)


# TODO(live): GitVaultStore.push() → push to the GitHub remote; two-way reconcile with the
# Google Sheet (LiveSheetTasks); load overlay/priorities.json into task_priorities each refresh.
