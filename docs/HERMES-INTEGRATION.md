# Hermes ↔ Backend integration spec
Exact wiring for connecting the Hermes agent to the Wise Old Man OS backend. Code-grounded
(`backend/app/config.py`, `auth/guard.py`, routers). The backend is a thin FastAPI cache +
adapter layer — Hermes is the brain. The backend does **no LLM calls of its own.**

---

## 1. Anthropic API key — the backend needs NONE
The backend never calls Anthropic. There is **no `ANTHROPIC_*` env var** anywhere in it (grep
`config.py` — not there). All reasoning lives in Hermes. So:
- **Nothing to set on the backend side.** Hermes keeps using whatever it already has — your
  Claude Max / OAuth flow is perfectly fine; no standard `console.anthropic.com` key is required
  *for the backend.* (If your Hermes runtime/SDK happens to want a key, that's a Hermes-side concern,
  unaffected by this backend.)
- No model-access requirements flow from the backend.

---

## 2. Every env var the backend reads
Loaded from repo-root `.env` then `backend/.env` (backend wins). Types: **cred** = secret,
**config** = path/URL/value, **flag** = on/off.

| Var | Purpose | Type | Default if unset |
|-----|---------|------|------------------|
| `WOM_SERVICE_TOKEN` | **The token Hermes authenticates with** (Bearer). | cred | `__STUB_SERVICE_TOKEN__` (rejects all bearer auth until set) |
| `WOM_AUTH_MODE` | Auth enforcement: `off` \| `app` \| `cloudflare` | flag | `off` (open; flip to `cloudflare` for prod) |
| `WOM_AUTH_DEV_BYPASS` | Allow localhost with no login | flag | `true` when `WOM_ENV=dev` |
| `ALLOWED_EMAILS` | Comma list of humans allowed to sign in | config | `gavin.watson.jr@gmail.com` |
| `SESSION_SECRET` | Signs the browser session cookie (humans only) | cred | `dev-insecure-change-me` (set in prod) |
| `WOM_PUBLIC_URL` | Public origin (OAuth redirect + Origin checks) | config | `http://localhost:8787` |
| `WOM_HOST` | Bind address (see §6) | config | `127.0.0.1` |
| `WOM_PORT` | Bind port | config | `8787` |
| `WOM_DATA_MODE` | `mock` \| `live` (live needs Google adapters wired) | flag | `mock` |
| `WOM_TASK_STORE` | `vault` (durable git markdown) \| `mock` | flag | `vault` |
| `WOM_VAULT_PUSH` | Push the vault repo to its remote after commits | flag | `false` |
| `WOM_VAULT_REMOTE` | Git remote URL for the vault repo | cred/config | `__STUB_GIT_REMOTE__` |
| `WOM_VAULT_BRANCH` | Vault push branch | config | `master` |
| `WOM_DB_PATH` | SQLite cache path | config | `backend/data/wom.db` |
| `WOM_CORS_ORIGINS` | Comma list of allowed browser origins | config | localhost dev origins |
| `WOM_ENV` | `dev` \| `prod` (drives dev-bypass default) | config | `dev` |
| `GOOGLE_CLIENT_ID` | Google OAuth client (Sheets/Gmail/Cal + app login) | cred | `__STUB_GOOGLE_CLIENT_ID__` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret | cred | `__STUB_GOOGLE_SECRET__` |
| `GSUITE_DASHBOARD_SHEET_ID` | The task sheet id (only if backend talks to Sheets — see §7) | config | `__STUB_SHEET_ID__` |
| `GSUITE_DASHBOARD_TAB` | Sheet tab name | config | `Tasks` |
| `CLOUDFLARE_TUNNEL_HOSTNAME` | Public hostname (informational/CORS) | config | `__STUB_TUNNEL_HOSTNAME__` |
| `LIMBACH_DRIVE_ROOT` | Work-account path (blocked, deferred) | config | `__STUB_BLOCKED_PENDING_IT__` |

**For Hermes, the only one that matters is `WOM_SERVICE_TOKEN`** (+ `WOM_AUTH_MODE` so the gate is on).
Everything else is the backend's own config.

