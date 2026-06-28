# Wise Old Man OS — User Manual

Your personal + work command center. One place to see what needs you today, run your agents, keep your tasks and notes, and approve anything before it goes out.

> **Heads-up: this is a MOCK build.** Everything in the app right now runs on built-in demo data. Nothing is really sent, emailed, written to a sheet, or pushed to your vault — every "send", "chase", "approve", and "save" is simulated and labeled **MOCK**. You can click freely and break nothing. When the real connections (Google, Sheets, Discord, Obsidian, Cloudflare) are wired up, the same buttons will do the real thing.

---

## Index

- [Getting around](#getting-around)
- [The top bar — Work/Personal, Quick add, Search](#the-top-bar)
- [Dashboard](#dashboard)
- [Tasks](#tasks)
- [Workspace (agents + live preview)](#workspace)
- [Approvals queue](#approvals-queue) *(new)*
- [Ball-in-Court chaser](#ball-in-court-chaser) *(new)*
- [Activity log / console](#activity-log) *(new)*
- [Global search / command palette](#global-search) *(new)*
- [Cockpit — Usage & Memory keeper](#cockpit) *(updated)*
- [Notes](#notes)
- [Notes — Obsidian vault tree](#notes-vault-tree) *(new)*
- [Notes — Freeform infinite canvas](#notes-freeform) *(new)*
- [Keyboard & gestures quick-reference](#keyboard-gestures)
- [On your iPad](#on-your-ipad)
- [Document status](#document-status)

---

## Getting around

The app has three zones:

- **Top bar** (always visible): the Wise Old Man logo, the **Work / Personal** toggle, **Quick add**, **Search**, and a **MOCK** badge so you always know you're in the demo.
- **Left nav** (desktop / iPad): your sections, grouped into **Primary** (Dashboard, Tasks), **Agents** (Workspace, Hermes, Claude Code, Cowork), and **More** (Cockpit, Notes, Activity, Approvals).
- **Bottom nav** (phone): the five most-used tabs — Home, Tasks, Agents, Notes, Cockpit — plus the Approvals tab.

**To switch sections:** click any nav item. On keyboard, **Tab** to a nav row and press **Enter** or **Space** to open it. Sections fade in as you move between them.

---

## The top bar

### Work / Personal toggle
The pill in the top-left switches your whole world between **Work** and **Personal**. Everything respects it — the dashboard hero, task list, project metrics, finance card (Personal only), approval counts, memory promotions, and activity feed all re-filter instantly to the scope you pick.

- **Click** Work or Personal to switch.

### Quick add
The **+ Quick add** button (top-right) opens a small menu:

- **New task** — jumps to Tasks and starts a fresh row for you.
- **New note** — opens Notes.
- **Quick capture** — jot or dictate a thought (mock: would land in your Obsidian inbox).

**Open it:** click **+ Quick add**. **Close it:** click outside it, or press **Escape**.

### Search (⌘K)
Left of Quick add is the **⌘K Search** button — the global command palette. See [Global search](#global-search).

---

## Dashboard

Your morning briefing. Open it from **Dashboard** in the nav (or **Home** on phone). It greets you by name and shows the day, then a grid of cards:

- **Today's focus (the hero)** — the single most important thing right now, chosen from your at-risk tasks (overdue, due soon, or waiting too long), preferring items where the ball is in *your* court. The button reads **Start** if it's on you, or **Chase {name}** if you're waiting on someone (see [chaser](#ball-in-court-chaser)). Below the headline are up to three "at-risk" pips with each task's due date.
  - When approvals are waiting, a red **"N awaiting you →"** pill appears on the hero — click it to jump straight to the [Approvals queue](#approvals-queue).
- **Project metrics** — progress bars per project (Work: Project Alpha / Beta; Personal: Italy trip / Home) with a status note. The **open** link goes to Tasks.
- **Tasks at a glance** — three big numbers (open / on me / at risk) and your next few open items. **open** link goes to Tasks.
- **Cockpit** — a compact strip showing how many connections and jobs you have, plus your **live window-usage %** (this number is now driven from a single source — see [Cockpit](#cockpit)). **open** link goes to Cockpit.
- **Finance** (Personal only) — net worth, today's move, and a sparkline.
- **Recent activity** — the last 3 events for the current scope, with an **open** link to the full [Activity log](#activity-log).
- **Hermes strip** — at the bottom, Hermes's top suggestion for the current scope, with how confident it is. **open →** takes you into the Workspace with Hermes selected.

**Tip:** The hero is the one thing to do first. If it says "Chase {name}", you're not the blocker — let the app draft the nudge.

---

## Tasks

A fast, spreadsheet-style grid of everything on your plate for the current scope. Open it from **Tasks**.

### Reading a row
- **Left colored bar** = the action type (Action / Wait / Hold / Read / Event).
- **! / P-column** = priority, **P0–P4** (P4 highest). A **✦** means Hermes set it; otherwise it's your value or auto-derived from risk.
- **Right pip** = deadline risk: **green** on track, **amber** getting close / blocked, **red** overdue or due within ~2 days. Hover the pip for the reason.

### Filtering & sorting
- **Filter chips** (top): All, Mine, Action, Wait, Hold, Read, Event. **Click** one to narrow the list; the count updates beside them.
- **Sort:** **click any column header**. Click again to flip ascending/descending. The active column shows a ▲/▼ arrow.

### Editing in place
- **Text cells** (description, dates, owner, ball-in-court, category…): **click** the cell and type. It commits the moment you click away. Press **Enter** to commit and drop to the same column in the next row; **Escape** to cancel.
- **Dropdowns** (Action, Status): **click** and pick — commits immediately.
- **Priority:** use the **P0–P4** dropdown in the first column.

### Adding a row
- Click **+ Add row** (bottom of the grid). A blank row appears with the description field focused.
- **Tab** through the cells, then press **Enter** to commit. Commit an empty description and the row is discarded. After you commit, a fresh blank row opens so you can keep going.
- Quickest start: **Quick add → New task** does the Add-row click for you.

### Chasing (new)
Every row you're *waiting on someone else for* gets a small **Chase {firstname}** button at the end, and the toolbar has a **Chase all waiting** pill. See [chaser](#ball-in-court-chaser).

**Tip:** The grid scrolls horizontally — all columns (including the chase button) are always reachable on a narrow screen by swiping the grid sideways.

---

## Workspace

Where you talk to your agents and watch them work. Open **Workspace**, or pick a specific agent under **Agents** in the nav: **Hermes** (the orchestrator), **Claude Code** (runs on your Windows machine), or **Cowork** (pairing). A colored dot shows each agent's status.

- **Left = conversation.** Type in the box at the bottom and press **Enter** or click the **↑** send button. (Mock replies come back instantly; the agent notes it needs real credentials to act for real.)
- **Right = live preview** of whatever the agent is producing, with three tabs: **Preview** (the rendered draft), **Code** (the raw file, e.g. `rfi-014.md`), and **Diff** (what changed). A footer shows build status and the draft path.
- On a draft you'll see **Approve & send** and **Edit**. In the mock, Approve & send shows a confirming toast; nothing leaves your machine. For staged items you can review, use the [Approvals queue](#approvals-queue).

**Tip:** Hermes proposes; you dispose. It explains *why* (e.g. "gates L2 rough-in") and stages work for your approval rather than acting on its own.

---

## Approvals queue
*(new)*

Everything an agent has staged for you that has **not** been sent. Nothing here ever leaves your machine — **every card is labeled mock.** Open it from **Approvals** (✓ icon) in the nav or the phone tab.

### Pending cards (top, newest first)
Each card shows:
- a **kind chip** — Draft / Chase / Sheet write / Action,
- the **title** and who it's addressed **to**,
- a **preview** of the draft body,
- a **source tag** — **✦ Hermes** if Hermes drafted it, or **You**.

Three buttons per card:
- **Approve** (green) — marks it approved, logs it to [Activity](#activity-log), and shows a toast. No real send.
- **Reject** — marks it rejected, with a toast.
- **Edit** — makes the body editable inline; click **Done** to save your wording, then Approve.

### Resolved (history)
Below pending, past items appear dimmed with a **✓ Approved** or **✕ Rejected** stamp.

### Filters & counts
- **Filter chips** at the top: **All / Pending / Resolved**. The Pending chip carries its own count.
- The **pending count** surfaces in three places so you never miss it: a **red badge** on the Approvals nav entry (and phone tab), the **"N awaiting you →"** pill on the Dashboard hero, and the queue itself. Counts are **per-scope** — toggling Work/Personal shows only that scope's pending items. Approving/rejecting updates every badge instantly.

**Tip:** This is your safety gate. In the mock it proves the flow; with real connections wired, this is the last click before anything is actually sent.

---

## Ball-in-Court chaser
*(new)*

Whenever a task is "waiting on" someone other than you, Wise Old Man can draft the chase for you — a polite, specific follow-up that references the task, how many days it's been waiting, and the due date.

Three ways to trigger it:
- **Dashboard hero:** when today's top item is in someone else's court, the big button reads **Chase {name}**. Click it.
- **Tasks grid:** click the **Chase {firstname}** button at the end of any waiting row.
- **Tasks toolbar:** click **Chase all waiting** (with a count) to draft chases for *every* waiting item in the current scope at once.

**Nothing is ever sent automatically.** Each chase is staged as a **pending** item in [Approvals](#approvals-queue), where you review the wording and approve or reject. After staging you get a confirmation toast and, if Approvals is available, the app jumps you straight there. Chases respect the current Work/Personal scope.

**Tip:** Use **Chase all waiting** first thing in the morning, then skim Approvals and approve the good ones in a batch.

---

## Activity log / console
*(new)*

Your audit trail — every event the system performs, newest first. Open **Activity** in the left nav (under **More**), or the **open** link on the Dashboard's Recent-activity tile.

What shows up: Hermes signals, approvals you resolved, tasks you edited, notes saved, chases drafted, the nightly memory push — each with:
- a **type icon** (colored by kind),
- a **scope chip** (work / personal),
- a **relative timestamp** ("2h ago"),
- the **event text**.

Rows are **grouped by day** — "Today", "Yesterday", then dated headers.

### Filtering
Two rows of chips:
- **By type:** Approvals, Chases, Edits, Signals, Notes, System.
- **By scope:** All / Work / Personal.

Click chips to narrow the feed.

### Persistence
- Served over the web, the log **survives reloads** (saved to your browser) and keeps the most recent **200 events**.
- In pure file preview (opening the HTML directly), it falls back to the seeded demo events.

**Tip:** When you wonder "did that actually do something?", Activity is the honest answer — if it happened, it's logged here.

---

## Global search
*(new)*

A keyboard-driven command palette that finds tasks, notes, and commands — and runs actions.

**Open it three ways:**
- click **⌘K Search** in the top bar,
- press **Ctrl-K** (**Cmd-K** on Mac) from anywhere,
- (when wired) via a "Go to…" command.

Start typing; results appear instantly in three groups:
- **Tasks** — matches description, category, owner, or ball-in-court in the **current scope**. Opening one jumps to the Tasks grid, scrolls the row into view, and focuses its description cell.
- **Notes** — matches title or body across **both** Work and Personal vaults. Opening one switches to Notes and selects the right folder + note.
- **Commands** — Go to Dashboard / Tasks / Workspace / Cockpit / Notes / Approvals / Activity, **New task**, **New note**, and **Toggle Work/Personal**.

**Fully keyboard-driven:**
- **↑ / ↓** (or **Tab / Shift-Tab**) move the highlight,
- **Enter** runs the highlighted result (top hit by default),
- **Escape** closes,
- click outside to dismiss.

Matching text is highlighted in each result, focus is trapped in the search box while open, and returns to where you were when you close.

**Tip:** Memorize one shortcut and you barely need the mouse: **⌘K → type two letters → Enter**.

---

## Cockpit
*(updated)*

Your operations panel. Open **Cockpit** (nav under **More**, or the phone tab). It shows four cards:

- **Connections** — Google, G-Suite Sheet, Discord, Obsidian vault, Cloudflare tunnel and their status (ready / pending).
- **Scheduled jobs** — Morning War-Board, Ball-in-Court chaser, Sheet↔vault sync, Drive ingest, nightly Memory git push, and their cadence.
- **Skills inventory** — the skills available and whether they're Work, Personal, or both.
- **Usage** *(now live)* — how much of your Claude window you've used today, tokens used, your plan (Claude Max), and when the window resets. This is the **single source** for the usage % shown on the Dashboard's Cockpit card — no more frozen numbers.

### Memory keeper *(new card)*
A snapshot of what the Memory keeper has learned and promoted:
- the **last nightly memory-push** time,
- a left-to-right **flow of your three vault tiers** with live counts: **00-raw** captured → **10-wiki** distilled → **20-outputs** shipped,
- a list of **recent promotions**, each showing the tier path it moved along (e.g. `00-raw→wiki`), the title, its scope, and when.

Promotions matching your **current Work/Personal scope** are listed first; toggle the top-bar switch and the list re-orders to surface the relevant scope.

**Tip:** This card is your proof that "capture → distill → ship" is actually flowing, tier by tier.

---

## Notes

A three-pane Obsidian-style editor: **folders/tree** | **note list** | **editor**. Open **Notes**.

- **Work / Personal toggle** sits above the left column to scope your notes.
- **Pick a note** from the middle list (**click**, or **Tab** + **Enter**). The editor opens on the right; the footer shows the saved vault path. Edits you type save back to that note (mock).
- **Editor modes** (top-right of the open note): **Type** (prose only), **Split** (prose + canvas), **Ink** (canvas only), and **Freeform** (new — see below). **Click** a mode button to switch.
- **Focus mode:** click **Focus** to hide the side columns and write distraction-free; **Exit focus** to bring them back.
- **Resizable panes (desktop):** drag the thin dividers between columns to set widths; in Split mode, drag the horizontal divider to size the canvas vs. the text.

---

## Notes — Obsidian vault tree
*(new)*

The left column is now a real Obsidian-style **vault tree** with the three tiers **00-raw**, **10-wiki**, and **20-outputs**. Each tier expands into **Work** and **Personal**, which hold nested project folders (Project Alpha/Beta, Meetings, Italy, etc.) and `.md` files.

- **Click a folder** to expand/collapse it **and** filter the middle note list to just that folder's files. The selected folder highlights and its path appears in the **VAULT PATH** indicator at the bottom of the tree.
- **Click a `.md` file** (in the tree or the filtered middle list) to open it. The editor footer shows the live path, e.g. `20-outputs/Work/Project Alpha/rfi-014.md`.
- **Edits** you type write back to that vault file in place (mock in file preview; saved to the server when hosted).

On phone/iPad the tree collapses with the rest of the left rail, same as before.

**Tip:** Think of the tiers as a pipeline — **00-raw** is where things land, **10-wiki** is distilled knowledge, **20-outputs** is what you ship. The same flow you see counted in the Cockpit's Memory keeper.

---

## Notes — Freeform infinite canvas
*(new)*

The editor mode switcher now has a 4th button: **Type / Split / Ink / Freeform**. Tap **Freeform** for an infinite, Apple-Freeform-style canvas. A dotted grid shows the canvas and your current zoom. **Each note keeps its own canvas** — leave and come back and your sketch is still there.

### Tools (floating palette, bottom-center)
- **Pen** — handwriting/sketching. On iPad with Apple Pencil the line gets **thicker as you press harder** (pressure-sensitive). A faint ring shows where the Pencil is hovering.
- **Highlighter** — translucent wide stroke for markup.
- **Eraser** — drag over strokes to remove them.
- **Select / move** — drag sticky notes and text boxes around.
- **Sticky note** — tap the canvas to drop one, then move/edit it.
- **Text** — tap to place a label (you'll be prompted for the text).

### Navigation
- **Pan:** two-finger drag (touch/trackpad), **hold Space and drag** (desktop), or middle-mouse drag.
- **Zoom:** pinch (touch/trackpad) or **Ctrl/Cmd + scroll**. The **100%** button resets the view.

### Switching tools fast
- The **⟳** palette button cycles **pen → highlighter → eraser → select**.
- On iPad you can also **double-tap the Pencil tip on the canvas** to cycle tools.

> **Honest hardware note:** the **Apple Pencil Pro squeeze** and the **Pencil's hardware double-tap** can't be read by any web app — there's no browser API for them. The ⟳ button and the on-canvas double-tap are the substitutes. **Pressure** works; **tilt** is read by some iPads but isn't wired into the stroke for reliability.

When hosted on the server, your canvas saves back to the note. In file preview it stays for the session.

**Tip:** Freeform is for thinking visually — clash sketches, room layouts, a quick org of who owns what. For typed text, stay in Type/Split.

---

## Keyboard & gestures quick-reference

| Action | How |
|---|---|
| Open Search / command palette | **Ctrl-K** / **Cmd-K** (or **⌘K** button) |
| Move through search results | **↑ / ↓** or **Tab / Shift-Tab** |
| Run highlighted result | **Enter** |
| Close palette / Quick-add menu | **Escape** |
| Activate a focused nav row / note | **Enter** or **Space** |
| Commit a task cell, drop to next row | **Enter** (in a grid cell) |
| Cancel a task cell edit | **Escape** |
| Move through new-row fields | **Tab**, then **Enter** to commit |
| Send a message to an agent | **Enter** (in the Workspace box) or **↑** |
| **Freeform — pan** | Two-finger drag · **Space-drag** · middle-mouse drag |
| **Freeform — zoom** | Pinch · **Ctrl/Cmd + scroll** · **100%** to reset |
| **Freeform — cycle tools** | **⟳** button · double-tap Pencil on canvas |
| **Freeform — pressure** | Press harder with Apple Pencil = thicker line |
| Resize Notes panes (desktop) | Drag the dividers between columns / rows |

---

## On your iPad

- **Install it as an app:** open it in Safari, **Share → Add to Home Screen**. It launches full-screen like a native app (PWA), respecting the status bar and safe-area insets.
- **Layout adapts:** on iPad-portrait the rails slim down so the editor breathes; the Notes folder column hides to give you room. On phone widths, the left nav becomes the **bottom tab bar** (Home, Tasks, Agents, Notes, Cockpit, plus Approvals).
- **Apple Pencil in Freeform:** pressure-sensitive ink, a hover ring showing where the nib is, and **double-tap on the canvas** to cycle tools (a stand-in for the Pencil's hardware gestures, which browsers can't access). Pinch to zoom, two-finger drag to pan.
- **Everything is tap-friendly:** chase buttons, filter chips, and approval buttons all have larger touch targets on small screens.

---

## Document status

*Living document, maintained by the Hermes agent. Reflects the current MOCK build (all data is simulated; nothing is sent or written). Last reviewed 2026-06-28 — refresh by 2026-07-28, or sooner when any of the above features move from mock to live connections.*