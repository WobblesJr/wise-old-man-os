# UI redesign — 5 options (for review)

Calmer, flatter takes on a **Slack/Discord-style agent-channel layout**, from a 9-agent design panel
(5 designers → calm/smoothness/distinctness critics → lead finalize). Flip through them live in
**`preview/redesign-options.html`** (served at `/preview/redesign-options.html`). Lead recommendation
below.

## Shared layout (all 5)
- **Left rail** (~212–248px): agent channels under two eyebrows — **AGENTS** (Hermes pinned first,
  then Claude Code, Cowork) and **WORKSPACE** (#morning-brief, #approvals, #tasks). Active channel
  marked by a left accent bar that **slides** on the same easing as the pane switch (one system).
- **Main pane** = the channel. Agent channels are a chat that shows **live output richly** —
  streamed text + caret, a collapsible Hermes "Reasoning" panel, flat code blocks with a lang tag,
  tool/HTTP cards (`GET /api/tasks · 200 · 120ms`), framed inline previews — like Claude Code's own
  tool output, but flat. The dashboard becomes channels too (War-Board → #morning-brief, grid → #tasks).
- **Hermes is the star** everywhere: pinned top, the only filled-accent avatar, default-open, with a
  live status caption.
- **Transitions:** one reused sub-200ms cross-fade-with-settle per skin (the "snap to next section"
  feel), scoped to opacity/transform, honoring reduced-motion. Flat 2D — hairline borders + one
  surface step do all separation; no glow, minimal shadow.

## The 5 options

| # | Name | Mode | Accent | One-liner |
|---|------|------|--------|-----------|
| 1 ⭐ | **Calm Daylight** | light | slate-blue `#4A6E84` on `#F7F6F3` | Bright near-white, hairline left-ledger transcript; silent chrome, only Hermes' output lifts. |
| 2 | **Warm Paper** | light | clay `#A65A3A` on cream `#FAF6EE` | A cream-paper reading app; serif agent voice, muted ink, one disciplined accent. |
| 3 | **Quiet Dark** | dark | sage `#7FA38C` on charcoal `#16181D` | The command center you know, **de-neoned** — warm charcoal, zero glow, only Hermes pulses. |
| 4 | **Soft Studio** | light | sage `#5B7B6F` on `#FBF9F6` | Friendly studio with gentle **per-agent color-coded bubbles** (lavender Hermes owns the room). |
| 5 | **Mono Minimal** | light | indigo `#4F5BD5` on warm grey `#FAF9F7` | Near-monochrome; one indigo reserved for the active thing + Hermes; horizontal snap; type does the work. |

## Recommendation
**Lead with Calm Daylight** — the cleanest single inversion of the dark/neon build you called
abrasive: bright, restful, one quiet accent, a signature left-ledger transcript. **Show Quiet Dark
second as the hedge** so you can decide light-vs-dark first (it keeps the command-center mood you're
used to while killing the glow), then refine the winner.

## How this gets built
Once you pick (or mix — e.g. "Calm Daylight palette + Soft Studio's per-agent colors"), I apply the
chosen tokens to the real `preview/index.html`: swap the palette to CSS variables, add the agent-rail
+ channel router, move the dashboard surfaces into channels, and wire the one shared transition. All
front-end, no credentials — buildable immediately.
