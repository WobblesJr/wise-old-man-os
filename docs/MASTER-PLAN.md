# Wise Old Man OS — Your Master Plan
*The one page to read at 7am. Compiled by a 9-agent pass (5 mapped every request against the code, 3 critics aligned on completeness/order/plain-English, 1 synthesized).*

## Where we are, and what "done" looks like

The whole system is **built and running on mock data** on your PC — the dashboard, the backend, the vault, the agent wiring. Nothing has been sent or deployed for real yet (that was the hard rule this session). **"Done"** means one thing: a live, login-locked site at **https://wise-old-man.xyz** that you open from your phone or anywhere, where your real tasks live in a GitHub-backed vault, Hermes (your agent in the Ubuntu VM) reads the board and posts its thinking, and bad data can't sneak in. We're not starting from scratch — we're flipping a finished machine from "demo mode" to "live and mine only." The path below is mostly **you handing over a few keys and clicking through Cloudflare once**; the rest is us building.

---

## What's already built and working (the foundation is real)

- **The dashboard UI** (`preview/index.html`) — your no-install, click-around command center. Works today.
- **Google-Sheets-style task grid** — click-and-type cells, sortable columns, the **"!" P0–P4 priority column** colored by who set it (you / Hermes / the rules), context-aware quick-add. Done.
- **Desktop + mobile layouts** — sidebar, max-width container, breakpoints. Done.
- **The vault** — a real three-tier Obsidian-style vault (`00-raw / 10-wiki / 20-outputs`) with your two projects, master files, and product reference. **Verified: all 35 folders have their `index.md` "map" — no gaps.** It's a real git repo and commits every edit locally.
- **Durable storage** — tasks save to markdown and git-commit on every change. Survives restarts.
- **War-Board band** — the morning brief: "X dates in danger / Y meetings," risk pips, a "START WITH" highest-leverage row. Done.
- **Hermes belief layer (live wire)** — the violet "✦ HERMES" strip, separate from the rules engine, updates instantly over a live connection. Done (on seed data).
- **Multi-agent console** — the Hermes / Claude Code / Cowork switch on one shared log. Done (canned replies for now).
- **Phone install (PWA)** — Apple icons, manifest, service worker all wired. Installs the moment the site is live over HTTPS.
- **The auth gate** — backend lock that allows only `gavin.watson.jr@gmail.com` plus Hermes's token. Built and tested; just switched **off** by default.

**Translation:** the screen you use, the place your data lives, and the safety lock are all done. What's left is connecting it to the real world and adding the last few panels.

---

## About two things you'll see everywhere

**Your `.env` file** is just a plain-text settings file in the project root, one `SETTING=value` per line (copy `.env.example` to `.env` to start). You can edit it in Notepad and restart the app — **but most `.env` edits are things Claude can do for you. Just say which value to set.** When a step says "set X in .env," assume Claude does it unless it's a secret only you can mint.

