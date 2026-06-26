# Wise Old Man OS

A personal **command center** that unifies your Personal and Work worlds into one
agent-driven dashboard: suggested next steps, approvals, tasks (from your G-Suite
Dashboard sheet), inbox, calendar, agent/usage cockpit, memory, and a persistent
console. Dark, flat, "W / Wise Old Man" wordmark, Personal⇄Work toggle.

> **Status: runs on MOCK data.** No real emails are sent, no real sheet is written,
> nothing is deployed. Flip pieces to live by filling in `NEEDS-FROM-YOU.md`.

---

## Quick start (zero Node required)

The FastAPI backend serves a **self-contained preview UI**, so you can click around
the whole thing with only Python.

```powershell
# Windows
./run.ps1
```
```bash
# macOS / Linux / Git-Bash
./run.sh
```

Then open **http://127.0.0.1:8787/** — Dashboard, Tasks, Cockpit, scope toggle,
console, quick-add, approvals — all live on mock data.

- API health: http://127.0.0.1:8787/api/health
- Interactive API docs: http://127.0.0.1:8787/docs

You can also just **double-click `preview/index.html`** (it falls back to embedded
mock data when opened as a file).

---

## Architecture

```
┌──────────────┐   fetch    ┌──────────────────────┐   adapters   ┌────────────────┐
│  Frontend    │ ─────────► │  FastAPI (read cache  │ ───────────► │  Mock adapters │
│  PWA (React) │  /api/...   │  + action stubs)      │              │  (→ live TODO) │
│  + preview   │ ◄───────── │  SQLite panel cache    │ ◄─────────── │  Google/Sheet/ │
└──────────────┘   JSON     └──────────────────────┘   refresh     │  Drive/Feeds…  │
                                       ▲                            └────────────────┘
                                       │ Hermes cron (refresh on schedule)
```

- **Read endpoints** serve cached JSON from SQLite (fast, decoupled).
- A **refresh** pulls adapters → cache (runs at startup; `POST /api/refresh` on demand;
  Hermes cron in prod).
- **Action endpoints** (approve/send/schedule, quick-add, capture) are **stubbed** —
  in mock mode they no-op. Swapping to live = implementing the `Live*` adapter with the
  same interface; routers don't change.

### Layout
```
backend/                 FastAPI + SQLite
  app/
    main.py              entrypoint (serves API + preview)
    config.py            env + mock-safe defaults + credential status
    db.py                SQLite schemas: panels, approvals, drafts, tasks, usage, captures, actions_log
    cache.py             refresh service (adapters -> panel cache)
    models.py            pydantic request models
    routers/             panels, tasks, approvals, capture, usage, actions
    adapters/            base (interfaces) + Mock impls + registry
    mock/mock_data.py    the realistic dataset (both scopes)
preview/                 zero-install UI (React via CDN) + PWA manifest + sw
frontend/                the real React + Vite + Tailwind PWA (needs Node to build)
tools/                   manpower-loaded-schedule xlsx generator
```

---

## The real frontend (`frontend/`)

The production UI is a **React + Vite + Tailwind** PWA. This machine has no Node, so it
isn't built here, but the source is complete:

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173  (proxies /api to :8787)
npm run build      # outputs frontend/dist  (backend serves it at /app)
```

The `preview/` build mirrors the same screens/design so you lose nothing while Node is
unavailable.

---

## Screens

- **Bento Dashboard** — hero *Suggested next steps* (one-tap actions) + tiles: Approvals,
  Today, Tasks-at-a-glance (counts by type/status), Inbox, Agent/usage, Memory+quick-capture,
  Console. Stacks to one column on mobile.
- **Task List** — dense table (desktop) / cards (mobile). Columns straight from the
  G-Suite Dashboard sheet. **Action drives a left color spine**:
  `action=red · wait=yellow · hold=purple · read=green · event=blue`. Status = secondary
  dot/label. Ball-in-Court "Me" is accented. Filters: All / Mine / each type. Quick-add bar.
- **Agent/System Cockpit** — connections, scheduled jobs, skills inventory, usage ledger
  (token volume + Max plan-usage).
- **Persistent console** — on every view, text + mic placeholder.

---

## Going live

Everything is stubbed behind clean interfaces. See **`NEEDS-FROM-YOU.md`** for the exact
secrets/decisions and where each one plugs in. Set `WOM_DATA_MODE=live` once the `Live*`
adapters are implemented.

## Deploy → `wise-old-man.xyz`

VPS behind a **Cloudflare tunnel** at **https://wise-old-man.xyz**; **Hermes cron** calls
`POST /api/refresh` (and `POST /api/warboard/run` at ~6am) on a schedule.
- DNS for `wise-old-man.xyz` → Cloudflare tunnel → the FastAPI backend (serves app + API).
- `WOM_PUBLIC_URL` / `CLOUDFLARE_TUNNEL_HOSTNAME` and the CORS origin are pre-set in `.env.example`.

### Install on your phone (Add to Home Screen)
Once served over **HTTPS** at the domain:
- **iOS Safari:** open the site → **Share** → **Add to Home Screen**. It installs as a
  standalone app ("Wise Old Man") using the Apple touch icon + manifest (already wired in
  `preview/index.html` / the frontend `index.html`). HTTPS is required — it won't offer it over http.
- **Android Chrome:** you'll get an install prompt / "Add to Home screen" from the menu.
