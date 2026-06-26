# GO-LIVE — final integration & live-run runbook

Your step-by-step to take Wise Old Man OS from "runs locally on mock/persistent data" to
"live at https://wise-old-man.xyz, gated to your Google login, with Hermes doing the heavy
lifting against your GitHub repo + Obsidian vault."

Status legend: ✅ done & usable now · 🟡 you provide a secret/decision · 🆕 small code task left.

---

## 0. What already works (use it today, no credentials)
```bash
./run.ps1            # Windows  (or ./run.sh)
# open http://127.0.0.1:8787/
```
- ✅ **Durable task grid** — Google-Sheets-style, inline-editable, per-column sort, `!` = P0–P4
  priority. Edits persist to `backend/data/vault/tasks/*.md` and **commit to git** (survives restart).
- ✅ **Hermes layer** (live beliefs over SSE), **multi-agent console** (Hermes/Claude Code/Cowork),
  **War-Board**, **chaser**, **priority overlay**, **quick-add with context**.
- ✅ **Login gate built** (off by default so the demo stays open). Dev sign-in works on localhost.

---

## 1. Storage → your GitHub repo + Obsidian vault  (🟡 + 🆕)
The vault is the source of truth; Hermes syncs it; the website reads/writes a fast local copy.
1. The app already created `backend/data/vault/` as a git repo with `tasks/personal.md`,
   `tasks/work.md`, `overlay/priorities.json`. **Point Obsidian at that folder** to read/edit notes.
2. Create a private GitHub repo (e.g. `wom-vault`) and set it as the remote:
   ```bash
   cd backend/data/vault
   git remote add origin git@github.com:<you>/wom-vault.git
   git push -u origin master
   ```
3. 🆕 **Turn on push** — `GitVaultStore._write()` currently commits but does not push (Hermes owns
   remote sync). Either let Hermes `git push` on its cron, or flip the one-line stub in
   `backend/app/adapters/git_vault.py` to push after commit.
4. Decide the vault home: keep it under `backend/data/vault/`, or move it beside Obsidian and set
   its path (small config add). Memory/signals can move into the vault too (design in
   `docs/ARCHITECTURE-AGENTS.md` / the storage blueprint).

---

## 2. Hermes (the brain) → start it thinking against the dashboard  (🟡)
See `docs/HERMES-SETUP.md` for the full checklist. Minimum to make Hermes live:
1. 🟡 **Anthropic API key** in the VM + an **Agent-SDK think-loop** (orchestrator that spawns sub-agents).
2. 🟡 **Service token** — set `WOM_SERVICE_TOKEN` in the backend `.env` and give Hermes the same
   value. Hermes calls the API with `Authorization: Bearer <token>` (no browser needed).
3. 🟡 **Network path** VM→backend: the Windows host IP:8787, or the public tunnel URL.
4. Hermes then: reads `GET /api/dashboard|tasks|warboard|agent/signals`, and writes via
   `POST /api/agent/signal` (beliefs — appear live), `/api/agent/priority` (P0–P4), `/api/tasks`,
   `PATCH /api/tasks/{id}`, `/api/console/message`. All already built + tested.

---

## 3. Login → "Sign in with Google", locked to you  (🟡 + 🆕)
Two options (the app supports both; pick one). **Cloudflare Access is recommended.**

### Option A — Cloudflare Access (recommended; ~zero code)
1. Cloudflare Zero Trust → **Settings → Authentication → Add Google** (one-time Google OAuth client).
2. **Access → Applications → Add self-hosted** → domain `wise-old-man.xyz`. Session ~30 days.
3. **Policies:** Allow → Emails → `gavin.watson.jr@gmail.com`; (default-deny blocks everyone else).
4. **Service Auth policy** for Hermes → create service token "hermes" → put its headers in Hermes' env.
5. In `.env`: `WOM_AUTH_MODE=cloudflare`. The app middleware reads `Cf-Access-Authenticated-User-Email`
   as defense-in-depth. Done — unauthenticated requests never reach the app.

