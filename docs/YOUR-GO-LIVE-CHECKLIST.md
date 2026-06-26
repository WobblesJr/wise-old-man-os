# Your go-live checklist — everything to do OUTSIDE this terminal

These are the only things **I can't do for you** — accounts to create, sign-ins, and clicks. Gather
them and I wire everything up. Grouped by system, roughly in order. (The build/plumbing is done by me;
see `docs/MASTER-PLAN.md` for who-does-what per step.)

---

## A. Accounts to create (if you don't have them)
- [ ] **Cloudflare** account, and add **wise-old-man.xyz** to it (point the domain's nameservers at Cloudflare). Free.
- [ ] **Cloudflare Zero Trust** (a.k.a. Access) — enable it on the account. Free tier is plenty.
- [ ] **GitHub** account + a new **private** repo named `wom-vault` (empty — no README).
- [ ] **Anthropic** account with an **API key** (this powers Hermes's thinking). console.anthropic.com → API keys.

## B. Secrets to generate (you make them, I paste them)
- [ ] **Service token** — one long random string. I'll give you a one-command generator. It goes in **two** places (backend + Hermes) and must match.
- [ ] **GitHub Personal Access Token** — repo-write scope, for pushing the vault. github.com → Settings → Developer settings → Tokens.
- [ ] *(Only if you pick app-level login instead of Cloudflare Access)* a **session secret** — second random string. **Recommended: use Cloudflare Access and skip this.**

## C. Cloudflare clicks (Zero Trust → ~15 min, one sitting)
- [ ] **Tunnel:** install `cloudflared` on your always-on machine; create a named tunnel routing **wise-old-man.xyz → localhost:8787**. (I'll hand you the exact commands.)
- [ ] **DNS:** point `wise-old-man.xyz` at the tunnel (Cloudflare does this for you when you create the route).
- [ ] **Login method:** Zero Trust → Settings → Authentication → **add Google**.
- [ ] **Access application:** add a self-hosted app for `wise-old-man.xyz`, session ~30 days.
- [ ] **Allow policy:** Include → Emails → **gavin.watson.jr@gmail.com** (only you). Leave default-deny on.
- [ ] **Service token** (for Hermes): Access → Service Auth → create token **"hermes"** → save its two header values (Client-Id + Client-Secret) for Hermes's env.

## D. Your Ubuntu VM (Hermes's home)
- [ ] Confirm the VM is the **always-on host** (recommended — Hermes lives there). Decide: run the backend on the **VM** or on **Windows**; tell me the IP:port the VM uses to reach the backend (or we just use the tunnel URL).
- [ ] Put in Hermes's environment: **`ANTHROPIC_API_KEY`**, the **service token** (same value as backend), and the **network path** to the backend.
- [ ] I'll give you the **Claude Agent SDK** install + the think-loop recipe to drop in.

## E. Your Windows machine (Claude Code + Cowork)
- [ ] The exact **command to launch Claude Code** for a job (and how it takes a task/prompt).
- [ ] Confirm **"Cowork" = Claude Cowork**, where it runs (Windows or VM), and **its launch command**.
- [ ] *(Until you give these, the delegation feature runs on a mock runner — fully demoable.)*

## F. Storage — GitHub + Obsidian + Drive
- [ ] The **private `wom-vault` repo** (from A) + the **GitHub token** (from B).
- [ ] **Open the vault in Obsidian** once (folder: `backend/data/vault/`) to confirm it looks right; tell me your **two real project names** to replace project-alpha / project-beta.
- [ ] **Pick the one Google Drive folder** that holds the Docs/Sheets your skills will read.
- [ ] Do a one-time **rclone Google sign-in** for Drive (I'll walk you through the ~3-min flow).

## G. Personal Google (for live tasks/inbox/calendar)
- [ ] An **OAuth client** (Google Cloud Console → Credentials → OAuth client ID → Web app), OR just complete the **Sheets read+write** consent when prompted.
- [ ] Your **G-Suite Dashboard Sheet ID + tab name** (copy from the sheet's address bar).
- [ ] *(Work Google is deferred — nothing to do there yet.)*

## H. Quick decisions (defaults are fine — just confirm or change)
- [ ] Login = **Cloudflare Access** ✔  ·  "Both" scope color = **slate grey** ✔  ·  Sync conflict = **newest wins, loser logged** ✔
- [ ] 7am reflection = **board + vault note, weekdays** ✔  ·  React app = **shelve, ship the preview** ✔
- [ ] **Chase escalation:** who is "your super," and should it ever auto-CC the GC/owner? *(default: internal only, never auto-CC outsiders)*

---

### The absolute minimum to be "live and locked to you" (everything else can follow)
1. Cloudflare account + domain + tunnel + Access (C) → the site is public-but-yours.
2. The **service token** (B) in both places → Hermes can talk to it.
3. **Anthropic key** in the VM (A/D) → Hermes can think.
That's it for a usable live system. GitHub/Drive/Google-live make it richer and come next.
