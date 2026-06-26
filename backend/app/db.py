"""SQLite cache.

Architecture: the (Hermes-cron) refresh job pulls from adapters and writes cached
JSON into these tables; read endpoints serve from here. That keeps the UI fast and
decoupled from upstream availability. In mock mode the refresh runs at startup.

Schemas: panels, approvals, drafts, tasks, usage, captures, actions_log.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS panels (
    key         TEXT NOT NULL,
    scope       TEXT NOT NULL DEFAULT 'both',
    data        TEXT NOT NULL,           -- JSON blob
    updated_at  TEXT NOT NULL,
    PRIMARY KEY (key, scope)
);

CREATE TABLE IF NOT EXISTS approvals (
    id       TEXT PRIMARY KEY,
    scope    TEXT NOT NULL,
    kind     TEXT NOT NULL,
    title    TEXT NOT NULL,
    summary  TEXT,
    target   TEXT,
    draft_id TEXT,
    risk     TEXT,
    status   TEXT NOT NULL DEFAULT 'pending',
    origin   TEXT NOT NULL DEFAULT 'seed',   -- 'seed' (mock) | 'chaser' (auto-generated)
    data     TEXT NOT NULL
);

-- Ball-in-Court chaser state: one row per task being chased.
CREATE TABLE IF NOT EXISTS chases (
    task_id      TEXT NOT NULL,
    scope        TEXT NOT NULL,
    nudge_count  INTEGER NOT NULL DEFAULT 0,   -- how many nudges actually sent (on approve)
    ladder_level INTEGER NOT NULL DEFAULT 0,   -- 0 polite, 1 firmer+CC, 2 escalation
    last_nudged  TEXT,
    status       TEXT NOT NULL DEFAULT 'pending',  -- pending (awaiting your tap) | approved
    approval_id  TEXT,
    PRIMARY KEY (task_id, scope)
);

CREATE TABLE IF NOT EXISTS drafts (
    id    TEXT PRIMARY KEY,
    kind  TEXT NOT NULL,
    data  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id            TEXT PRIMARY KEY,
    scope         TEXT NOT NULL,
    description   TEXT,
    bang          TEXT,
    start         TEXT,
    followup      TEXT,
    due           TEXT,
    owner         TEXT,
    ball_in_court TEXT,
    category      TEXT,
    subcategory   TEXT,
    action        TEXT,
    status        TEXT,
    data          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS usage (
    id        TEXT PRIMARY KEY,
    ts        TEXT,
    agent     TEXT,
    model     TEXT,
    tokens    INTEGER,
    cost_note TEXT,
    scope     TEXT
);

CREATE TABLE IF NOT EXISTS captures (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    scope       TEXT NOT NULL,
    text        TEXT NOT NULL,
    kind        TEXT NOT NULL DEFAULT 'note',
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS actions_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    kind        TEXT NOT NULL,
    ref         TEXT,
    scope       TEXT,
    result      TEXT,
    created_at  TEXT NOT NULL
);

-- Shared multi-agent console: one stream all agents read/write (Hermes ⇄ Claude Code ⇄
-- Cowork ⇄ you). Shared storage = everyone sees what everyone else is doing.
CREATE TABLE IF NOT EXISTS console_messages (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts        TEXT NOT NULL,
    scope     TEXT,
    agent     TEXT NOT NULL,        -- who wrote it: you | hermes | claude-code | cowork
    to_agent  TEXT,                 -- who it's addressed to (nullable)
    text      TEXT NOT NULL
);

-- The HERMES layer: agent-authored beliefs/decisions posted in real time, distinct from
-- the deterministic rules engine (risk/chaser/warboard). provenance tags who authored it.
CREATE TABLE IF NOT EXISTS agent_signals (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    ts             TEXT NOT NULL,
    scope          TEXT NOT NULL,
    kind           TEXT NOT NULL,        -- belief | decision | reprioritize | insight | note | alert
    title          TEXT NOT NULL,
    body           TEXT,
    target_task_id TEXT,                 -- optional: a task this belief is about
    confidence     INTEGER,              -- 0..100, Hermes's own confidence
    provenance     TEXT NOT NULL DEFAULT 'hermes',
    status         TEXT NOT NULL DEFAULT 'active'   -- active | dismissed | acted
);
"""


def _ensure_dir() -> None:
    Path(settings.DB_PATH).parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    _ensure_dir()
    conn = sqlite3.connect(str(settings.DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    _ensure_dir()
    with get_conn() as conn:
        conn.executescript(SCHEMA)


# --- panel cache helpers ---------------------------------------------------- #

def put_panel(key: str, scope: str, data, updated_at: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO panels(key, scope, data, updated_at) VALUES(?,?,?,?) "
            "ON CONFLICT(key, scope) DO UPDATE SET data=excluded.data, updated_at=excluded.updated_at",
            (key, scope, json.dumps(data), updated_at),
        )


def get_panel(key: str, scope: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT data, updated_at FROM panels WHERE key=? AND scope=?", (key, scope)
        ).fetchone()
    if not row:
        return None
    return {"data": json.loads(row["data"]), "updated_at": row["updated_at"]}
