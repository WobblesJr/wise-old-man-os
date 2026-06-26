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

### Phase 1 deadline-defense (from the 12-agent roadmap) — DONE, verified
- **`risk()` scorer** (`backend/app/risk.py`): one server-side verdict per task —
  band (green/amber/red/done), reason, days-to-due, follow-up staleness, runway,
  sortable score. Anchored demo "today" = 2026-06-25 (real clock in live mode).
- **Stamped everywhere**: cache stamps tasks + sorts suggestions by the same engine;
  tasks router stamps too. Hero now ranks by risk (verified order w-s1>w-s2>w-s3>w-s4).
- **Sheet-write spine**: `decide()` `sheet_write` now routes through
  `SheetTasks.update_task` (was a no-op). Verified: approving p-a3 flips p-t8
  in_progress→completed; re-caches so dashboards reflect it. Added approval
  `created_at`/`last_nudged`/`nudge_count` (Phase-2 chaser groundwork).
- **Preview UI**: risk engine mirrored in JS (agrees with backend exactly); task
  table gains a Risk column with right-edge glowing pip, Due cell colored by band,
  auto-bang on red, and a legend (left bar = action type, right pip = deadline risk).
  Verified via DOM: pips red/amber/amber, reasons "due in 2d"/"blocked"/"due in 5d".
- Follow-up (unverified, no Node): mirror the risk pip into `frontend` Tasks.jsx
  using the `task.risk` the API now returns.

### Desktop layout (adapts the happy mobile layout) — DONE, verified
- Single responsive source (option a). lg≥1024 = left sidebar (wordmark + vertical
  nav + scope toggle + MOCK) replacing the top bar, content capped 1360px; md 768-1023
  = top bar + 2-up tiles; <768 = mobile layout unchanged. Focus-visible rings + tile
  hover-lift. Mirrored shell into React `frontend/App.jsx`.
- Verified switching at 1440/820/375 via DOM inspection (preview screenshot tool was
  wedged all session — used eval/inspect, which the tool docs prefer for layout anyway).

### Phase 2 — Ball-in-Court chaser (deadline-defense follow-up engine) — DONE, verified
- **`backend/app/chaser.py`**: idempotent sweep. When `risk()` flags a ball you're
  WAITING ON (ball_in_court != Me) amber/red, drafts the next nudge in a 3-step ladder
  (polite → firmer+CC → escalate to super) and surfaces it as an `email_send` approval.
  Outbound stays locked to a human tap (chaser only drafts).
- **Rules enforced**: follow-up re-arms ONLY when the approval fires (`on_chase_approved`,
  via the sheet-write spine), never at draft time; ladder advances only on renewed
  staleness (not mere due-date pressure); pending chases dedupe; chases for now-ineligible
  tasks are withdrawn. `chases` table tracks nudge_count/ladder_level/status per task;
  `origin` column keeps chaser approvals alive across cache refreshes.
- **Wiring**: runs on every `refresh_all` (Hermes-cron seam) + `POST /api/chaser/run`;
  approvals panel rebuilt from DB so chases show on the dashboard.
- **Preview**: JS chaser mirror — AUTO-CHASE cards in the Approvals tile with ladder
  label + "nudged ×N"; "Send nudge" re-arms (drops it). 
- **Verified**: backend — 2 chases drafted (Turner GC, Dr. Pham); approving bumps
  nudge_count→1, re-arms follow-up to 2026-06-28, sends nothing, throttles next nudge.
  Preview (DOM) — chase card shown, click drops it + 3→2 pending + re-arm toast.

### Phase 2 — Morning War-Board (one brief, fanned out) — DONE, verified
- **`backend/app/warboard.py`**: one `risk()` pass per scope → ONE structured object
  `{headline, top_dates(3), meetings_today, stale_balls, highest_leverage, personal_hard_dates}`.
  The single highest-leverage action = the most urgent on-you at-risk item. Folds personal
  RED dates into the WORK brief so nothing hides behind work.
- **Fan-out** (`fan_out`): builds the brief + pushes it to Discord (mock) and writes a
  Memory note (mock) — same object renders all three surfaces, guaranteed identical.
