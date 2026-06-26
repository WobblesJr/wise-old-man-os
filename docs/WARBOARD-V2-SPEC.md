# War-Board v2 — layout spec

> Output of a 5-lens agent panel (operations · schedule · productivity · financial · mental-health)
> → debate → synthesis, 2026-06-25. Weighted to Gavin's profile: field-driven 7–6, phone glances,
> deadlines+productivity primary, financial+mental supporting, Hermes-orchestrates-Claude-Code,
> draft-everything posture. Grounded in real code (`warboard.build()`, `risk.py`, `chaser.py`,
> `approvals.decide()`'s 4 kinds, `sheet_tasks.COLUMNS`).

**Guiding rule:** the band is the product. On a calm day a field PM sees **only deadlines + the one
thing + the day's shape**. Everything else is signal-gated to zero pixels or lives below the fold.

## 1. Expanded War-Board — top to bottom, on a phone at 6am

| # | Section | Placement | Above fold | Source |
|---|---------|-----------|------------|--------|
| 0 | **Headline** — `build().headline` | band | ✅ | `warboard.build()` |
| 1 | **The One Thing** — `highest_leverage` huge: desc + `why`(risk.reason) + Action spine + ONE button. ball=Me→**Do**, else→**Chase** | band hero | ✅ | `highest_leverage` |
| 2 | **Date-in-Danger Spine** — 2–3 fat chips from `top_dates`: desc+due+days+reason+runway micro-bar+subcat icon. De-duped vs the hero | band | ✅ | `top_dates` |
| 3 | **Day-Shape Ribbon** — one thin 7am–6pm row; events + labeled open gaps; largest gap carries the single **Protect this window** tap | band sub-row | borderline | `google.today()` |
| 4 | **Conditional strip — AT MOST ONE** — tripped Overload Gauge **or** Money-at-Risk pin; zero pixels when cold | band lower | no | risk density / `$` red task |
| 5 | **Delegation badge** — "2 running, 1 awaiting you" (Hermes→Claude Code) | band footer | no | jobs/usage |
| 6 | **Ball-in-Court Ledger** — collapsed header = calm framing; expands to chase rows + "nudged ×N" + OK-to-send | primary tile | no | `stale_balls`+`chases` |
| 7 | **Batch-Approve Queue** — every pending approval, inline OK; "Approve all low-risk (N)" | primary tile | no | `/api/approvals` |
| 8 | **Lead-Time Backsolver** — top 3 start-by-in-danger; degrades to days_to_due until Phase-2 | primary tile | no | risk + lead-time map |
| 9 | **Collision Radar** — next-10-day strip, red dot on pileups; band dot only <48h | secondary | no | risk.stamp_tasks |
| 10 | **Delegation Rail** (full) — Hermes→Claude Code jobs queued/running/done + task_id + elapsed + tokens | drawer | no | jobs+usage |
| 11 | **Schedule-Recovery & Decision-Debt drawer** — 14-day lookahead, crew-curve options, all `action=hold` decide-by+consequence | drawer | no | risk + holds |
| 12 | **Budget drawer** — held-money decisions + bills-as-tasks only (no fake bars; sheet has no `$` col) | drawer | no | parsed `$` |
| 13 | **End-of-Day nudge** — ~6pm cron line, states the win, auto-expires | cron line | n/a | cron |

**Above the fold:** Headline · The One Thing · 2–3 Date chips. Nothing financial/mental renders here
unless it *became* `highest_leverage` itself.

## 2. Cross-lens conflicts resolved
- **A. Chase-harder vs protect-pace** → one list, one tile, two states. Calm framing = the *collapsed
  header* of the Ball-in-Court Ledger; chase rows = the *expanded* state. Band carries no nag count.
- **B. One hero, not two** → nest, don't compete. Fixed order: headline → One Thing (only full-bleed) →
  3 chips (de-duped) → ribbon (thin context row).
- **C. One calendar gap, one draft** → the ribbon single-owns gap detection; the largest gap asks ONE
  question, arbitrated by overload (hot→recovery block, else→focus window).
- **D. Money never gets standing band pixels** → a hard-money date is just a red task with a `$` icon on
  the spine; the money pin shows only when hot AND not already top-3 AND overload is cold.
- **E. Four delegation rails → one** shared scope-filtered rail in a drawer; band shows only the count.

## 3. Spacing system — one vertical rhythm
```
--space-1:4  --space-2:8  --space-3:12  --space-4:16  --space-6:24  --space-8:32
```
**8 inside, 12 between, 16 at the hero seam, 24 at the fold.**
- chip/card internals: 8 · rows within a tile: 12 · sibling tiles: 12 (= current `.grid` gap) ·
  3 date chips: 8 (tighter, read as a unit) · band sub-sections: 16 · band→grid seam: 24 (the fold) ·
  card padding: 12 (hero 16). Conditional strips collapse to **0 height** (no residual gap). Never a
  value off the scale.

## 4. Hermes ↔ Claude Code surface
New tiny `delegations` table: `id, scope, job_name, task_id|approval_id, status(queued|running|done|
needs_approval), elapsed_s, tokens, artifact_ref`. Hermes writes a row when it hands Claude Code a
build/coding job; Claude Code updates status+tokens (reuses the usage ledger).
- **Band:** one count badge only.
- **Drawer:** the full rail.
- **Posture tie:** a completed delegation **never auto-applies** — its output stages as a pending
  approval of an existing kind and the row flips to `needs_approval`; "Review output" deep-links into
  the Batch-Approve Queue. Kicking one off ("Dispatch to Claude Code") is itself a low-risk approval.
  Nothing delegated fires, and nothing it produces lands, without a tap.

## 5. Build order
**Phase 1 — fits the current preview now (pure render off `build()`):**
1. Re-lay band to fixed order: headline → One Thing hero (promote "START WITH" to full-bleed + Do/Chase
   flip) → 3 date chips (runway bar + subcat icon) → Day-Shape Ribbon from `today()`.
2. Ball-in-Court Ledger collapsed-calm-header → expand to chaser rows.
3. Batch-Approve Queue tile → `/api/approvals` + `decide()`; "Approve all low-risk".
4. Delegation badge + drawer (mock `delegations`).
5. Apply spacing tokens. *(+ 3-way Personal|Both|Work toggle with unified risk-ranked merge.)*

**Phase 2 — backend:** lead-time backsolver into `risk_for_task()` · decision-debt `sheet_write` ·
money-as-tag parse · collision radar · real `delegations` writes staged as approvals.

**Phase 3 — live + cron:** calendar end-times + Protect-window `calendar_create` · overload gauge ·
end-of-day cron · schedule-recovery/crew-curve drawer as `sheet_write` approvals.

## 6. Open questions (needed for Phase 2, not Phase 1)
1. Real per-subcategory **business-day lead-times** (RFI response, submittal review, manpower-build, passport buffer)?
2. **Overload trip points** — ≥3 red / N back-to-back meetings / 3rd loaded day? Set N.
3. Real **crew cap** (spec assumed 14) — per-project or global?
4. **Chase ladder identities** — who is "super" by name/role; should escalation ever copy GC/owner or stay internal?
