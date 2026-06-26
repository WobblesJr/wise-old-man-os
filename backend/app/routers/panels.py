"""Read endpoints — serve cached JSON panels. Plus a refresh trigger."""
from __future__ import annotations

from fastapi import APIRouter, Query, HTTPException

from .. import db, cache
from ..config import settings

router = APIRouter(prefix="/api", tags=["panels"])

# Which panels are global (scope 'both') vs scoped.
_GLOBAL = {"usage", "connections", "scheduled_jobs", "skills", "feeds"}


@router.get("/panel/{key}")
def panel(key: str, scope: str = Query("personal", pattern="^(personal|work)$")):
    eff_scope = "both" if key in _GLOBAL else scope
    p = db.get_panel(key, eff_scope)
    if p is None:
        raise HTTPException(status_code=404, detail=f"panel '{key}' not cached")
    return {"key": key, "scope": eff_scope, **p}


def _hermes_signals(scope: str) -> list:
    """Live agent-authored signals for the scope (the Hermes layer, not cached)."""
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT id, ts, scope, kind, title, body, target_task_id, confidence, provenance, status "
            "FROM agent_signals WHERE status='active' AND scope=? ORDER BY id DESC", (scope,)).fetchall()
    return [dict(r) for r in rows]


@router.get("/dashboard")
def dashboard(scope: str = Query("personal", pattern="^(personal|work)$")):
    """Bundle every tile the bento home needs in one call."""
    def grab(key, sc):
        p = db.get_panel(key, sc)
        return p["data"] if p else None

    return {
        "scope": scope,
        "mode": settings.DATA_MODE,
        "credentials": settings.credential_status(),
        "warboard": grab("warboard", scope),
        "hermes_signals": _hermes_signals(scope),
        "suggestions": grab("suggestions", scope),
        "approvals": grab("approvals", scope),
        "today": grab("today", scope),
        "task_counts": grab("task_counts", scope),
        "inbox": grab("inbox", scope),
        "usage": grab("usage", "both"),
        "memory": grab("memory", scope),
    }


@router.get("/cockpit")
def cockpit():
    """Agent/System cockpit bundle: connections, jobs, skills, usage."""
    def grab(key):
        p = db.get_panel(key, "both")
        return p["data"] if p else None
    return {
        "connections": grab("connections"),
        "scheduled_jobs": grab("scheduled_jobs"),
        "skills": grab("skills"),
        "usage": grab("usage"),
        "credentials": settings.credential_status(),
    }


@router.post("/refresh")
def refresh():
    return cache.refresh_all()


@router.post("/chaser/run")
def chaser_run():
    """Manually trigger the Ball-in-Court chaser sweep (also runs on every refresh /
    Hermes cron). Returns how many chases were created/advanced/withdrawn."""
    from .. import chaser
    res = chaser.run_all()
    cache.refresh_all()  # re-cache so the new chases surface on the dashboard
    return res


@router.get("/warboard")
def warboard_get(scope: str = Query("personal", pattern="^(personal|work)$")):
    """The Morning War-Board brief for a scope (cached; same object the hero renders)."""
    p = db.get_panel("warboard", scope)
    if p is None:
        raise HTTPException(status_code=404, detail="warboard not cached")
    return p["data"]


@router.post("/warboard/run")
def warboard_run(scope: str = Query("work", pattern="^(personal|work)$")):
    """The 6am cron entrypoint: build the brief and fan it out to Discord + Memory (mock)."""
    from .. import warboard
    return warboard.fan_out(scope)
