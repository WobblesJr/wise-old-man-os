"""Deadline-defense scorer — the one place urgency is computed.

Every task gets a single `risk()` verdict stamped on it: a band (green/amber/red/done),
a human reason, days-to-due, follow-up staleness, a normalized runway (0..1), and a
sortable score. Suggestions, the hero ranking, and the task-list pip all consume THIS —
so "what's at risk" means exactly one thing across the whole app.

NOTE (Phase-1 scope): uses calendar days. The roadmap's per-subcategory business-day
lead-times + contractual response windows are the Phase-2 refinement — see
docs/PM-AUTOMATION-ROADMAP.md. The interface (the returned dict) won't change.
"""
from __future__ import annotations

from datetime import date

from .config import settings

# Anchor "today" so the mock demo always looks current. In live mode use the real clock.
DEMO_TODAY = date(2026, 6, 25)


def today() -> date:
    return DEMO_TODAY if settings.is_mock else date.today()


def _parse(d: str | None) -> date | None:
    if not d:
        return None
    try:
        return date.fromisoformat(d)
    except ValueError:
        return None


# Band -> base score (higher = more urgent). Score breaks ties by closeness to due.
_BAND_BASE = {"red": 100, "amber": 50, "green": 10, "done": 0}


def risk_for_task(task: dict, ref: date | None = None) -> dict:
    ref = ref or today()
    status = task.get("status")
    due = _parse(task.get("due"))
    followup = _parse(task.get("followup"))
    ball = task.get("ball_in_court", "Me")

    days_to_due = (due - ref).days if due else None
    days_past_followup = (ref - followup).days if followup else None

    if status == "completed":
        return {"band": "done", "reason": "completed", "days_to_due": days_to_due,
                "days_past_followup": days_past_followup, "runway": 1.0, "score": 0, "bang": False}

    band = "green"
    reasons: list[str] = []

    # --- due-date pressure ---
    if days_to_due is not None:
        if days_to_due < 0:
            band = "red"; reasons.append(f"overdue {abs(days_to_due)}d")
        elif days_to_due <= 1:
            band = "red"; reasons.append("due now")
        elif days_to_due <= 2:
            band = "red"; reasons.append(f"due in {days_to_due}d")
        elif days_to_due <= 5:
            band = _max_band(band, "amber"); reasons.append(f"due in {days_to_due}d")

    # --- follow-up staleness (a ball you're waiting on that's gone quiet) ---
    if days_past_followup is not None and days_past_followup > 0:
        owed_by_other = ball != "Me"
        if days_past_followup >= 3:
            band = _max_band(band, "red")
        else:
            band = _max_band(band, "amber")
        reasons.append(("waiting on " + ball if owed_by_other else "follow-up") +
                       f" {days_past_followup}d past")

    # --- blocked items that also have date pressure get nudged up ---
    if status == "blocked" and band == "green":
        band = "amber"; reasons.append("blocked")

    # normalized runway: 1.0 = comfortable (>=14d), 0 = due/overdue
    if days_to_due is None:
        runway = 0.6
    else:
        runway = max(0.0, min(1.0, days_to_due / 14.0))

    score = _BAND_BASE[band]
    if days_to_due is not None:
        score += max(0, 30 - days_to_due)  # closer due date => higher
    if days_past_followup and days_past_followup > 0:
        score += days_past_followup

    return {"band": band, "reason": ", ".join(reasons) or "on track",
            "days_to_due": days_to_due, "days_past_followup": days_past_followup,
            "runway": round(runway, 2), "score": score, "bang": band == "red"}


def _max_band(a: str, b: str) -> str:
    order = ["green", "amber", "red"]
    return a if order.index(a) >= order.index(b) else b


def stamp_tasks(tasks: list[dict]) -> list[dict]:
    """Return tasks with a `risk` key added (non-mutating copy)."""
    ref = today()
    out = []
    for t in tasks:
        r = risk_for_task(t, ref)
        nt = dict(t)
        nt["risk"] = r
        # auto-raise the bang on red (deadline-defense: red always flags)
        if r["bang"] and not nt.get("bang"):
            nt["bang"] = "!"
        out.append(nt)
    return out


def suggestion_score(sugg: dict, tasks_by_id: dict[str, dict]) -> int:
    """Rank a suggestion: if it points at a known task, use that task's risk score;
    otherwise fall back to its declared urgency."""
    ref_task = tasks_by_id.get(sugg.get("ref"))
    if ref_task and "risk" in ref_task:
        return ref_task["risk"]["score"]
    return {"high": 90, "med": 55, "low": 20}.get(sugg.get("urgency"), 40)
