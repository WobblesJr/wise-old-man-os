"""Wise Old Man OS — FastAPI entrypoint.

Boot: init SQLite, run a refresh (mock adapters -> panel cache), expose API,
and serve the zero-install preview.html so the whole UI is clickable with just
`python -m uvicorn app.main:app` — no Node required.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from . import db, cache
from .config import settings
from .auth import guard
from .routers import panels, tasks, approvals, capture, usage, actions, agent, auth

app = FastAPI(title="Wise Old Man OS", version="0.1.0",
              description="Personal+Work command center — running on MOCK data.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (panels.router, tasks.router, approvals.router, capture.router,
          usage.router, actions.router, agent.router, agent.console_router, auth.router):
    app.include_router(r)


@app.middleware("http")
async def _auth_gate(request, call_next):
    """Gate every route behind the allowlisted login (or Hermes bearer token).
    WOM_AUTH_MODE=off (default) keeps the mock demo open; flip to app|cloudflare for prod."""
    if settings.AUTH_MODE == "off" or request.method == "OPTIONS" or guard.is_open(request.url.path):
        return await call_next(request)
    if guard.resolve_identity(request) is None:
        if request.url.path.startswith("/api"):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        return RedirectResponse("/auth/login")
    return await call_next(request)


@app.on_event("startup")
def _startup() -> None:
    db.init_db()
    cache.refresh_all()
    agent.seed_if_empty()              # seed a couple of Hermes beliefs (mock)
    agent.seed_priorities_if_empty()   # seed a few Hermes-decided P0..P4 priorities (mock)


@app.get("/api/health")
def health():
    return {"ok": True, "service": "wise-old-man-os", "mode": settings.DATA_MODE,
            "credentials": settings.credential_status()}


# --- serve the zero-install preview + (optional) built frontend ------------- #
_REPO = Path(__file__).resolve().parents[2]
_PREVIEW = _REPO / "preview"
_FRONT_DIST = _REPO / "frontend" / "dist"


@app.get("/")
def root():
    index = _PREVIEW / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return JSONResponse({"ok": True, "hint": "Preview not found; API is up at /api/health"})


if _PREVIEW.exists():
    app.mount("/preview", StaticFiles(directory=str(_PREVIEW), html=True), name="preview")
# If you build the real Vite app (npm run build), it gets served too:
if _FRONT_DIST.exists():
    app.mount("/app", StaticFiles(directory=str(_FRONT_DIST), html=True), name="app")
