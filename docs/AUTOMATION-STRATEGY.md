# Wise Old Man OS — Automation & Growth Strategy
### Compiled for your ~7am review. Read top-to-bottom or jump by section; each ends with a **First move**.

This is the blueprint for the "final automation" phase: how you grow new skills and automate
them, how information flows through a **three-tier vault (Raw → Wiki → Outputs)**, the **loop
engineering** that makes the system self-improving, and the **QC gates** that stop malformed
outputs (like the multi-cell descriptions you flagged). Everything is Cloudflare-hosted and
gated to your Google login. Grounded in what's already built (see `BUILD-LOG.md`, `docs/GO-LIVE.md`,
`docs/HERMES-SETUP.md`).

**Your decisions baked in:** skills = markdown files you **manually promote**; Drive → vault is
**one-way**; QC is a **schema + blocking gate before any write**; this doc is compiled now.

**Where to start:** Section 7 is the sequenced rollout. Sections 1–6 are the design behind it.

---

## 1. The three-tier vault (Raw → Wiki → Outputs)

Your Obsidian vault becomes the brain, in three folders that mirror how information matures:

```
vault/
├─ 00-raw/          # RAW: everything ingested, unprocessed
│   ├─ email/             # pulled emails (one note per thread)
│   ├─ drive/             # synced Google Docs/Sheets (one-way Drive→vault)
│   ├─ web/ · feeds/      # clipped articles, feed pulls
│   └─ capture/           # your quick-captures, voice notes
├─ 10-wiki/         # WIKI: structured, context-linked knowledge (self-organizing)
│   ├─ projects/          # Project Alpha, Beta … (rolled-up state)
│   ├─ people/            # Turner GC, Priya, subs … (who owes what, history)
│   ├─ topics/            # RFIs, submittals, manpower, VE decisions …
│   └─ index.md           # the map of content (auto-maintained backlinks)
├─ 20-outputs/      # OUTPUTS: the actual deliverables agents produce
│   ├─ drafts/            # RFI cover notes, emails, schedules (await your approval)
│   ├─ schedules/         # manpower xlsx, lookaheads
│   └─ reports/           # morning briefs, weekly rollups
├─ skills/          # skill definitions (Section 2)
├─ jobs/            # promoted skills on a schedule (Section 3)
└─ .wom/            # sync state, schema, QC logs
```

**How information matures (the refinement pipeline):**
- **Raw** is append-only and dumb. Drive files, emails, captures land here verbatim. Nothing is
  trusted yet. This is what "connects everything to the machine code."
- **Wiki** is where Hermes *synthesizes*: as raw items get used, an agent distills them into
  context-linked notes (a person note accretes their open balls; a project note rolls up its RFIs,
  schedule risk, decisions). This is your second brain — it gets *neater the more you use it*,
  because the synthesis loop (Section 4) runs on access.
- **Outputs** are deliverables: an agent reads Wiki + Raw, produces a draft/schedule/report, and
  drops it here as a **pending approval** (draft-everything — nothing leaves without your tap).

**Why three tiers matter for automation:** each tier has a *different writer and a different QC
bar.* Raw = ingest validators (is this a well-formed email/doc?). Wiki = synthesis QC (is this
distilled correctly, properly linked, no hallucinated facts?). Outputs = deliverable QC (schema +
does-it-do-the-job?). Mixing them is what produces messy data; separating them is the cure.

**Sync:** Drive → `00-raw/drive/` is **one-way** (Drive is the source; vault never overwrites
Drive). Use `rclone` (a single `rclone sync gdrive:WOM 00-raw/drive` on a cron) or the Drive API in
Hermes. The whole vault is a git repo Hermes pushes; the dashboard reads a fast cache of it.

> **First move:** scaffold the three folders + `.wom/` in `backend/data/vault/`, commit. Decide the
> Drive folder that feeds `00-raw/drive/` (which Docs/Sheets "support skills and jobs").

---

## 2. Skill system — define → (you) promote → automate

A **skill** is a markdown file in `vault/skills/` with structured frontmatter. It is the unit you
grow. You write/refine it, run it manually, and **manually promote** it to a job when it's proven.

