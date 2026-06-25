"""Adapter interfaces.

These define the contract every data source must satisfy. Mock impls live in
sibling modules. Real impls (TODO) implement the same methods so nothing
downstream changes.
"""
from __future__ import annotations

from typing import Protocol, Any


class GooglePersonalAdapter(Protocol):
    """Gmail / Calendar / Drive / Sheets for the personal Google account."""

    def inbox(self, scope: str) -> list[dict]: ...
    def today(self, scope: str) -> list[dict]: ...
    def create_calendar_event(self, payload: dict) -> dict: ...
    def send_email(self, draft: dict) -> dict: ...


class SheetTasksAdapter(Protocol):
    """The 'G-Suite Dashboard' sheet: the task source-of-truth (read + append)."""

    COLUMNS: list[str]

    def list_tasks(self, scope: str) -> list[dict]: ...
    def add_task(self, scope: str, task: dict) -> dict: ...
    def update_task(self, scope: str, task_id: str, patch: dict) -> dict: ...


class DriveBridgeAdapter(Protocol):
    """Work (Limbach) file bridge — blocked pending IT, mock for now."""

    def list_files(self, scope: str) -> list[dict]: ...


class FeedsAdapter(Protocol):
    """OSRS hiscores/prices, World Cup, DC events, news."""

    def all_feeds(self) -> dict: ...


class MemoryAdapter(Protocol):
    """Obsidian git vault memory."""

    def recent(self, scope: str) -> list[dict]: ...
    def capture(self, scope: str, text: str, tag: str | None = None) -> dict: ...


class DiscordAdapter(Protocol):
    """Discord notify + console relay."""

    def post(self, channel: str, message: str) -> dict: ...
