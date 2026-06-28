# Hermes handoff — Wise Old Man OS

**Living document.** This is the running brief between the build side (the dashboard/PWA in this repo) and
**Hermes** (the brain + the deploy/host owner). Update it every session. Last updated **2026-06-28**.

> **Two asks of Hermes are standing (do them every time):**
> 1. Keep **`docs/USER-MANUAL.md`** current. It's the end-user manual (indexed). Whenever a feature ships or
>    changes, refresh the matching section + the "Document status" date. **The manual is a Hermes function and
>    must be re-confirmed in every future handoff.**
> 2. Reply to the **"What we need from Hermes"** section below with status + what you need from us.

---

## 0. TL;DR for Hermes

The dashboard is now a fairly complete, calm "command center" running on **MOCK data** in a single file
(`preview/index.html`, vanilla JS, no build). The backend (`backend/`, FastAPI) serves it at `/`. Today we:
shipped a Warm-Paper redesign, ran a multi-agent QA pass and fixed the blockers, then **built the 5 missing
command-center surfaces + a Notes overhaul + this manual**. Nothing sends/writes for real yet — that's the
mock→live flip, which is largely **your** side (adapters, real actions, real usage/memory, the Obsidian vault).
Also: the live site **works** — the user just hit a `www` routing gap (see §2).

---

## 1. What's been done (build side)

### Design + structure
- **Warm-Paper** palette + strict base-4 spacing scale; calm, uncluttered, flat/hairline aesthetic.
- **3-tier left nav:** Primary (Dashboard, Tasks, **Approvals**) · Agents (Workspace + Hermes/Claude Code/Cowork)
  · More (Cockpit, **Activity**, Notes). Phone gets a bottom tab bar. PWA manifest re-themed to warm paper.
- Finance shows on **Personal only**; the dedicated Finance section is intentionally deferred.

### QA pass (multi-agent) — fixed
- Spreadsheet inline editing was rebuilding the grid on every commit (focus loss) — now commits **in place**;
  Enter/Tab cell navigation; no-op guard; editable **P0–P4 priority** cell.
- PWA manifest dark→warm; iOS safe-area top bar; mobile nav reaches Notes; touch/Apple-Pencil resizers;
  focus-visible + keyboard nav; description wrapping; scope-aware SSE toasts.

### The 5 command-center surfaces (new this session)
1. **Approvals queue** — staged agent actions you approve/reject/edit before anything is sent. Pending-count
   **badge** on the nav + a **"N awaiting you"** pill on the Dashboard hero. Per-scope.
2. **Ball-in-Court chaser** — drafts a specific follow-up for any task you're waiting on (hero CTA, per-row
   button, "Chase all waiting"). **Stages as a pending Approval — never auto-sends.**
3. **Activity log / console** — audit trail of every event (signals, approvals, edits, chases, notes, nightly
   push), grouped by day, filterable by kind + scope. Persists to localStorage on the web.
4. **Global search / command palette** — **⌘K / Ctrl-K** (or top-bar button). Ranks Tasks, Notes, and Commands;
   fully keyboard-driven.
5. **Usage + Memory** — Cockpit now reads usage from a single source (no more frozen 41%); a **Memory keeper**
   card shows vault-tier counts (00-raw→10-wiki→20-outputs), recent promotions, and the last nightly push.

### Notes overhaul (new this session)
- **Obsidian vault tree** — real nested tree (00-raw / 10-wiki / 20-outputs → Work/Personal → project folders →
  `.md` files). Click a folder to filter the note list; click a file to open it; edits write back in place.