**Skill file template** (`vault/skills/rfi-drafter.md`):
```yaml
---
name: rfi-drafter
status: draft            # draft → active(manual) → promoted(scheduled)
purpose: Draft a construction RFI from project context
trigger: manual          # manual | event:<name> | cron:<expr> (set on promote)
inputs: [project, question, drawing_refs]
reads: [10-wiki/projects, 00-raw/drive]      # vault paths it may read
writes: 20-outputs/drafts                     # where its output lands
output_kind: email_send                       # maps to an approval kind
model: claude-opus-4-8
qc: [schema, no-hallucinated-refs, tone-professional]   # QC checks (Section 5)
promote_after: manual                         # YOUR choice — never auto
owner: hermes
---

## Procedure
1. Pull the project's open items + the referenced drawings from Wiki/Raw.
2. Draft the RFI in the firm's format; cite only refs that exist in `reads`.
3. Emit as a pending approval in `20-outputs/drafts/` + an approval card on the board.

## Examples / few-shot
(paste 1–2 good RFIs here — this is how the skill "learns" your voice)
```

**Lifecycle (your manual-promote model):**
1. **Draft** — you (or Hermes) write the skill file. Status `draft`.
2. **Active (manual)** — you invoke it from the console ("run rfi-drafter for Alpha"). It produces
   an output → approval. Each run is logged with its QC result.
3. **Promote** — when it's reliably good, **you** flip `status: promoted` and set a `trigger`
   (event or cron). Now it's a job (Section 3). *Nothing auto-promotes — your explicit call.*

