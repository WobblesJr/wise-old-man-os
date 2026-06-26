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