### Option B — App-level Google login (independent of Cloudflare)
1. Google Cloud Console → Credentials → **OAuth client ID → Web application**.
   - Redirect URIs: `https://wise-old-man.xyz/auth/callback`, `http://localhost:8787/auth/callback`.
   - Consent screen: add your email as a **test user** (extra lock).
   - Scopes: `openid email profile`.
2. `.env`: `WOM_AUTH_MODE=app`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`,
   `ALLOWED_EMAILS=gavin.watson.jr@gmail.com`, a long random `SESSION_SECRET`, `WOM_SERVICE_TOKEN`,
   `WOM_PUBLIC_URL=https://wise-old-man.xyz`.
3. 🆕 **Wire the token exchange** — `routers/auth.py::callback` has a labeled TODO where the Google
   `code → tokens → verified email` step goes (add `google-auth-oauthlib`, ~20 lines). The dev path
   and everything else is done.

---

## 4. Personal Google data → flip from mock to live  (🟡)  *(you said personal Google is available)*
1. Reuse the OAuth client from step 3B (or a separate one) with scopes for
   Gmail/Calendar/Drive + **Sheets (read+write)** — already listed in `.env.example`.
2. Implement `LiveGooglePersonal` + `LiveSheetTasks` (the TODOs already sketched in the adapters) and
   set `WOM_DATA_MODE=live`. The **G-Suite Dashboard Sheet** then two-way-syncs with the vault
   (reconcile by id; `!` column written from the priority overlay). Until then the vault is truth.
3. Inbox/Calendar tiles go real once `LiveGooglePersonal` lands. **Work account stays mock** (deferred).

---

## 5. Deploy → wise-old-man.xyz + phone install  (🟡)
1. Run the backend on your VPS/host; stand up the **Cloudflare tunnel** → `:8787`.
2. DNS `wise-old-man.xyz` → tunnel. HTTPS via Cloudflare (**required** for PWA install).
3. `.env`: `WOM_PUBLIC_URL=https://wise-old-man.xyz`, `CLOUDFLARE_TUNNEL_HOSTNAME=wise-old-man.xyz`
   (already defaulted), keep the CORS origin.
4. iOS: Safari → Share → **Add to Home Screen** (Apple icons/manifest already wired).

---

## 6. Flip the switches (final `.env`) & verify
```
WOM_DATA_MODE=live            # when Live adapters land (else mock)
WOM_TASK_STORE=vault
WOM_AUTH_MODE=cloudflare       # or app
WOM_PUBLIC_URL=https://wise-old-man.xyz
ALLOWED_EMAILS=gavin.watson.jr@gmail.com
SESSION_SECRET=<long random>
WOM_SERVICE_TOKEN=<long random, shared with Hermes>
```
Checks: visit the site in a private window → forced to Google login → only your email gets in.
Hermes `POST /api/agent/signal` with the bearer token → belief appears live. Add a task → it lands
in `vault/tasks/*.md` and pushes to GitHub. Install to your phone.

---

## Remaining build (not blockers — UI polish + nice-to-haves from this chat)
These are designed/queued; say the word and I'll build them next session:
- 🆕 War-Board Phase-1 finish: One-Thing **Do/Chase** flip, **Batch-Approve Queue**, **delegation
  badge/drawer**, the spacing tokens (8/12/16/24). Spec: `docs/WARBOARD-V2-SPEC.md`.
- 🆕 **3-way scope toggle** Personal | Both | Work (unified risk-ranked merge).
- 🆕 **`/api/delegations*` bridge** so "Dispatch to Claude Code/Cowork" is end-to-end.
- 🆕 Frontend auth UX: on 401 redirect to `/auth/login`; show the signed-in email chip; logout button.
- 🆕 Two-way Google Sheet ↔ vault sync; vault `push`; load `priorities.json` into the overlay on refresh.

## The shortest path to "live and mine only"
1. Set `WOM_SERVICE_TOKEN` + `SESSION_SECRET`. 2. Cloudflare tunnel + Access (Option A) with your
email. 3. Give Hermes the token + network path. → The site is public-but-locked-to-you, persistent,
and Hermes can drive it. Personal-Google-live (step 4) and the UI polish can follow without blocking.
