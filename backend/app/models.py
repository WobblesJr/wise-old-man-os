"""Pydantic request/response models for the action + capture endpoints."""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class QuickAddTask(BaseModel):
    scope: str = Field(default="personal", pattern="^(personal|work)$")
    description: str
    action: str = Field(default="action")          # action|wait|hold|read|event
    status: str = Field(default="not_started")
    due: Optional[str] = None
    followup: Optional[str] = None
    start: Optional[str] = None
    category: Optional[str] = "Inbox"
    subcategory: Optional[str] = ""
    ball_in_court: Optional[str] = "Me"
    bang: Optional[str] = ""
    priority: Optional[int] = Field(default=None, ge=0, le=4)   # optional user-picked P0..P4


class TaskPatch(BaseModel):
    status: Optional[str] = None
    ball_in_court: Optional[str] = None
    due: Optional[str] = None
    followup: Optional[str] = None
    action: Optional[str] = None


class CaptureIn(BaseModel):
    scope: str = Field(default="personal", pattern="^(personal|work)$")
    text: str
    kind: str = "note"          # note | task | draft | idea
    tag: Optional[str] = None


class ApproveIn(BaseModel):
    approval_id: str
    decision: str = Field(default="approve", pattern="^(approve|reject)$")


class ScheduleIn(BaseModel):
    title: str
    when: str
    scope: str = Field(default="personal", pattern="^(personal|work)$")
    where: Optional[str] = None


class AgentSignalIn(BaseModel):
    """What Hermes posts to the board — a belief/decision in real time."""
    scope: str = Field(default="work", pattern="^(personal|work)$")
    kind: str = Field(default="belief")   # belief|decision|reprioritize|insight|note|alert
    title: str
    body: Optional[str] = None
    target_task_id: Optional[str] = None
    confidence: Optional[int] = None      # 0..100
    provenance: str = "hermes"


class ConsoleMessageIn(BaseModel):
    """A message into the shared multi-agent console."""
    text: str
    to_agent: str = Field(default="hermes", pattern="^(hermes|claude-code|cowork)$")
    agent: str = "you"                    # who is speaking (default: the user)
    scope: Optional[str] = "work"


class PriorityIn(BaseModel):
    """Hermes assigns a task's priority (P0..P4, 4 = highest) — an overlay, not in the sheet."""
    scope: str = Field(default="work", pattern="^(personal|work)$")
    task_id: str
    level: int = Field(ge=0, le=4)
    why: Optional[str] = None
