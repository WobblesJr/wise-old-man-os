"""QC gate — the bouncer in front of every task write.

Deterministic structural validator that runs before any task is saved (grid edit,
quick-add, or a direct vault write). It AUTO-REPAIRS harmless mistakes (a stray `|`
that would shatter a row, embedded newlines, loose whitespace, sloppy dates, enum
casing/synonyms) and BLOCKS anything it can't safely fix (a description that's too
long / clearly holds multiple values, an unknown action/status, an unparseable date),
returning a plain-English reason. Every decision is logged.

This kills the "description bleeding across cells" defect class at the door.
Rulebook is the Python schema below (authoritative); a readable mirror is written to
vault/.wom/schema/tasks.yaml for you/Hermes/Obsidian.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from . import db, risk
from .config import settings

# --- The rulebook: what each column may hold (! priority is validated separately) ---
TASK_SCHEMA = {
    "description":   {"type": "text", "max_len": 200, "required": True},
    "start":         {"type": "date"},
    "followup":      {"type": "date"},
    "due":           {"type": "date"},
    "owner":         {"type": "text", "max_len": 80},
    "ball_in_court": {"type": "text", "max_len": 80},
    "category":      {"type": "text", "max_len": 60},   # free-text for now (per your call)
    "subcategory":   {"type": "text", "max_len": 60},
    "action":        {"type": "enum", "values": ["action", "wait", "hold", "read", "event"]},
    "status":        {"type": "enum", "values": ["not_started", "in_progress", "completed",
                                                 "delegated", "blocked"]},
}

ENUM_SYNONYMS = {
    "action": {"todo": "action", "do": "action", "task": "action", "waiting": "wait",
               "on_hold": "hold", "review": "read", "meeting": "event"},
    "status": {"in_progress": "in_progress", "inprogress": "in_progress", "wip": "in_progress",
               "in_process": "in_progress", "done": "completed", "complete": "completed",
               "finished": "completed", "todo": "not_started", "to_do": "not_started",
               "open": "not_started", "new": "not_started", "delegate": "delegated",
               "assigned": "delegated", "stuck": "blocked", "waiting": "blocked"},
}


def _clean_text(v) -> str:
    s = str(v if v is not None else "")
    s = s.replace("|", "/")           # a pipe would split the markdown row — never allow it
    s = " ".join(s.split())           # collapse newlines/tabs/multi-space, trim
    return s


def _coerce_date(v):
    s = str(v if v is not None else "").strip()
    if not s or s in ("—", "-", "tbd", "TBD"):
        return "", None
    s2 = s.replace(".", "/").replace("-", "/")
    for fmt in ("%Y/%m/%d", "%m/%d/%Y", "%m/%d/%y", "%m/%d"):
        try:
            d = datetime.strptime(s2, fmt)
            if fmt == "%m/%d":
                d = d.replace(year=risk.today().year)
            return d.strftime("%Y-%m-%d"), None
        except ValueError:
            continue
    return None, "use a date like 2026-07-10 or 07/10"


def _clean_enum(v, values, synonyms):
    s = str(v if v is not None else "").strip().lower().replace(" ", "_")
    if not s:
        return "", None
    if s in values:
        return s, None
    if s in synonyms:
        return synonyms[s], None
    return None, "must be one of: " + ", ".join(values)


def gate(data: dict, partial: bool = False) -> dict:
    """Validate a task (or a patch). Returns {ok, cleaned, repairs, blocks}."""
    cleaned, repairs, blocks = {}, [], []
    for field, val in data.items():
        spec = TASK_SCHEMA.get(field)
        if spec is None:                 # id, bang, owner-set fields, etc. pass untouched
            cleaned[field] = val
            continue
        t = spec["type"]
        if t == "text":
            c = _clean_text(val)
            if c != (str(val) if val is not None else ""):
                repairs.append({"field": field, "fix": "normalized text (pipes/whitespace)"})
            if spec.get("required") and not c and not partial:
                blocks.append({"field": field, "reason": "is required and can't be empty"})
            if len(c) > spec.get("max_len", 9999):
                blocks.append({"field": field,
                               "reason": f"too long (>{spec['max_len']} chars) — looks like several "
                                         f"things in one cell; split it (e.g. into Subcategory or a note)"})
            cleaned[field] = c
        elif t == "date":
            iso, err = _coerce_date(val)
            if err:
                blocks.append({"field": field, "reason": err})
            else:
                if iso != (str(val).strip() if val is not None else ""):
                    repairs.append({"field": field, "fix": f"date → {iso or 'empty'}"})
                cleaned[field] = iso
        elif t == "enum":
            e, err = _clean_enum(val, spec["values"], ENUM_SYNONYMS.get(field, {}))
            if err:
                blocks.append({"field": field, "reason": err})
            else:
                if e != (str(val) if val is not None else ""):
                    repairs.append({"field": field, "fix": f"{field} → {e}"})
                cleaned[field] = e
    return {"ok": not blocks, "cleaned": cleaned, "repairs": repairs, "blocks": blocks}


def clean(data: dict) -> dict:
    """Best-effort sanitize (no blocking) — the store's last line of defense."""
    return gate(data, partial=True)["cleaned"]


def log_qc(scope: str, where: str, result: dict) -> None:
    """Record every QC decision: actions_log row + an Obsidian-readable vault note."""
    if not result["repairs"] and result["ok"]:
        return  # nothing notable to log on a clean pass
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload = {"where": where, "scope": scope, "ok": result["ok"],
               "repairs": result["repairs"], "blocks": result["blocks"]}
    try:
        with db.get_conn() as conn:
            conn.execute(
                "INSERT INTO actions_log(kind, ref, scope, result, created_at) VALUES(?,?,?,?,?)",
                ("qc_block" if not result["ok"] else "qc_repair", where, scope,
                 json.dumps(payload), now))
    except Exception:
        pass
    try:
        d = Path(settings.BACKEND_DIR) / "data" / "vault" / ".wom" / "qc-log"
        d.mkdir(parents=True, exist_ok=True)
        line = f"- {now} [{where}/{scope}] " + (
            "BLOCKED: " + "; ".join(f"{b['field']}: {b['reason']}" for b in result["blocks"])
            if not result["ok"] else
            "repaired: " + "; ".join(r["fix"] for r in result["repairs"]))
        (d / (now[:10] + ".md")).open("a", encoding="utf-8").write(line + "\n")
    except Exception:
        pass


def ensure_schema_mirror() -> None:
    """Write the human/agent-readable tasks.yaml mirror (code dict stays authoritative)."""
    try:
        d = Path(settings.BACKEND_DIR) / "data" / "vault" / ".wom" / "schema"
        d.mkdir(parents=True, exist_ok=True)
        lines = ["# Task column rulebook (QC gate). Code (backend/app/qc.py) is authoritative.",
                 "# The '!' column is the P0-P4 priority overlay (validated 0-4 separately).",
                 "columns:"]
        for f, spec in TASK_SCHEMA.items():
            extra = ""
            if spec["type"] == "text":
                extra = f" {{ no_pipes: true, single_line: true, max_len: {spec.get('max_len')}" + \
                        (", required: true" if spec.get("required") else "") + " }"
            elif spec["type"] == "enum":
                extra = " { values: [" + ", ".join(spec["values"]) + "] }"
            elif spec["type"] == "date":
                extra = " { format: YYYY-MM-DD, nullable: true }"
            lines.append(f"  {f}: {spec['type']}{extra}")
        (d / "tasks.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    except Exception:
        pass