**Making a secret** (you'll need two): open https://www.uuidgenerator.net and copy the result, or run `openssl rand -hex 32`. ⚠️ The **service token** must be pasted *identically in two places* — the backend `.env` AND Hermes in the VM — or Hermes can't connect. The **session secret** is a different, second random string used in only one place.

---

# Section 1 — Go live & lock it down (Cloudflare + login)
*Why it matters: this is the difference between a demo on your PC and a real app on your phone, locked to you.*

### ⛳ DECIDE THIS FIRST (it collapses ~6 other items)
**Use Cloudflare Access for login — recommended.** It does the "Sign in with Google" for you, with zero login code to build. Choosing this means the app-level Google login, the session-secret worry, and the "real token exchange" code all become **N/A**. *Reply only if you want app-level login instead.*

**The whole go-live, in order (~30 minutes, one sitting):**

1. **[we build]** Put two real secrets in `.env` — `WOM_SERVICE_TOKEN` and `SESSION_SECRET`. (You generate them; we paste them — see "Making a secret" above.)
2. **[you]** Pick the always-on machine. **Your Ubuntu VM is the obvious home** (Hermes lives there too).
3. **[we build]** Run the backend on that machine on port 8787.
4. **[you]** Install Cloudflare's `cloudflared` and create a named tunnel pointing `wise-old-man.xyz` → `localhost:8787`. (A few one-time commands; we hand you the exact lines.)
5. **[you]** In Cloudflare DNS, point `wise-old-man.xyz` at the tunnel. HTTPS turns on automatically and free.
6. **[you]** In Cloudflare Zero Trust: add **Google sign-in**, add an **Access app** for the domain, add an **Allow policy → your email only**, and add a **service-token policy named "hermes"** (save the two header values it gives you — Hermes needs them).
7. **[we build]** Set `WOM_AUTH_MODE=cloudflare` in `.env`.
8. **[you]** Open the site in a **private browser window** — you should be forced to Google sign-in, and only your email gets through. Then on your iPhone: Safari → Share → **Add to Home Screen**.

> **YOU DO:** pick the host (VM), run the cloudflared install/login, click through the Cloudflare Access setup, generate two secrets, do the final private-window + phone test.
> **CLAUDE BUILDS:** all `.env` edits, running the backend, the auth-mode switch.

---

# Section 2 — Turn on Hermes (the brain)
*Why it matters: Hermes is what makes this self-driving instead of a static board. Everything Hermes will call already exists — the brain itself just needs to wake up in the VM.*

**The dashboard side is 100% done.** Every endpoint Hermes needs to read the board and write its beliefs, priorities, and console messages already exists and is proven over the live wire. Two things gate it:

1. **[you]** **Set the real service token** (Section 1, step 1) in both the backend `.env` and the VM. *Until this is a real value, Hermes is silently blocked from every write — the code rejects the placeholder token on purpose.*
2. **[you]** **Choose the network path** from the VM to the backend: either the Windows host IP on port 8787, or the public `wise-old-man.xyz` tunnel once it's up.

Then, to stand up the brain itself:

3. **[you]** Put your **Anthropic API key** in the VM (`ANTHROPIC_API_KEY`).
4. **[we build]** Install the Claude Agent SDK in the VM and stand up the always-on **think-loop**: read the board → think → post what it believes. (Full recipe in `docs/HERMES-SETUP.md`.)
5. **[we build]** Define the five helper sub-agents (triage, drafter, scheduler, researcher, verifier) so Hermes can hand off scoped jobs and have the verifier double-check drafts before they become approvals.
6. **[you]** **Decide Hermes's default reasoning model.** *Recommend Opus for orchestration, with cheaper models for high-frequency chores — model IDs are already in the docs. Reply only to change.*

> **YOU DO:** Anthropic key in the VM, the service token, the network path, the model pick.
> **CLAUDE BUILDS:** the think-loop, the sub-agents, all wiring.

---

# Section 3 — Storage & the vault (GitHub / Obsidian / Drive)
*Why it matters: today your tasks are safe on one PC. This makes them recoverable from anywhere and version-controlled in GitHub — and stops bad rows at the door.*

### 3a. The bouncer at the door (QC gate) — **DO THIS BEFORE ANY OFF-MACHINE WRITE**
This is the fix for the exact problem you complained about: descriptions bleeding across cells, one cell with three things jammed in, made-up drawing numbers. It's a **bouncer for your task list**: it auto-fixes harmless mistakes (a stray `|`, a line break) and **refuses** anything it can't safely fix, telling you exactly what to split. Every catch is logged.

1. **[we build]** Write the rulebook (`tasks.yaml`) — what each column may hold — from the spec that's already drafted.
2. **[we build]** Build the bouncer and wire it as a **blocking check in front of every save** (grid edits, quick-add, and the vault writer). Safe fixes save cleaned; ambiguous ones are refused with a plain reason. Every decision logged.
3. **[you]** Say **yes to two short lists** — the allowed **Action** words (`action/wait/hold/read/event`) and **Status** words (`not_started/in_progress/completed/delegated/blocked`). *Recommend: approve as-is. Keep Category free-text for now until your projects are named for real.*

> **YOU DO:** nothing to start — just approve two short word-lists.
> **CLAUDE BUILDS:** everything. No credentials needed; buildable now.

### 3b. Push the vault to GitHub (off your PC)
*Note: the "WOM_VAULT_PUSH" flag people may reference **does not exist yet** — it's a small thing we build, not a switch already sitting there.*

4. **[you]** Create an empty **private GitHub repo** (recommend its own repo, e.g. `wom-vault`).
5. **[you]** Mint a **GitHub Personal Access Token** with repo-write scope (only you can do this) — we paste it into `.env`.
6. **[we build]** Attach the remote, do the first push, then **add** the `WOM_VAULT_PUSH` option (default off) **and** the push-on-commit code, with failures made non-fatal so a dropped network never blocks a save. **Goes live only after the QC gate (3a) is in front of writes.**
7. **[you]** Test: edit one task in the dashboard, confirm it shows as a new commit in GitHub.

### 3c. Your two real project names *(optional, 10 seconds)*
8. **[you]** Tell us your two active project names to replace `project-alpha` / `project-beta`. *(Optional: open the vault in Obsidian once to eyeball it.)*

### 3d. Drive → vault one-way mirror
9. **[you]** **One decision, answered once** (it also unblocks the hourly Ingest loop later): *which Google Drive folder holds the Docs/Sheets your skills will read?* If unsure, point to the folder your two active projects live in — we can add more. You'll find it just by opening that folder in Drive.
10. **[you]** Do a one-time rclone Google sign-in (~3 minutes; we walk you through it).
11. **[we build]** A small hourly sync job mirroring that folder into `00-raw/drive` (Drive stays the source of truth; the vault never writes back).

> **YOU DO:** make the private repo + GitHub token, name your two projects, pick the one Drive folder, do the rclone sign-in.
> **CLAUDE BUILDS:** the QC gate, the push code + flag, the Drive sync job.

---

# Section 4 — Finish the dashboard (grid / spacing / toggle / War-Board)
*Why it matters: the screen you look at daily. All of this is pure front-end on the canonical preview — no infrastructure, mostly buildable now.*

1. **[we build] Spacing rhythm.** Add the `8/12/16/24` spacing tokens and replace the hand-typed pixel values so nothing feels randomly cramped or loose. Collapse empty bands to zero height. *(Defined on paper; not yet applied — a clean cleanup pass.)*
2. **[we build] War-Board "One Thing" Do/Chase flip.** When the ball's on **you**, show a red **"Do"** button; when you're waiting on someone, show an amber **"Chase {name}"** that drafts a nudge.
3. **[we build] Batch-Approve Queue.** Wire the Approve buttons to the real decision endpoint (it already exists) and add an **"Approve all low-risk (N)"** button. Group the auto-chase drafts and approvals into one queue with a clear count.
4. **[we build] Delegation badge + drawer.** A small "N running, M awaiting you" pill plus a panel listing what Hermes handed to Claude Code / Cowork. (Renders mock data until the bridge in Section 5 lands.)
5. **[we build] 3-way scope toggle — Personal | Both | Work.** "Both" merges everything into one risk-ranked list with small **P/W chips** so you can tell which world each item came from.
   - **[you] One quick visual call:** the accent color for "Both." *Recommend **neutral slate grey** so neither world's color dominates. Reply only to change.*
6. **[we build] Login chip + logout.** Show your signed-in email in the header with a logout button. *(With Cloudflare Access, the login redirect is handled for you — this just displays who's in and lets you sign out.)*
7. **[you] One strategic call on the React app.** There are two versions of the screen: the **simple one you actually use** (the preview) and a fancier React one that needs a developer tool (Node) just to open, is currently *behind* the preview, and gives you nothing extra today. **Recommendation: ship the simple one; we put the fancier one on ice and stop splitting effort. You lose nothing visible.** *One yes/no — say the word if you ever want the fancier track revived.*

> **YOU DO:** pick the "Both" accent color (or accept grey), the React yes/no, and confirm the chase ladder wording (see "What I need from you").
> **CLAUDE BUILDS:** everything else here.

---

# Section 5 — Skills, automation & QC (the self-improving part)
*Why it matters: this is where the system grows on its own over time — but correctly sequenced so it never runs before its data or its engine exist.*

1. **[we build] The QC gate** — already covered in 3a. It's listed here too because it's the foundation for everything that writes. It comes **first**.
2. **[we build + you] Your first skill.** Skills are markdown files you run by hand, then **you** manually promote to scheduled jobs — nothing auto-promotes. We write the template and **one** real skill with you (recommend **rfi-drafter** or **inbox-triage**); it starts in "draft" and only writes to the drafts folder, so it can't do anything risky.
   - **[you]** Pick the first skill, and paste **one or two examples of a "good" output** (e.g. a well-written RFI) so it learns your voice.
3. **[we build] The delegations bridge** (`/api/delegations*`). Lets you or Hermes hand a coding job to Claude Code / Cowork on your Windows machine. **Built token-guarded from the first commit** so the public site can never trigger local agents. **Safety promise, tested:** a finished job lands as **"needs approval"** and shows in the Batch-Approve Queue — *it never writes to your tasks until you tap Approve.* Dispatch is one tap; apply is a second tap; never silent.
   - **[you]** The exact command to launch Claude Code (and confirm Cowork = Claude Cowork, where it runs, and its launch command). Until you give these, we keep a **mock runner** so the whole loop is demoable.
4. **[we build] Jobs & loops** — run by Hermes's tick-loop once the VM is up. Build the **inward-only, lowest-risk** loops first: **Synthesis** (distills new raw items into linked Wiki notes) and the **7am Reflection** (yesterday's recap + today's risks + top 3 improvements). Then Ingest and Execution. The **Improvement** loop (which proposes sharper prompts from your approve/reject pattern) comes **last** and never changes itself without your tap.
   - **[you]** Where you want the **7am reflection** delivered. *Recommend: posted to the board + a vault note, weekdays only. Reply only to change.*
   - **Interim:** a Cloudflare Cron Trigger can ping the War-Board endpoint at 6am so your morning brief fires **even before** the Hermes loop exists.

> **YOU DO:** pick the first skill + paste a sample output, give the Claude Code / Cowork launch commands, choose where the 7am note lands.
> **CLAUDE BUILDS:** the gate, the skill template + first skill, the delegations bridge + mock runner, the loops.

---

# Section 6 — Personal Google live (the biggest jump in usefulness)
*Why it matters: this flips your tasks from mock to your real ones. Your personal Google is available now; work Google is deferred.*

1. **[you]** Grab your **Sheet ID + tab name**: open your G-Suite Dashboard sheet — the ID is the long code in the address bar: `docs.google.com/spreadsheets/d/`**`THIS-LONG-CODE`**`/edit` — copy that and the tab name at the bottom (e.g. `Tasks`). A 2-minute copy-paste.
2. **[you]** One Google sign-in granting **Sheets read + write** (write is required so the dashboard can push edits back).
3. **[we build]** The live two-way Sheet sync (read rows, append on quick-add, update on edit) **with an echo-guard built in** so the two sides never fight. **Goes live only after the QC gate protects it.**
   - **[you] Conflict rule.** *Recommend: **newest edit wins, loser logged.** Reply only to change.*
4. **[we build] Priorities round-trip.** Make the priority-setter also write `priorities.json` first (so the file is a true mirror), then add a refresh-time loader that validates each value is `0–4` and reads it back. *(Order matters so an empty file never wipes Hermes's live priorities.)*

> **YOU DO:** copy the Sheet ID + tab, one Google sign-in, confirm the conflict rule.
> **CLAUDE BUILDS:** the live connector, the echo-guard, the priorities loop.

---

# ✅ Do this first — the ordered milestones

| # | Milestone | Needs from you | Who |
|---|-----------|----------------|-----|
| **0 ✅ DONE** | **QC bouncer built + wired into every save** (grid edits, quick-add, vault writer). Auto-repairs pipes/dates/synonyms, blocks the unfixable, logs every call. Verified end-to-end. | (used default word-lists — change anytime) | ✅ |
| **1** | **Two secrets in `.env`** + pick the VM→backend network path. *Unblocks the entire Hermes column.* | Generate 2 secrets, pick path | you + we |
| **2** | **GitHub push live** — private repo + token, attach remote, add `WOM_VAULT_PUSH`. *After QC gate.* | Make repo + token | you + we |
| **3** | **Priorities round-trip** — writer first, then loader. | — | we build |
| **4** | **Go live + locked** — VM → tunnel → Cloudflare Access → `AUTH_MODE=cloudflare` → private-window test → phone install. | Cloudflare clicks, cloudflared login | you + we |
| **5** | **Hermes goes live** against the now-locked board (token + network already done). | Anthropic key in VM | you + we |
| **6** | **Delegations bridge** — token-guarded, mock runner, no-silent-autonomy test. | Launch commands (later) | we build |
| **7** | **Finish the dashboard** — spacing, Do/Chase flip, Batch-Approve, delegation drawer, Both toggle, login chip. | "Both" color, React yes/no | you + we |
| **8** | **Live Sheet sync** — last write path on. *After QC gate.* | Sheet ID + tab, Google sign-in | you + we |
| **9** | **Automation engine** — Drive sync → Hermes loop → Synthesis + 7am Reflection → promote skills to jobs. Interim: Cloudflare cron for the 6am brief. | Drive folder, rclone sign-in | you + we |
| **10** | *(lowest)* React parity catch-up when Node is available — or formally retire it. | One yes/no | you |

---

# 📋 What I need from you (gather these once)

**Keys & secrets**
- [ ] **Anthropic API key** (goes in the VM)
- [ ] **Two random secrets** — one service token (pasted in *two* places), one session secret (uuidgenerator.net or `openssl rand -hex 32`)
- [ ] **GitHub Personal Access Token** with repo-write scope
- [ ] **Personal Google sign-in** with Sheets read + **write**, plus a one-time **rclone** Google sign-in for Drive

**Accounts & hosting**
- [ ] **Cloudflare account** with `wise-old-man.xyz` added; click through Zero Trust (Google sign-in + Access app + Allow-your-email policy + a "hermes" service token)
- [ ] **Your Ubuntu VM** confirmed as the always-on host; run the `cloudflared` install/login
- [ ] A **private GitHub repo** for the vault (e.g. `wom-vault`)

**Copy-paste lookups**
- [ ] **Sheet ID + tab name** from the address bar of your G-Suite Dashboard sheet
- [ ] **The one Drive folder** that feeds your skills (answer once — unblocks Drive sync *and* the Ingest loop)

**Quick decisions (defaults recommended — just nod)**
- [ ] Login = **Cloudflare Access** ✔ recommended
- [ ] "Both" accent = **neutral slate grey** ✔
- [ ] Sync conflict = **newest edit wins, loser logged** ✔
- [ ] 7am reflection = **board + vault note, weekdays only** ✔
- [ ] React app = **put on ice, ship the preview** ✔
- [ ] Approve the **Action / Status** word-lists as drafted ✔
- [ ] **Chase ladder:** who is "the super" you escalate to, and should escalation ever copy the GC/owner? *Recommend: escalate internally to your super first, never auto-copy the GC/owner without your tap.*
- [ ] **Claude Code + Cowork launch commands** (needed only when we wire the real delegation runner — mock works until then)

---

**Status: the foundation is done and real — the screen, the vault, the safety lock, the live agent wire all work on mock data. The path to live is mostly you handing over a handful of keys and one Cloudflare click-through; we build the rest, in the order above, starting with the bouncer that keeps your task list clean.**
