"""Adapter registry — selects mock vs live impls based on settings.DATA_MODE.

Routers call `get_adapters()` and use the interface methods. To go live, write a
Live* impl and swap the assignment below (or branch on settings.is_mock).
"""
from __future__ import annotations

from dataclasses import dataclass

from ..config import settings
from .google_personal import MockGooglePersonal
from .sheet_tasks import MockSheetTasks
from .drive_bridge import MockDriveBridge
from .feeds import MockFeeds
from .memory import MockMemory
from .discord import MockDiscord


@dataclass
class Adapters:
    google: object
    sheet: object
    drive: object
    feeds: object
    memory: object
    discord: object


_singleton: Adapters | None = None


def get_adapters() -> Adapters:
    """Process-wide singleton so mock add/update state persists within a session."""
    global _singleton
    if _singleton is not None:
        return _singleton

    if settings.is_mock:
        _singleton = Adapters(
            google=MockGooglePersonal(),
            sheet=MockSheetTasks(),
            drive=MockDriveBridge(),
            feeds=MockFeeds(),
            memory=MockMemory(),
            discord=MockDiscord(),
        )
    else:
        # TODO(live): instantiate Live* impls here once creds are present.
        # from .google_personal import LiveGooglePersonal  (etc.)
        raise RuntimeError(
            "WOM_DATA_MODE=live but no live adapters are wired yet. "
            "See NEEDS-FROM-YOU.md and the TODO(live) blocks in each adapter."
        )
    return _singleton
