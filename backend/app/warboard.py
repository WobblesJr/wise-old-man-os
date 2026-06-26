"""Morning War-Board — one risk() pass → the single brief that fans out everywhere.

Produces ONE structured object per scope so the dashboard hero band, the Discord
pre-huddle, and the Memory note are guaranteed identical (they all render the same
dict). Folds personal hard dates into the WORK brief so nothing external hides behind
work. Runs on every refresh (data only); the 6am cron calls fan_out() to push it.
"""
from __future__ import annotations

from . import risk
from .adapters import get_adapters

SCOPES = ("personal", "work")


def build(scope: str) -> dict:
    a = get_adapters()
    tasks = risk.stamp_tasks(a.sheet.list_tasks(scope))
    open_tasks = [t for t in tasks if t["risk"]["band"] != "done"]
    ranked = sorted(open_tasks, key=lambda t: t["risk"]["score"], reverse=True)
    at_risk = [t for t in ranked if t["risk"]["band"] in ("amber", "red")]

    top_dates = [{
        "task_id": t["id"], "description": t["description"], "due": t.get("due"),
        "band": t["risk"]["band"], "reason": t["risk"]["reason"],
        "ball_in_court": t.get("ball_in_court"),
    } for t in at_risk[:3]]

    meetings = [{
        "time": e.get("time"), "title": e.get("title"), "where": e.get("where"),
    } for e in a.google.today(scope) if e.get("kind") == "event"]

    stale_balls = [{
        "task_id": t["id"], "who": t.get("ball_in_court"), "description": t["description"],
        "due": t.get("due"), "band": t["risk"]["band"],
    } for t in at_risk if t.get("ball_in_court") != "Me"]

    # the single highest-leverage action: something that's ON YOU and at risk; the most
    # urgent of those, else just the most urgent thing overall.
    mine = [t for t in at_risk if t.get("ball_in_court") == "Me"]
    hi = (mine or ranked or [None])[0]
    highest = None
    if hi:
        highest = {"task_id": hi["id"], "description": hi["description"], "due": hi.get("due"),
                   "why": hi["risk"]["reason"], "action_label": "Start now"}

    # cross-scope: surface personal RED dates inside the work brief
    personal_hard_dates = []
    if scope == "work":
        for t in risk.stamp_tasks(a.sheet.list_tasks("personal")):
            if t["risk"]["band"] == "red":
                personal_hard_dates.append({"task_id": t["id"], "description": t["description"],
                                            "due": t.get("due")})
        personal_hard_dates = personal_hard_dates[:2]

    return {
        "scope": scope, "for": risk.today().isoformat(),
        "headline": _headline(top_dates, meetings, highest),
        "top_dates": top_dates,
        "meetings_today": meetings,
        "stale_balls": stale_balls,
        "highest_leverage": highest,
        "personal_hard_dates": personal_hard_dates,
        "counts": {"in_danger": len(top_dates), "meetings": len(meetings),
                   "stale_balls": len(stale_balls)},
    }


def _headline(top_dates: list, meetings: list, highest: dict | None) -> str:
    n = len(top_dates)
    parts = [f"{n} date{'s' if n != 1 else ''} in danger" if n else "no dates in danger"]
    if meetings:
        parts.append(f"{len(meetings)} meeting{'s' if len(meetings) != 1 else ''} today")
    if highest:
        parts.append("start with: " + highest["description"][:48])
    return " · ".join(parts)


def format_brief(b: dict) -> str:
    """Plain-text rendering shared by the Discord post + Memory note."""
    lines = [f"Morning War-Board ({b['scope']}) — {b['for']}", b["headline"], ""]
    if b["top_dates"]:
        lines.append("Dates in danger:")
        for d in b["top_dates"]:
            who = "" if d.get("ball_in_court") == "Me" else f" [waiting on {d['ball_in_court']}]"
            lines.append(f"  - [{d['band']}] {d['description']} (due {d['due']}) — {d['reason']}{who}")
    if b["personal_hard_dates"]:
        lines.append("Personal hard dates:")
        for d in b["personal_hard_dates"]:
            lines.append(f"  - {d['description']} (due {d['due']})")
    if b["meetings_today"]:
        lines.append("Meetings:")
        for m in b["meetings_today"]:
            lines.append(f"  - {m['time']} {m['title']} @ {m['where']}")
    if b["highest_leverage"]:
        lines.append("-> Highest leverage: " + b["highest_leverage"]["description"])
    return "\n".join(lines)


def fan_out(scope: str) -> dict:
    """Build the brief and push it to Discord (mock) + Memory (mock). 6am cron calls this."""
    a = get_adapters()
    brief = build(scope)
    text = format_brief(brief)
    discord = a.discord.post(f"#daily-{scope}", text)             # mock no-op
    memory = a.memory.capture(scope, "Morning brief — " + brief["headline"], tag="war-board")
    return {"ok": True, "mock": True, "scope": scope, "brief": brief,
            "fanned_to": {"discord": discord, "memory": memory.get("note")}}