---

## 3. What the backend writes in the vault (and what Hermes should read)
Vault root: `backend/data/vault/` — its own git repo.

| Path | Format | Written by backend | Hermes use |
|------|--------|--------------------|------------|
| `tasks/personal.md`, `tasks/work.md` | GFM markdown table: `id · ! · Description · Start · Follow-up · Due · Owner · Ball in Court · Category · Subcategory · Action · Status` | on every task add/edit | **Read for current task state.** (`!` cell is left blank — priority is the overlay below.) |
| `overlay/priorities.json` | `{ "<task_id>": {scope, level 0–4, source, why, ts} }` | on every priority change; **re-read on every refresh** | **Hermes's write target.** Write this file to set priorities (P4 highest); the backend loads it on next refresh — validates 0–4, ignores junk, and an empty file never wipes live values. |
| `.wom/schema/tasks.yaml` | YAML rulebook | at startup | Read to know valid columns/enums before writing tasks. |
| `.wom/qc-log/<date>.md` | append log | on every QC decision | Audit what got auto-repaired/blocked. |
| `index.md` (every folder) | markdown map | scaffold | Navigation — read the folder's `index.md` to understand its contents. |

**Not in the vault (yet) — use the API instead:** agent beliefs/signals, the multi-agent console,
approvals, drafts, usage. Those live in the SQLite cache and are reached through the endpoints in §4.

So Hermes's two file-level touchpoints: **read `tasks/*.md`** for state, **read/write
`overlay/priorities.json`** for priorities. Everything else is API.

---

## 4. API endpoints Hermes should call
Base: `http://<host>:8787` (or `https://wise-old-man.xyz` via the tunnel). JSON in/out.

**Read (GET):**
- `/api/health` — liveness (always open, no auth)
- `/api/dashboard?scope=personal|work` — the whole bento bundle (warboard, suggestions, approvals, today, tasks counts, inbox, usage, memory, hermes_signals)
- `/api/tasks?scope=&filter=&sort=` — task rows (with risk + priority attached)
- `/api/warboard?scope=` — the morning brief object
- `/api/approvals?scope=` · `/api/drafts/{id}` — pending approvals + draft bodies
- `/api/agent/signals?scope=personal|work|both` — current beliefs
- `/api/console/messages` · `/api/qc/log` · `/api/usage` · `/api/cockpit`

