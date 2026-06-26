# NEEDS-FROM-YOU

Everything below is **stubbed** so the build keeps moving. The app runs end-to-end
on **mock data** right now. Fill these in to flip pieces from mock → live.

Order is roughly "unblocks the most." Each item says **what to provide** and
**exactly where it plugs in**.

---

## 1. Google OAuth — PERSONAL account (`gavin.watson.jr@gmail.com`)
**Status:** 🟡 Stubbed. Needed for Gmail / Calendar / Drive / Sheets.

**What to provide**
- An OAuth client (Desktop app is easiest) from Google Cloud Console → `client_id` + `client_secret`.
- One-time consent → produces a token JSON.

**Scopes already wired** (in `.env.example` → `GOOGLE_SCOPES`):
- `gmail.readonly`, `calendar.readonly`, `drive.readonly`
- `spreadsheets` (read **+ write** — required so the task quick-add can append rows)

**Where it plugs in**
- `.env`: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_OAUTH_TOKEN_PATH`
- Code: `backend/app/adapters/google_personal.py` → replace `MockGooglePersonal` TODOs with real `google-api-python-client` calls. The interface (`GooglePersonalAdapter`) is already what the routers call, so only this file changes.

---

## 2. G-Suite Dashboard — Sheet ID
**Status:** 🟡 Stubbed. This is the **task source-of-truth** (your "G-Suite Dashboard" sheet).

**What to provide**
- The Sheet ID (the long string in the sheet URL: `docs.google.com/spreadsheets/d/<THIS>/edit`).
- The tab/worksheet name holding tasks (default assumed: `Tasks`).
- Confirm the column order matches what I built to:
  `! / Description / Start / Follow-up / Due / Owner / Ball in Court / Category / Subcategory / Action / Status`

**Where it plugs in**
- `.env`: `GSUITE_DASHBOARD_SHEET_ID`, `GSUITE_DASHBOARD_TAB`
- Code: `backend/app/adapters/sheet_tasks.py` → `MockSheetTasks` reads/writes a local mock; swap to Sheets API using the column map already defined there (`COLUMNS`).

---

## 3. Domain + Cloudflare Tunnel — `wise-old-man.xyz`
**Status:** 🟡 Domain chosen (`wise-old-man.xyz`); DNS + tunnel + HTTPS still to wire.

**What to provide / do**
- Point `wise-old-man.xyz` DNS at the Cloudflare tunnel (or the VPS).
- Stand up the `cloudflared` tunnel to the backend (serves the app + API).
- **HTTPS is required** for the iOS/Android "Add to Home Screen" PWA install to work
  (Safari only offers it on a secure origin). Cloudflare provides the cert.

**Where it plugs in**
- `.env`: `WOM_PUBLIC_URL=https://wise-old-man.xyz`, `CLOUDFLARE_TUNNEL_HOSTNAME=wise-old-man.xyz`
  (already set as defaults). It's in `WOM_CORS_ORIGINS` too.
- Frontend `VITE_API_BASE=https://wise-old-man.xyz` for the built app.
- The PWA manifests (`preview/manifest.webmanifest`, frontend Vite manifest) + Apple touch
  icons are already in place; they just need to be served over that HTTPS origin.

---

## 4. Limbach WORK account
**Status:** 🔴 **Blocked — pending IT.** No action from you yet beyond the IT request.

**What's needed eventually**
- Graph/app registration (client id/secret) **or** a sanctioned file-sync path for work Drive files.

**Where it plugs in**
- `.env`: `LIMBACH_GRAPH_*`, `LIMBACH_DRIVE_ROOT`
- Code: `backend/app/adapters/drive_bridge.py` → `MockDriveBridge`. The Work scope in the UI already toggles to this adapter; it just serves mock work files until unblocked.

---

## 5. API keys (all optional — mock works without them)
**Status:** 🟡 Stubbed.

| Key | For | Plugs into |
|-----|-----|-----------|
| `OSRS_HISCORES_USERNAME` | your RuneScape stats | `adapters/feeds.py` (Hiscores is public, just needs the name) |
| `NEWS_API_KEY` | news feed | `adapters/feeds.py` |
| `DISCORD_BOT_TOKEN`, `DISCORD_DEFAULT_CHANNEL_ID` | Discord notify/console relay | `adapters/discord.py` |
| `MEMORY_VAULT_PATH`, `MEMORY_GIT_REMOTE` | Obsidian git memory vault | `adapters/memory.py` |

Notes:
- OSRS Wiki prices and Hiscores are public (no key). World Cup + DC events are mock-only for now — say the word if you want a real source wired.

---

## 6. Auth / login — 🅿️ BACKBURNER (your call)
Parked for now; proceeding single-user no-login. Captured in `docs/BACKLOG.md`. The one place it
matters sooner: protecting the agent-control endpoints (#7) once the domain is public.

## 7. Hermes ↔ Claude Code / Cowork control bridge
**Status:** 🟡 Designed + stubbed. Lets this dashboard dispatch Claude Code + Cowork to work on your
machine. Full design in `docs/ARCHITECTURE-AGENTS.md`.

**What to provide to go live**
- The exact command/entrypoint Hermes (in the Ubuntu VM) or a Windows runner uses to invoke
  **Claude Code** and **Cowork** for a job (+ how task context is passed).
- Network path from the Ubuntu VM → the Windows FastAPI (host IP:port on the VM network, or the
  `https://wise-old-man.xyz` tunnel).
- Confirm "Cowork" = Claude Cowork; does it run on Windows or in the VM?
- A shared token to auth the control endpoints (so the public domain can't trigger local agents).

**Where it plugs in:** the `delegations` table + `/api/delegations*` endpoints (being built mock);
the runner side is yours/Hermes. Contract is in the architecture doc.

---

## Decisions I made for you (so I didn't stall) — flag if any are wrong
- **Personal⇄Work** swaps both accent color *and* data scope (Personal = Google personal; Work = Limbach DriveBridge mock).
- **Task sheet column order** taken verbatim from your prompt (see #2). Action→color spine: `action=red, wait=yellow, hold=purple, read=green, event=blue`.
- **Backend port** `8787`, **frontend dev** `5173`.
- Since **Node isn't installed on this machine**, I shipped a zero-install `preview.html` for immediate click-around; the real Vite app is in `frontend/` for when Node is available.
