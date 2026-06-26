# PM Autopilot & Deadline-Defense — Roadmap

> Output of a 12-agent ideation panel (ideate → debate → rank → synthesize), 2026-06-25.
> The agents audited the actual repo; recommendations cite real files/lines.

## The big idea
The dashboard today *displays* state; it doesn't *defend* dates. Everything collapses into
one move: a server-side **`risk()` field** + a working **sheet write-back spine**. Hang every
deadline feature off those two pieces so the chaser, morning brief, backsolver, and recovery
sentinel become thin consumers of one engine instead of crons that drift apart.

**Two prerequisites gate everything:**
- **`sheet_write` is a no-op** — `approvals.py:55` returns "not touched"; never calls the working
  `SheetTasks.update_task` (`sheet_tasks.py:62`). Wire `decide()` through it.
- **No scorer** — `cache.py` serves hardcoded `urgency:'high'`. One `risk()` function ends six
  surfaces each reinventing urgency.

## Deadline-defense — "Defended-Commitment Spine" (every refresh, stamped on task/suggestion/approval)
- **Backsolve** Due − per-subcategory business-day lead times → Start + Follow-up; flag
  "behind-before-begun". Lead-times are per-project config; only auto-fill when empty.
- **Band** GREEN/AMBER/RED from `min(due-float, response-window-float, staleness)`; auto `!` on RED.
  Float uses the contractual response window, not just Due.
- **Defend** Hero re-sorts by risk; runway bar normalizes to lead-time, not raw days-to-due.
- **Stale-ball ladder** polite → firmer+CC → escalation note to super; visible "nudged ×N".
- **Morning War-Board** (weekday 6am cron) one risk() pass → hero band + Discord pre-huddle +
  Memory note from one object. Folds in personal hard dates (passport, taxes).
- **Friday 14-day lookahead** same scorer, wider window; flags same-day collisions.

## PM autopilot — one "Approval Trust Bus" (per-kind policy table on `decide()`)
- **Ball-in-Court chaser** — drafts next nudge; re-arms Follow-up only when the approval *fires*.
  Email structurally locked to a tap.
- **Inbox→task reconciler** — classifies unread GC/coordinator mail into proposed sheet diffs;
  emits a `sheet_write` approval; never auto-completes off a fuzzy subject match.
- **Submittal-log reconciler** — diffs a pasted/dropped xlsx against the sheet by artifact key
  (sidesteps IT-blocked DriveBridge). Build the fuzzy key normalizer first.
- **Soft-auto hold-timer** — after a hold window, auto-fires local-only writes; allowlist
  `sheet_write(self)` + `calendar_create(self)` only — never email, never auto-close an RFI/submittal.

## Creative problem-solvers
1. **Coordination-meeting loop closer** — pre-meeting packet; dictate outcomes into the mic →
   Quick-capture parses each into a task with ball-in-court = named trade + due + follow-up.
2. **Crew-curve recovery sentinel** — blocking row red → shift activity, re-run `build()`, show
   "peak → 16, over your 14 cap"; offer 2-3 named options, never one silent auto-solve.
3. **Decision-debt forcing function** — every `action=hold` gets a decide-by + stated consequence.

## Build order
**Phase 1 — this week:** ① sheet-write spine (+ `last_nudged`/`created_at`) ② `risk()` + date layer
③ deadline-aware hero ranking + runway bar ④ unified risk legend (action = LEFT spine; risk = RIGHT pip + bang).
**Phase 2 — big bets:** Ball-in-Court Ledger + chaser · Morning War-Board · Critical-path backsolver ·
Approval Trust Bus · the two reconcilers.
**Phase 3 — needs a real data model:** manpower trade×week matrix → recovery sentinel +
cross-project clash detector (group by category) → Friday lookahead.

## Cut
The `actions_log` lead-time "learning loop": it logs only kind/ref/result (no timestamps) → zero
signal for months, and silent drift destroys trust. Ship hand-editable constants in the cockpit.

## Top picks
1. Sheet-write spine  2. `risk()` helper  3. Ball-in-Court Ledger + chaser
4. Critical-path backsolver  5. Morning War-Board