- **Wiring**: computed into a `warboard` panel on every `refresh_all`; added to the
  `/api/dashboard` bundle; `GET /api/warboard` + `POST /api/warboard/run` (the 6am cron).
- **Preview**: full-width War-Board band atop the dashboard (above the hero) — label,
  headline, band-colored date pips, "→ START WITH" highest-leverage row + Start button.
- **Verified**: backend brief (RFI red/2d, manpower amber/3d, pre-con amber/4d; 2 meetings;
  Turner GC stale; highest=RFI) + fan-out (Discord #daily-work + memory note) + preview
  band (DOM) matches the backend exactly.

### Hosting + installable PWA (iOS "Add to Home Screen") — DONE, verified
- Domain chosen: **wise-old-man.xyz**. Wired into `.env.example` (`WOM_PUBLIC_URL`,
  `CLOUDFLARE_TUNNEL_HOSTNAME`, CORS), README deploy section, NEEDS-FROM-YOU #3
  (DNS+tunnel+HTTPS still to do; HTTPS required for the install prompt).
- iOS install: Apple meta tags (`apple-mobile-web-app-capable/-title/-status-bar-style`)
  + `apple-touch-icon` in both `preview/index.html` and `frontend/index.html`.
- Real PNG icons generated (green tile + dark W) via `tools/gen_icons.py`:
  apple-touch-icon(180)/icon-192/icon-512 in `preview/` and `frontend/public/`.
- Manifests updated (preview + frontend Vite) with PNG icons, id/start_url/scope, maskable.
- **Verified**: served apple-touch-icon/icon-192/manifest all 200; served HTML head carries
  the Apple tags. Safari → Share → Add to Home Screen will install once on HTTPS.
- Vision captured: "living/adaptive" system → registry-driven layout (skills + cron jobs
  declared as data so new ones auto-surface new sections). See docs/WARBOARD-V2-SPEC.md.

### The HERMES layer — real-time agent beliefs on the board — DONE, verified
- Dual-layer model: deterministic **rules engine** (risk/chaser/warboard, relabeled "rules engine")
  + the **Hermes layer** (agent judgment), attributed + visually distinct (violet "✦ HERMES").
- Backend: `agent_signals` table; `backend/app/routers/agent.py` → `POST /api/agent/signal`
  (Hermes posts a belief), `GET /api/agent/signals`, `POST /api/agent/signal/{id}/{act|dismiss}`,
  and **`GET /api/agent/stream` (SSE)** real-time broadcast (in-proc pub/sub). Seeded 2 beliefs;
  added to `/api/dashboard` bundle as `hermes_signals`.
- Preview: a violet HERMES strip in the War-Board band (kind + confidence% + body + Act/Dismiss),
  live via `EventSource('/api/agent/stream')`; seeds embedded for standalone (file://) mode.
- **Verified (DOM)**: seeded belief renders; POSTing a NEW belief arrives **live via SSE** (<2s,
  no refresh), becomes the top signal, flashes a toast. Dashboard bundle carries hermes_signals.
- To go live: Hermes (VM) just calls `POST /api/agent/signal`. See docs/ARCHITECTURE-AGENTS.md.

### Multi-agent shared console — DONE, verified
- The bottom console bar now switches between agents: **Hermes** (VM · orchestrator),
  **Claude Code** (Windows), **Cowork** (Windows) — each with its own color; placeholder +
  send button re-target/recolor per selection.
- Backend: `console_messages` table + `POST /api/console/message` (+ mock role-aware reply) +
  `GET /api/console/messages`, broadcast over the SAME SSE bus as the Hermes layer
  (`backend/app/routers/agent.py` → `console_router`). Shared storage = every agent reads/writes
  one stream and sees the others.
- Preview: agent switcher chips, lines tagged `you → <agent>` / `<agent>`, live via SSE,
  history pulled on load, console auto-scrolls. Standalone (file://) falls back to local echo.
- **Verified (DOM)**: send to Claude Code → round-trips via SSE into the shared log; switching
  agents re-targets; persisted history from a different writer shows up (proves shared storage).
- To go live: each real agent posts its lines via `POST /api/console/message`.

### Task sorting + Hermes priority overlay + smarter quick-add — DONE, verified
- **Priority P0..P4 (P4 highest) as an OVERLAY, not in the sheet** — decided by Hermes, with a
  rules-derived fallback so it's never blank. New `task_priorities` table + `POST /api/agent/priority`
  (Hermes sets it) + seeds; tasks API attaches `{level, source: hermes|rules|you, why}` and accepts
  a user-picked priority on quick-add (stored in the overlay, never the sheet).
- **Sort**: tasks API `?sort=` and preview sort control — Priority (P4→P0), A→Z, Z→A, Due, Sheet order.
  Preview shows a colored P-badge (✦ Hermes / ✎ you / muted rules) + a new "Prio" column.
- **Smarter quick-add**: a "📍 On site" context selector auto-files new tasks under that project
  (category auto-fill); tap-through selects for Category / Action / Priority — no typing the fields.
- **Verified (DOM)**: default prio sort lists ✦P4 first then rules P3; A→Z alphabetizes; setting
  context=Project Alpha auto-fills the category; quick-add with P4 → task tagged "✎ P4 / Project Alpha".
- Backend sort verified too (P4-first, az/za). To go live: Hermes calls `POST /api/agent/priority`.

### Durable git-vault storage (GitHub/Obsidian-shaped) — DONE, verified
- Per the storage design (2 background design agents this session): source of truth = markdown
  task tables in a git `vault/` (Obsidian-friendly), website = fast cache + manipulate layer.
- **`backend/app/adapters/git_vault.py` GitVaultStore**: reads/writes `vault/tasks/{scope}.md`
  GFM tables (id + sheet columns; '!' left blank — priority is the derived overlay), commits each
  write to the vault git repo (`push` stubbed — Hermes owns remote sync). Same interface as
  MockSheetTasks → routers/cache unchanged. Seeds the vault from mock + `git init` on first run.
- Registry selects via `WOM_TASK_STORE` (default **vault**, falls back to mock if git/fs fails).
  Vault lives at `backend/data/vault/` (its own repo; gitignored from the main repo).
- Broadened `TaskPatch` so inline grid edits to ANY field persist via PATCH → vault commit.
- **Verified**: add task → written to `work.md` + committed (`web: add …`) → a FRESH process
  re-reads it (durable across restarts). The dashboard is now continuously usable on local files.

### Secure login gate (Sign in with Google, allowlisted) — DONE, verified
- Per the auth design (background agent): app-level gate now + Cloudflare Access recommended for prod.
- **`backend/app/auth/`**: stateless signed session cookie (stdlib HMAC, no new deps) + `guard.py`
  identity resolver (browser session / CF-Access email / **Hermes bearer token** / localhost dev-bypass).
- **`routers/auth.py`**: `/auth/login` (Google redirect when creds present, else a dark dev-sign-in page),
  `/auth/callback` (dev path works now; real Google token-exchange is a labeled TODO for go-live),
  `/auth/logout`, `/auth/me`. Middleware in `main.py` gates everything except `/auth/*` + `/api/health`.
- `WOM_AUTH_MODE=off` (default) keeps the demo open; `app`/`cloudflare` enforce. Allowlist = your email only.
- **Verified**: bearer token → machine; signed cookie (allowlisted) → human; forged/non-allowlisted/remote
  → blocked; `/auth/login` renders; `/auth/callback?dev=1` sets the cookie; demo stays open at mode=off.

### Milestone 0 — QC bouncer (schema + blocking gate before every write) — DONE, verified
- `backend/app/qc.py`: deterministic structural validator. AUTO-REPAIRS the safe stuff (pipes→/,
  collapse newlines/whitespace, enum casing + synonyms like "Done"→completed, loose dates 07/10→
  2026-07-10) and BLOCKS what it can't safely fix (unknown action/status, unparseable date, a
  description >200 chars = "several things in one cell — split it"), each with a plain reason.
- Rulebook = the Python `TASK_SCHEMA` (authoritative); readable mirror written to
  `vault/.wom/schema/tasks.yaml`. Action/Status word-lists are the system defaults (Category free-text).
- Wired as a BLOCKING gate in front of every save: `routers/tasks.py` quick_add + patch_task (422 on
  block), and `GitVaultStore.add_task/update_task` as the last-line sanitize. Every decision logged to
  actions_log + an Obsidian-readable `.wom/qc-log/<date>.md`; viewable at `GET /api/qc/log`.
- **Verified**: unit (pipes/newlines/synonym/bad-enum/loose-date/bad-date/overloaded all correct) +
  over HTTP (piped grid edit → cleaned + committed; bad status → 422; "Done"→completed; vault row
  stays exactly 12 cells; QC log shows repairs/blocks). The malformed-cell defect class is closed.

### Milestones 1–3 frameworks (creds stubbed until you say go) — DONE, verified
- **M1 (secrets + network path):** `tools/gen_secrets.py` prints the two random tokens you paste;
  run scripts + `.env.example` honor `WOM_HOST` (set 0.0.0.0 so the VM/tunnel reaches the backend).
  The auth gate + service-token bearer already exist — just awaiting your real values.
- **M2 (vault → GitHub push):** `GitVaultStore.push()` behind `WOM_VAULT_PUSH` (default off), remote
  from `WOM_VAULT_REMOTE` (stubbed); auto-push after commit when enabled, **non-fatal** (a dropped
  network never blocks a save); manual/cron trigger `POST /api/vault/push`. Verified: off→push_off,
  flag-on+stub-remote→no_remote (never raises). Activates when you add the private repo + token.
- **M3 (priorities round-trip) — FULLY DONE:** `POST /api/agent/priority` + quick-add now mirror the
  overlay to `vault/overlay/priorities.json` (writer); `cache.refresh_all` loads the file back into the
  DB each refresh (loader), validating `0–4`, ignoring junk, and **an empty file never wipes** live
  priorities. Verified: seed→file (5 entries), Hermes file-edit→DB (w-t3→P4), out-of-range ignored,
  empty-file safety holds. This is how Hermes owns priorities by editing one JSON file.
- Also: `docs/YOUR-GO-LIVE-CHECKLIST.md` — the outside-this-terminal action list (accounts, Cloudflare,
  VM, Windows, storage, Google), grouped + ordered, with the absolute-minimum-to-go-live at the bottom.

### Fix: task grid cells stacking into one cell (illegible rows) — DONE, verified
- Root cause: `.gedit` set `display:block` on editable `<td>`s, which collapses table layout — every
  cell rendered at 0,0 (row_height 0), so all values piled into one spot = "multiple cells in one cell"
  AND unreadable tasks. Single CSS bug behind both complaints.
- Fix: editable cells stay `table-cell` (removed display:block); added Sheets-like truncate-with-ellipsis
  + expand-on-focus for long descriptions.
- Verified (DOM @1280px): table visible, 8 rows, 27px row height, all 12 cells side-by-side in one row,
  each value in its correct column (! / Description / Start / Follow-up / Due / Owner / Ball-in-Court /
  Category / Subcategory / Action / Status / Risk).

### Fix: iOS PWA top cut off behind status bar (safe-area insets) — DONE
- Installed standalone PWA drew full-bleed under the notch/status bar (viewport-fit=cover +
  black-translucent), hiding the top bar + the Personal⇄Work toggle so it couldn't be tapped.
- Fix (preview/index.html CSS): `.topbar` top padding = `calc(env(safe-area-inset-top) + 10px)`
  (+ left/right insets for landscape); `.console` + `.mnav` get `env(safe-area-inset-bottom)` to
  clear the home indicator. env() falls back to 0 on non-notch screens → no desktop/tablet change.
- The dark top-bar background now fills the status-bar area (reads as a native dark bar).
- Note: React frontend header (frontend/) would want the same insets when it's built (parity TODO).

<!-- newest entries go ABOVE this line as work proceeds -->