**Discovery + display:** Hermes scans `vault/skills/*.md` (registry-driven — matches the "living
system" north star). The dashboard's **Cockpit → Skills inventory** (already built) lists them with
status; promoting one makes it appear in **Scheduled jobs**.

**Growing skills safely:** a new skill starts read-mostly and output-to-drafts (approval-gated), so
a half-baked skill can't do harm — worst case it drafts something you reject. QC (Section 5) runs on
every run regardless of status.

> **First move:** drop the template above as `vault/skills/_TEMPLATE.md`, plus one real skill you
> run weekly (rfi-drafter or inbox-triage). Run it manually once; eyeball the output.

---

## 3. Jobs & scheduling (Cloudflare-centric)

A **job** is a promoted skill bound to a trigger. Two scheduling layers:

- **Hermes loop (primary):** Hermes is always-on in the VM and IS the scheduler — a tick loop that,
  each interval, checks `vault/jobs/` for due crons and event subscriptions, runs them (spawning
  sub-agents), and writes results back. This is where "heavy lifting happens with Hermes."
- **Cloudflare (edge + triggers):** the tunnel serves `wise-old-man.xyz`; **Access** gates it to
  your Google login; optionally **Cloudflare Cron Triggers / Workers** can ping
  `POST /api/warboard/run` or `/api/refresh` on a schedule as a redundant heartbeat if the VM sleeps.

**Job definition** = the promoted skill's frontmatter (`trigger: cron:0 6 * * 1-5`). The cockpit
already renders a jobs table; promoting writes a row.

**The standing jobs to seed** (most already exist as endpoints): morning War-Board (6am),
chaser sweep (15m), refresh/sync (10m), Drive→raw ingest (hourly), Wiki synthesis (nightly),
vault git push (nightly), the **7am reflection** (Section 4).

> **First move:** pick the 3 jobs you want first (suggest: 6am War-Board, hourly Drive ingest,
> nightly Wiki synthesis). Everything else can promote later.

---

## 4. Loop engineering — the self-improvement engine

"Loop engineering" = designing small, composable loops, each with a **trigger → transform → QC
verify → output → stop condition**. Small loops compose into the system's behavior. Here are the
loops your system runs, mapped to the three tiers:

| Loop | Tier | What it does | Stop condition |
|------|------|--------------|----------------|
| **Ingest** | Raw | Pull new email/Drive/feeds → normalize → file in `00-raw/` | nothing new |
| **Synthesis** | Wiki | Take fresh Raw → distill into context-linked Wiki notes; backlink people/projects/topics | loop-until-dry (2 clean passes) |
| **Execution** | Outputs | Due skills run → produce drafts/approvals | job list empty |
| **Improvement** | meta | Review outputs + QC failures + your approve/reject signal → propose skill/prompt edits | propose-and-approve (you decide) |
| **Reflection (7am)** | meta | Summarize yesterday, surface what's at risk today, list the 1–3 improvements worth making | once/day |

**Loop design rules (the discipline):**
1. **One job per loop.** A loop that both ingests and synthesizes is two loops — split them.
2. **Always verify before writing.** Every loop ends in a QC gate (Section 5), never a raw write.
3. **Bounded.** Each loop has a token budget and a stop condition (count, until-dry, or time).
4. **Idempotent.** Re-running a loop must not duplicate (dedupe by id / content hash).
5. **Propose-and-approve for anything outward or destructive.** Inward synthesis can be autonomous;
   outputs and skill changes are drafts you approve.

**Workflow patterns to reach for** (these are the multi-agent shapes that make loops *good*):
- **Fan-out → adversarially verify:** generate with N agents, then have skeptic agents try to
  *refute* each finding; keep only survivors. Use for: bug-finding, fact-checking Wiki synthesis.
- **Loop-until-dry:** keep finding until K consecutive empty passes. Use for: ingest, audit sweeps.
- **Judge panel:** N independent attempts, scored by judges, synthesize the winner. Use for: drafting
  important deliverables (a recovery plan, a tricky RFI).
- **Perspective-diverse verify:** verify with distinct lenses (correctness, schema, tone, does-it-
  reproduce) instead of N identical checkers. Use for: QC of outputs.
- **Completeness critic:** a final agent asks "what's missing?" Its findings become the next loop.
  Use for: the 7am reflection and weekly rollups.

**The improvement loop is how you "improve everything":** it watches three signals — QC failures,
your approve/reject ratio per skill, and time-to-close on tasks — and proposes concrete edits
(a sharper prompt, a missing QC check, a new few-shot example). You approve; the skill file updates;
the system gets better. This is the engine of growth.

> **First move:** stand up just the **Synthesis loop** + the **7am Reflection** first — they create
> the most leverage (a self-organizing Wiki + a daily plan) and are low-risk (inward, no outward sends).

---

## 5. QC agents & the schema gate (no more malformed cells)

**The defect you flagged**, generalized: agent/LLM writes can violate structure — a description
with embedded `|`/newlines that shatters a row, a field stuffed with multiple values, a fabricated
drawing reference. The data today is clean; this gate keeps it that way as agents start writing.

**(a) Column schema** — one source of truth for what each field may contain. Example for tasks:
```yaml
# vault/.wom/schema/tasks.yaml
columns:
  description: { type: text, single_line: true, no_pipes: true, max_len: 160 }
  start|followup|due: { type: date, format: YYYY-MM-DD, nullable: true }
  ball_in_court: { type: text, single_value: true }
  category: { type: enum, source: 10-wiki/projects }      # must be a known project/category
  action: { type: enum, values: [action, wait, hold, read, event] }
  status: { type: enum, values: [not_started, in_progress, completed, delegated, blocked] }
  priority(!): { type: int, range: [0,4], source: overlay }   # Hermes overlay, not free-text
```

**(b) The blocking QC gate** — every write (Hermes API write, inline grid edit, skill output) passes
through QC *before commit*:
1. **Structural validator** (deterministic, fast): checks the schema. Auto-repairs the safe stuff
   (escape pipes, collapse newlines, trim, coerce dates). **Blocks** the ambiguous stuff (a
   description with 3 jammed values → reject with "split into Description + Subcategory + a note").
2. **Semantic QC agent** (LLM, for content): does this make sense, is it consistent with Wiki, are
   all references real (no hallucinated drawing/spec numbers)? Flags or blocks.
3. **Output QC** (for deliverables): perspective-diverse verify — correctness, tone, completeness.

**Block vs auto-repair:** repair where the fix is unambiguous and lossless; block + return a precise
error where it isn't (the agent retries with the error as feedback — the same retry mechanism
already used for structured outputs). Every QC decision is logged to `.wom/qc-log/` so you can audit
what got repaired/blocked and tune the schema.

**QC roster (the agents):** Structural Validator · Semantic Reviewer · Reference Checker ·
Tone/Format Checker · Completeness Critic. Hermes spawns the relevant ones per write type.