**Write (POST/PATCH) — the agent surface:**
- `POST /api/agent/signal` — post a belief `{scope, kind, title, body, target_task_id?, confidence?}` (appears live on the board via SSE)
- `POST /api/agent/priority` — set a task's priority `{scope, task_id, level 0–4, why?}` (also mirrors to `priorities.json`)
- `POST /api/console/message` — `{to_agent, text}` into the shared console
- `POST /api/tasks` — quick-add a task (goes through the QC gate → 422 if it can't be cleaned)
- `PATCH /api/tasks/{id}?scope=` — edit fields (QC-gated)
- `POST /api/capture` — `{scope, text, kind}` quick-capture
- `POST /api/refresh` — rebuild the cache (also reloads `priorities.json`)
- `POST /api/warboard/run?scope=` — build + fan out the morning brief (the 6am cron)
- `POST /api/chaser/run` — run the ball-in-court chaser sweep
- `POST /api/vault/push` — push the vault to GitHub (no-op until `WOM_VAULT_PUSH` + remote set)
- `POST /api/approvals/decide` — `{approval_id, decision}` (note: outbound effects are mock until live adapters are wired)
- **SSE** `GET /api/agent/stream?scope=both` — live event stream (beliefs, console, priorities). Cookie-auth only; Hermes generally POSTs rather than subscribes.

**Auth:** when `WOM_AUTH_MODE` is `app` or `cloudflare`, **every** route except `/api/health` and
`/auth/*` requires identity. Hermes supplies it with the bearer token (§5). When `off` (today's
default), all routes are open.

---

## 5. The service token — where it's used
There are **two different tokens** if you go through Cloudflare. Don't conflate them.

**(a) Backend app token — `WOM_SERVICE_TOKEN`** (this is the one the backend checks):
- Set the **same value** in the backend `.env` and in Hermes.
- Hermes sends it as an HTTP header on every API call:
  `Authorization: Bearer <WOM_SERVICE_TOKEN>`
- Backend check is in `auth/guard.py` → `_bearer_ok()`: it reads the `Authorization` header, takes
  the `Bearer ` token, and `compare_digest`s it against `settings.SERVICE_TOKEN` (the env var).
- It's a **header at request time** on the Hermes side, an **env var** on the backend side. Same string.

**(b) Cloudflare Access service token** (only when `WOM_AUTH_MODE=cloudflare`, going through the tunnel):
- This is a *Cloudflare* credential, validated by Cloudflare at the edge — the backend never sees it.
- Hermes sends `CF-Access-Client-Id: <id>` and `CF-Access-Client-Secret: <secret>` headers so the
  edge lets the request through. After that, the backend's gate still applies, so Hermes also sends
  the `Authorization: Bearer` from (a).
- The backend additionally trusts the `Cf-Access-Authenticated-User-Email` header that Cloudflare
  injects for human logins (defense-in-depth) — Hermes doesn't need that; it uses the bearer.

**Net:** direct (no Cloudflare) → just `Authorization: Bearer <WOM_SERVICE_TOKEN>`. Through Cloudflare
Access → that **plus** the two `CF-Access-Client-*` headers.

---

## 6. Bind address + port for the tunnel
- Port: **8787** (`WOM_PORT`).
- **If `cloudflared` runs on the same machine as the backend** (recommended): keep
  `WOM_HOST=127.0.0.1`; point the tunnel at `http://localhost:8787`. Nothing else is exposed.
- **If Hermes (a different VM) reaches the backend directly** (no tunnel in between): set
  `WOM_HOST=0.0.0.0` so it binds all interfaces, and Hermes calls `http://<backend-host-ip>:8787`.
- `cloudflared` ingress example:
  ```yaml
  ingress:
    - hostname: wise-old-man.xyz
      service: http://localhost:8787
    - service: http_status:404
  ```
- The run scripts honor `WOM_HOST` (`run.ps1` / `run.sh`), so `WOM_HOST=0.0.0.0 ./run.sh` just works.

---

## 7. Google Sheets — let Hermes own it (recommended)
- **Today the backend does NOT call Sheets at all** — tasks come from the vault (`WOM_TASK_STORE=vault`)
  or mock. A `LiveSheetTasks` adapter is a stubbed TODO.
- **Recommended, and it matches your architecture (“heavy lifting on Hermes”):** Hermes owns the
  Google Sheets credentials. Hermes reads/writes the sheet and writes task rows into the vault
  (`tasks/*.md`); the backend just reads the vault. **→ the backend needs no Sheets creds, and does
  not piggyback on Hermes.** Clean single-owner; no double-writer conflicts.
- **Alternative (only if you want the backend to talk to Sheets directly):** implement `LiveSheetTasks`
  and set `WOM_DATA_MODE=live` + `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` + `GSUITE_DASHBOARD_SHEET_ID`
  + a token. Not recommended while Hermes is the orchestrator.

---

## TL;DR for the Hermes side
1. **No Anthropic key for the backend.** Keep Hermes's existing auth.
2. Share **one secret**: `WOM_SERVICE_TOKEN` (same value backend env + Hermes), sent as
   `Authorization: Bearer …`. Set `WOM_AUTH_MODE=cloudflare` (or `app`) to turn the gate on.
3. Base URL `https://wise-old-man.xyz` (tunnel) or `http://<host>:8787` (direct).
4. **Read** `tasks/*.md` for state; **write** `overlay/priorities.json` for priorities; everything
   else via the §4 API (post beliefs, set priorities, quick-add, refresh, warboard/run).
5. Through Cloudflare Access, add the `CF-Access-Client-Id/-Secret` headers too.
6. Hermes owns Google Sheets; the backend reads the vault it writes.