- **Freeform infinite canvas** — 4th editor mode (Type/Split/Ink/**Freeform**), Apple-Freeform-style pan/zoom
  canvas with pen/highlighter/eraser/select/sticky/text, **Apple Pencil pressure**, hover ring.
  **Honest limit:** the Apple Pencil **Pro squeeze / hardware double-tap are not exposed to any web app** —
  substitutes are the ⟳ tool-cycle button and an on-canvas double-tap. Pressure works; tilt is read by some
  iPads but not wired to stroke width yet.

### Docs
- **`docs/USER-MANUAL.md`** — full indexed end-user manual (your living doc going forward).
- All verified in the local preview with **zero console errors**.

---

## 2. The website "404" — diagnosis + fix (your side)

**Finding:** the site is **up and gated correctly.** Both `https://wise-old-man.xyz` and
`https://www.wise-old-man.xyz` return **302 → Cloudflare Access** (the Google login at
`wiseoldman.cloudflareaccess.com/...`). Tunnel + Access are working. The user's `404` came from visiting the
**`www`** host: it reaches Access fine, but the **cloudflared tunnel ingress has no rule for `www`**, so after
auth nothing matches and it 404s. The bare apex is wired end-to-end (Access → tunnel → backend `@app.get("/")`
→ `preview/index.html`).

**Immediate user workaround (already told them):** use **`https://wise-old-man.xyz`** (no `www`).

**Please fix one of these so `www` doesn't dead-end:**
- **Simplest:** add a Cloudflare **Redirect Rule** `www.wise-old-man.xyz/* → https://wise-old-man.xyz/$1` (301).
- **Or:** add `www` as a public hostname on the tunnel (ingress → `http://localhost:8787`) **and** a DNS CNAME
  for `www` → the tunnel, **and** extend the Access application to cover `www` (or use a wildcard app).

**If the bare apex ever 404s *after* login** (different failure): check `systemctl status wom` (uvicorn up),
that the tunnel origin is `http://localhost:8787`, and `curl -s localhost:8787/` on the VM returns the HTML.
Deploy/restart model is in `docs/DEPLOY-RESTART.md` + `tools/deploy.sh` (systemd for liveness, cron for git pull;
static `preview/index.html` changes need **no restart** — they're served fresh on next request).

---

## 3. What's still MOCK → the flip points we need from you

Everything below is built on the UI side and **guarded** so the app loads fine without it; it goes live when the
backend/Hermes provides the real source. The frontend already detects http vs file and is structured for the flip.

| Surface | Frontend today | What Hermes/back end needs to provide |
|---|---|---|
| **Approvals** | `S.approvals` seeded from `MOCK.approvals`; approve/reject is local + toast | `GET /api/approvals` (list, per scope) + `POST /api/approvals/{id}/resolve` that **actually executes** on approve (send email/Discord, write the Sheet, etc.) per approval `kind`. Hermes is the one that *stages* approvals. |
| **Chaser** | Generates the draft text, stages a pending approval | Nothing extra — real send happens when the chase approval is approved. Optionally Hermes pre-stages chases on its 15-min cron. |
| **Activity log** | Writes events to `S.activity` + localStorage | `GET /api/activity` (server-side event log). Hermes appends an event each time it acts so the audit trail is real + shared across devices. |
| **Usage** | `MOCK.usage` (window %, tokens, reset) | `GET /api/usage` with real Claude window/token numbers. |
| **Memory keeper** | `MOCK.memory` (tier counts, promotions, last push) | Real tier counts from the vault + the promotion log + last nightly-push timestamp. |
| **Notes / vault** | `MOCK.vault` tree; edits mutate in memory | Read the **real Obsidian vault** file tree + file bodies; persist edits back to the vault (you own vault git sync). |
| **Freeform canvas** | Strokes in `S.freeform`; `persistFF()` PUTs to `/api/notes/freeform` (no-op if 404) | Implement `PUT /api/notes/freeform` (store strokes/items per note) if you want canvases to persist server-side. |
| **Hermes beliefs** | Live over SSE `/api/agent/stream` (already wired + working) | Keep emitting `agent_signal` events; they appear on the Dashboard + Workspace and toast in-scope. |

Auth/data/deploy switches and the adapter TODOs are already catalogued in `docs/GO-LIVE.md` and
`docs/HERMES-INTEGRATION.md` — those remain the source of truth for env vars, the service token, and the
mock→live adapter work. This handoff is the *delta* on top of them.

---

## 4. What we need from Hermes (please reply in this doc)

1. **Status:** what's running on the VM right now — uvicorn (systemd `wom`), cloudflared tunnel, the cron pull,
   and the think-loop? Are the morning War-Board + 15-min chaser jobs actually firing?
2. **The `www` fix** (§2) — applied? Confirm the host the user should bookmark.
3. **Which mock→live flips** from §3 do you want first? Our recommendation: **Approvals real-execute + Activity
   feed + real Usage/Memory**, since they make the morning-review loop trustworthy end-to-end.
4. **What do you need from us** to do those — exact endpoint shapes, payloads, an auth header contract, a JSON
   schema for approvals/activity? Tell us and we'll build the frontend side to match.
5. **Service token + network path** (`WOM_SERVICE_TOKEN`, VM→backend URL) — set and shared? (per `docs/GO-LIVE.md`)
6. **Confirm** you'll keep `docs/USER-MANUAL.md` updated as features flip to live.

---

## 5. Pointers

- App (single file): `preview/index.html` · backend root route: `backend/app/main.py` (`@app.get("/")`).
- Manual: `docs/USER-MANUAL.md` · Go-live runbook: `docs/GO-LIVE.md` · Integration spec: `docs/HERMES-INTEGRATION.md`
  · Deploy/restart: `docs/DEPLOY-RESTART.md` + `tools/deploy.sh` + `deploy/wom.service`.
- Repo: private GitHub `wise-old-man-os`, branch `main`. The host pulls `main` on cron; static UI changes need no restart.