**Where it plugs into the code:** a `qc_gate(write)` step in the write path — for the dashboard,
that's `routers/tasks.py` (PATCH/quick-add) and `GitVaultStore.update_task`; for Hermes, it's a
required call before any `POST /api/*` write. Reject → 422 with the reason; repair → commit the
cleaned value + note.

> **First move:** write `tasks.yaml` schema + a deterministic structural validator, and wire it as a
> blocking gate on `GitVaultStore` writes. That alone kills the malformed-cell class immediately.

---

## 6. Cloudflare & access (everything through Cloudflare)

- **Tunnel:** `cloudflared` → backend `:8787`; DNS `wise-old-man.xyz` → tunnel; HTTPS (required for
  the PWA install). The site is your access layer from anywhere.
- **Access (Zero Trust):** Google IdP + Allow-policy = your email only → public-but-locked-to-you,
  near-zero app code. **Service Token "hermes"** for the VM's server-to-server writes. (Full steps in
  `docs/GO-LIVE.md` §3.) The app's auth gate is already built as defense-in-depth.
- **Optional Workers/Cron Triggers:** an edge heartbeat that pings `/api/warboard/run` and
  `/api/refresh` so the morning brief fires even if the VM is mid-reboot.

> **First move:** create the tunnel + an Access app with your email allowlist + the hermes service
> token. That's the whole "make it live and mine-only" gate.

---

## 7. Putting it into motion — sequenced rollout (start ~7am)

Each phase is independently valuable; do them in order, stop anywhere and you still have a working
system. ✅ = already built this far.

**Phase 0 — Foundations (✅ mostly done)**
- ✅ Durable git-vault task store · ✅ Sheets-style editable grid · ✅ auth gate · ✅ Hermes belief
  layer + multi-agent console · ✅ War-Board, chaser, priority overlay.

**Phase 1 — Structure + safety (this is the 7am starting line)**
1. Scaffold the **three-tier vault** (`00-raw / 10-wiki / 20-outputs / skills / jobs / .wom`).
2. Write the **tasks schema + blocking QC gate** (Section 5 first-move) — stops bad writes now.
3. Drop the **skill template** + author **one real skill**; run it manually.

**Phase 2 — Flow + skills**
4. **Drive → `00-raw/` one-way sync** (rclone cron) for the Docs/Sheets that support skills/jobs.
5. **Synthesis loop** (Raw → Wiki) + **7am Reflection** loop — the self-organizing brain + daily plan.
6. Promote 2–3 skills to **jobs**; seed the standing crons.

**Phase 3 — Live + locked**
7. **Cloudflare tunnel + Access** → `wise-old-man.xyz`, your email only, hermes service token.
8. **Personal Google live** (Sheets/Gmail/Cal adapters; `WOM_DATA_MODE=live`) — two-way sheet↔vault.
9. **Improvement loop** on (proposes skill/prompt edits from QC + your approve/reject signal).

**Phase 4 — Compounding**
10. Each new skill follows the same path (draft → manual run → you promote → QC-gated job).
11. The Wiki keeps self-structuring; the 7am reflection keeps surfacing the next improvement.

**What needs you (not me):** the Cloudflare tunnel/Access setup, the Anthropic key + service token
for Hermes, the Drive folder choice, and the manual promote calls. Everything else I can build.

---

## Appendix — decisions captured & open questions for next round
**Captured:** skills = markdown, **manual promote** · Drive→vault **one-way** · vault tiers
**Raw/Wiki/Outputs** · QC = **schema + blocking gate** · doc compiled now.

**Open (answer when you review, so I can build Phase 1 cleanly):**
1. Which **Drive folder(s)** feed `00-raw/drive/`? (the Docs/Sheets that support skills/jobs)
2. **First real skill** to build with you — rfi-drafter, inbox-triage, or the meeting-loop-closer?
3. **Wiki granularity** — notes per project+person+topic (recommended), or start with just projects?
4. **Reflection time** — 7am weekdays only, or daily? Delivered where (board + Discord + a vault note)?
5. Any **hard "never auto" lines** beyond outward sends (e.g., never auto-edit a Wiki fact sourced
   from a contract)?
