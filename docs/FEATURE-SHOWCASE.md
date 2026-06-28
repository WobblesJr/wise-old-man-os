# Feature showcase + information architecture (Warm Paper)

From a 10-agent panel (6 feature designers → IA / spacing / progressive-disclosure debate → lead).
Flip through it in **`preview/feature-options.html`** (served at `/preview/feature-options.html`).

## Navigation — most-used first (3 tiers, so 9 destinations never read as a flat list)
- **PRIMARY** (full weight, one click): **Dashboard**, **Tasks** — hot.
- **AGENTS** (grouped channel): **Workspace** (hot), then **Hermes** (hot), **Claude Code** (periodic), **Cowork** (rare).
- **MORE** (recedes in muted ink, still one click): **Cockpit**, **Finance**, **Notes** — periodic.
- Two key moves: (1) **Approvals is a verb, not a 7th nav item** — it rides the Dashboard hero CTA +
  the Workspace queue. (2) A **global Quick-Add (+)** in the top bar handles task/note capture, so
  capture frequency comes off the rail (lets Notes safely live in tier 3).

## Spacing — one base-4 scale, nothing off it
`4 / 8 / 12 / 16 / 20 / 24 / 32`. **The whole system in a sentence: 8 inside a cluster · 12 between
siblings · 16 at a seam · 24 between regions.** Anchors that never vary: page-pad 24 (Tasks 20 top /
24 sides), grid-gutter 16 (Cockpit's 2×2 of equals is the one place it goes to 24), tile-pad 20,
region-seam 24. Label↔value 6–7, chips 8, hairline dividers 16 above/below. This kills the old build's
four near-identical gaps (6/8/10/12) that read as visual noise.

## Anti-overwhelm — progressive disclosure
Every tile shows **one number-cluster + one short list, then a quiet clay deep-link** (no tile is a
dead-end, none crams two competing data blocks). Cockpit sections collapse; Tasks hides advanced
columns; reasoning panels auto-collapse after streaming. Responsive: single column at 768px
(iPad-portrait); phone bottom bar = Dashboard / Tasks / Workspace / More, mirroring the desktop tiers
so muscle memory transfers; scope toggle moves to the Dashboard header on phone.

## The 6 screens (build briefs)
- **Dashboard** — header band (greeting + Work/Personal) → 24 seam → 2-col grid (16 gutter, 20 pad):
  full-bleed *Today's focus* hero (3px clay rule, the one CTA) · *Project metrics* (runway bars) ·
  *Tasks at a glance* (3 stats + 3 rows) · *Cockpit glance* ("7 connected · 5 jobs") · *Finance peek*
  (net worth + sparkline). Each tile = one cluster, capped, with a deep-link.
- **Tasks (spreadsheet)** — title row · control bar (on-site select | filter chips | "N saved") · grid
  card with **lightened inner gridlines** (the cage→ledger move), sticky header, 35px rows, pinned
  footer **+ Add row** → editable blank row, **Tab** through cells, Enter commits + reopens.
- **Finance** — net-worth header · asymmetric 2-col (portfolios + bills | top holdings + connected
  card) · right-aligned number columns · up/down = static green/clay only, never flashing.
- **Notes** — 3-pane card: folder rail (Work/Personal + vault path) | note list | editor with
  Type/Ink/Split + an **Apple-Pencil ink canvas**; persistent "✓ Saved to Obsidian" + per-note pills.
- **Cockpit** — header glance strip → 2×2 of **equal** tiles (24 gutter): Connections · Scheduled jobs
  · Skills · Usage; **rows on hairlines, not boxes**; clay reserved for the "window used" stat only.
- **Workspace (agents + live preview)** — agent rail + a 2-pane split: conversation (left) ·
  **artifact pane (right)** with Preview / Code / Diff tabs swapping the same rendered preview in
  place. The live-preview ability stays.

## Recommendation
Ship this as the structure: Warm Paper palette + the strict base-4 scale + the 3-tier rail. It "shows
a lot but feels calm," and the most-used items (Dashboard, Tasks, Workspace) are one click with the
periodic ones quietly in **More**. Pick this and I apply it to the real `preview/index.html`.
