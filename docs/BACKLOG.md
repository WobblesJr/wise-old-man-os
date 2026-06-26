# Backlog (parked ideas — not building yet)

## Auth / access control  🅿️ backburner (Gavin's call, 2026-06-25)
**Goal:** host `wise-old-man.xyz` publicly but gate the board so only Gavin can see it; later,
support multiple users who can each configure their own board.

**Why parked:** proceed with the current single-user, no-login mock model first.

**When we build it — sketch (so it's not lost):**
- Phase A — single-user gate: one login (password or a magic link / passkey) in front of the whole
  app. Simplest secure option behind the Cloudflare tunnel: **Cloudflare Access** (zero app code —
  Google/email gate at the edge) OR a tiny FastAPI session/JWT middleware + a login screen.
- Phase B — multi-user: a `users` table, per-user scope/config (their own task sheet id, skills,
  cron set, layout registry), row-level data isolation, and an admin who can invite/configure.
- Ties to the registry-driven layout: each user gets their own section/skill/cron registry.

**Where it'll plug in:** FastAPI middleware + `users`/`sessions` tables; the frontend gains a login
route; `WOM_PUBLIC_URL` already set. No data model today blocks this.

---

## Other parked ideas
- (add here as they come up)
