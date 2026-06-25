"""Memory adapter — Obsidian git vault (recent facts + quick-capture)."""
from __future__ import annotations

import copy

from ..mock import mock_data as M


class MockMemory:
    def __init__(self) -> None:
        self._mem = copy.deepcopy(M.MEMORY)
        self._seq = 100

    def recent(self, scope: str) -> list[dict]:
        return self._mem.get(scope, [])

    def capture(self, scope: str, text: str, tag: str | None = None) -> dict:
        self._seq += 1
        note = {"id": f"m-{scope[0]}{self._seq}", "text": text,
                "tag": tag or "capture", "ts": "just now"}
        self._mem.setdefault(scope, []).insert(0, note)
        return {"ok": True, "mock": True, "note": note}


# --------------------------------------------------------------------------- #
# TODO(live): LiveMemory
#   - MEMORY_VAULT_PATH: write one markdown file per fact (frontmatter + body),
#     append an index line, `git add/commit/push` to MEMORY_GIT_REMOTE.
#   - recent(): read the index / latest files. Same shapes.
# --------------------------------------------------------------------------- #
