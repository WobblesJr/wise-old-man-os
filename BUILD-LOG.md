# BUILD-LOG

Reverse-chronological log of what got built, by an autonomous session.

## 2026-06-25 — Session 1 (autonomous)

### Environment
- Working dir was empty. Spec `.md` files not on disk → built from the prompt summary.
- Toolchain found: **Python 3.8.10**, **git 2.54**. **No Node/npm.**
- Installed + verified **FastAPI 0.124 + uvicorn** → backend is runnable now.
- Decision: ship a zero-install `preview.html` (CDN React+Tailwind) for immediate
  click-around since Vite can't run here; real Vite app lives in `frontend/`.

### Scaffold
- `git init`; `.gitignore`, `.env.example`, `README.md`, `run.ps1`, `run.sh`.
- `NEEDS-FROM-YOU.md` with 5 stubbed items + plug-in points.

### Backend (FastAPI + SQLite) — DONE, verified live
- `config` (mock-safe defaults + credential status), `db` (7 tables: panels,
  approvals, drafts, tasks, usage, captures, actions_log), `cache.refresh_all`
  (adapters → panel cache), `models` (pydantic).
- Routers: `panels` (/api/panel, /api/dashboard, /api/cockpit, /api/refresh),
  `tasks` (list+filter, quick-add, patch), `approvals` (list, draft, decide),
  `capture`, `usage`, `actions` (schedule, run, log).
- Adapters: `base` interfaces + Mock impls (GooglePersonal, SheetTasks w/ column
  map, DriveBridge, Feeds, Memory, Discord) + `registry` (mock/live switch).
- Realistic mock dataset for both Personal + Work scopes.
- **Verified over HTTP** (uvicorn :8799): health, dashboard(work)=4 sugg/2 appr/
  7 open/5 mine, tasks filter, quick-add, capture, usage, and approve email →
  confirmed MOCK no-op ("no email left the building"). Root serves preview (200).

### Preview UI (zero-install) — DONE
- `preview/index.html`: self-contained React+Tailwind (CDN) — Dashboard (bento),
  Tasks (table/cards, color spine, filters, quick-add), Cockpit, persistent
  console, Personal⇄Work toggle. PWA manifest + service worker + icon.
- Served by the backend at `/` so one command = clickable app, no Node needed.
- Falls back to embedded mock data if opened as a file (file://).

### Frontend (React + Vite + Tailwind PWA) — DONE (source; needs Node to build)
- Vite + Tailwind + PWA plugin; store (scope/accent/console/toast), api client,
  useApi hook, shared ui, Console, screens (Dashboard/Tasks/Cockpit), App shell.
- Mirrors the preview; fetches from the API with graceful "backend down" states.

### Tools — DONE
- `tools/manpower_schedule.py`: xlsx manpower-loaded-schedule generator (activities
  × weeks grid, trade color spine, TOTAL row, man-hours, crew-curve chart; load
  curves flat/ramp/front/back). Verified: built-in sample → valid 2-sheet xlsx
  (peak 35 wk5, 6,880 man-hrs). `sample_plan.json` + README included.

### Notes
- Installed for this machine: fastapi, uvicorn, python-dotenv, openpyxl.
- HARD LIMIT respected throughout: nothing sent/written/deployed; all effects mocked.

### Fix — preview was a black screen
- **Cause:** the preview depended on 3 runtime CDNs (React UMD + in-browser Babel
  + Tailwind Play CDN). Babel-in-browser failed silently in the sandboxed/served
  context → nothing rendered (confirmed via preview console + DOM inspection).
- **Fix:** rewrote `preview/index.html` to be **100% dependency-free** — vanilla JS
  (DOM rendering, event delegation) + embedded CSS design system. No CDNs, no build,
  works offline / double-click / served. Same screens + design.
- **Verified in-browser:** renders (7 tiles, topbar, hero); scope toggle flips accent
  personal #34d399 → work #f59e0b and re-scopes data; Tasks shows 8 rows with correct
  action spines (red/yellow/green…); console + filters + quick-add functional.
- Also noted: the machine has **two Pythons** — Anaconda (used by the preview panel)
  and the WindowsApps 3.8. `run.ps1/.sh` pip-install first, so they self-provision
  whichever `python` resolves to.

<!-- newest entries go ABOVE this line as work proceeds -->
