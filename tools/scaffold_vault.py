#!/usr/bin/env python3
"""Scaffold the Obsidian vault with an index.md "map" in every folder.

Structure follows docs/AUTOMATION-STRATEGY.md: three tiers (Raw / Wiki / Outputs) plus the
live task store, skills, jobs, and system folders. Every folder gets an index.md that tells
an agent (or you) exactly what lives there, how to use it, and the conventions — so Claude/
Hermes can navigate the vault by reading the maps instead of guessing.

Organized around YOUR work: projects (Alpha/Beta), recurring master files, product reference.

Run: python tools/scaffold_vault.py [--root backend/data/vault]
Idempotent: creates folders if missing, (re)writes index.md, never touches your content files.
"""
from __future__ import annotations

import argparse
from pathlib import Path

PROJECTS = ["project-alpha", "project-beta"]
PROJECT_SUBS = {
    "rfis": ("RFIs", "The RFI log + one note per RFI (number, question, status, ball-in-court, "
                     "response-due). Tasks of category RFI link here."),
    "submittals": ("Submittals", "The submittal log + one note per submittal (spec section, rev, "
                                  "status, reviewer, returned-date)."),
    "schedule": ("Schedule", "Baseline, lookaheads, manpower-loaded schedules, and recovery plans "
                             "for this project. Generated schedules land in 20-outputs/schedules."),
    "meetings": ("Meetings", "Minutes — pre-con, coordination/OAC, weekly. One note per meeting; "
                            "action items become tasks (ball-in-court = the named party)."),
    "closeout": ("Closeout", "Punchlist, O&M manuals, as-builts, warranties, final documentation."),
}

# (relative path, Title, purpose, [contents bullets], agent-notes)
FOLDERS: list[tuple] = [
    (".", "Vault map — START HERE",
     "The map of this vault for Claude/Hermes. Read this first; then the index.md of any folder "
     "you enter. Three tiers: information matures Raw → Wiki → Outputs.",
     ["**00-raw/** — everything ingested, unprocessed (low-trust). Email, Drive mirror, feeds, captures.",
      "**10-wiki/** — structured, context-linked knowledge. **Read this to answer questions.**",
      "**20-outputs/** — deliverables agents produce (all drafts pending your approval).",
      "**tasks/** — the live task store (the G-Suite Dashboard mirror; managed by the app).",
      "**overlay/** — agent overlays not in the sheet (priorities P0–P4).",
      "**skills/**, **jobs/** — automation definitions (see docs/AUTOMATION-STRATEGY.md).",
      "**.wom/** — system: sync state, the QC column schemas, QC logs."],
     "Navigation rules: to answer about a project, read 10-wiki/projects/<p>/index.md first, then "
     "its subfolders. Cite Wiki/Outputs, not Raw, unless verifying. Never hand-edit tasks/*.md while "
     "the app runs. Everything outward is draft-and-approve."),

    ("00-raw", "RAW — ingest tier",
     "Unprocessed, append-only, low-trust intake. The Synthesis loop distills these into 10-wiki.",
     ["email/ — pulled email threads", "drive/ — one-way mirror of selected Google Drive files",
      "feeds/ — feed pulls (news, OSRS, events)", "capture/ — your quick-captures + voice notes"],
     "Do NOT cite raw items directly in deliverables without verification. New raw items are the "
     "input to the Synthesis loop. Treat anything here as 'claimed, not confirmed'."),
    ("00-raw/email", "Raw · Email",
     "Pulled email threads, one note per thread.",
     ["One markdown note per thread", "frontmatter: {from, subject, ts, thread_id, project, scope}"],
     "Source for inbox triage. Link the relevant project/person when filing into Wiki."),
    ("00-raw/drive", "Raw · Google Drive mirror (read-only)",
     "One-way mirror of the Google Drive Docs/Sheets that support skills and jobs. Drive is the "
     "source of truth — NEVER edit here; edits are overwritten on the next sync.",
     ["Mirrored Docs/Sheets/exports", "Re-synced by the Drive→raw ingest job (rclone/Drive API)"],
     "Read-only reference. If a skill needs a Drive file, point its `reads:` at a path here."),
    ("00-raw/feeds", "Raw · Feeds",
     "Time-stamped feed pulls (news, OSRS hiscores/prices, events).", ["one file per pull/day"],
     "Low priority; feeds the personal-scope tiles and occasional context."),
    ("00-raw/capture", "Raw · Quick capture",
     "Your quick-captures and voice notes — the fastest way to get a thought into the system.",
     ["append-only capture notes"],
     "The triage loop converts these into tasks (quick-add) or Wiki notes. Process then mark done."),

    ("10-wiki", "WIKI — knowledge tier",
     "Structured, context-linked knowledge. Self-organizing: the Synthesis loop distills Raw into "
     "here and maintains backlinks. **This is the tier agents should read to answer questions.**",
     ["projects/ — per-project rolled-up state (your projects)",
      "people/ — contacts: who owes what, history",
      "products/ — reference info for products/equipment/materials",
      "master-files/ — recurring master files + templates (span projects)",
      "topics/ — cross-cutting process knowledge"],
     "Prefer Wiki over Raw when answering. Every fact should trace to a Raw source or a deliverable. "
     "Keep notes atomic and backlinked ([[Turner GC]], [[Project Alpha]])."),
    ("10-wiki/projects", "Wiki · Projects",
     "One folder per project. Each project's index.md is its living rollup.",
     ["project-alpha/", "project-beta/", "(add new projects as folders here)"],
     "To brief a project, read its index.md, then rfis/submittals/schedule for live detail."),
    ("10-wiki/people", "Wiki · People & companies",
     "One note per person or company you work with (GC, subs, coordinator, owner, engineers).",
     ["who-owes-what + open balls", "contact info + response patterns (best time to reach)",
      "history of interactions"],
     "Linked from a task's Ball-in-Court. The chaser/escalation skills read these for the right "
     "tone + the right person to CC."),
    ("10-wiki/products", "Wiki · Product & equipment reference",
     "Canonical reference for products, equipment, and materials — so skills cite real specs, never "
     "hallucinated ones.",
     ["one note per product/equipment line", "manufacturer, model, spec section, lead time",
      "approved/substitution status, cut-sheet links (to 00-raw/drive)"],
     "The Reference-Checker QC agent validates any spec/model number cited in a draft against THIS "
     "folder. If it's not here, it's not citable."),
    ("10-wiki/master-files", "Wiki · Recurring master files & templates",
     "The reoccurring master files and templates that span projects — your canonical, reusable set.",
     ["blank RFI log / submittal log templates", "manpower-schedule template",
      "standard procedures, checklists, company standards", "contacts master, distribution lists"],
     "Templates here are copied into a project folder to create an instance. Keep these clean and "
     "version them; project-specific data does NOT live here."),
    ("10-wiki/topics", "Wiki · Topics (cross-cutting)",
     "Process knowledge not tied to one project (the 'how we do X' notes).",
     ["e.g. RFI process, VE decision playbook, MEP coordination, closeout checklist"],
     "Reference these for procedure; link from project notes when applied."),

    ("20-outputs", "OUTPUTS — deliverables tier",
     "The actual deliverables agents produce. Everything here is a DRAFT pending your approval — "
     "draft-everything; nothing leaves without your tap.",
     ["drafts/ — emails, RFI cover notes, messages", "schedules/ — manpower schedules, lookaheads",
      "reports/ — morning briefs, weekly rollups, the 7am reflection"],
     "An output references the Wiki/Raw it was built from. On approval it routes through the board's "
     "approval flow (email_send / sheet_write / schedule_post)."),
    ("20-outputs/drafts", "Outputs · Drafts",
     "Drafted emails / RFI cover notes / chase messages awaiting your one-tap approval.",
     ["one file per draft", "frontmatter: {kind, to, subject, source_refs, approval_id}"],
     "Maps to an approval card on the board. Never send directly."),
    ("20-outputs/schedules", "Outputs · Schedules",
     "Generated manpower-loaded schedules and lookaheads (xlsx via tools/manpower_schedule.py).",
     ["xlsx deliverables + a sidecar .md summary"], "Link back to the project's schedule folder."),
    ("20-outputs/reports", "Outputs · Reports",
     "Briefs and rollups: the morning War-Board, weekly summaries, the 7am reflection.",
     ["one file per report/day"], "Display-only; the reflection report seeds the next day's plan."),

    ("tasks", "Tasks — LIVE store (app-managed)",
     "The live task store: personal.md / work.md are GFM tables mirroring your G-Suite Dashboard. "
     "Managed by the dashboard (GitVaultStore) — edit via the grid or the PATCH API.",
     ["personal.md, work.md — id + sheet columns (! left blank; priority is the overlay)"],
     "Do NOT hand-edit while the app is running (it owns these files). The '!' column is rendered "
     "from overlay/priorities.json. Schema + QC gate (.wom/schema) guards every write."),
    ("overlay", "Overlay — agent decisions (not in the sheet)",
     "Overlays layered on tasks that are NOT sheet columns.",
     ["priorities.json — P0–P4 (P4 highest), Hermes-decided, keyed by task_id"],
     "Hermes owns this. The website reads it; `POST /api/agent/priority` updates it."),

    ("skills", "Skills — definitions",
     "Skill definitions (markdown + frontmatter). status: draft → active(manual) → promoted. YOU "
     "manually promote. See docs/AUTOMATION-STRATEGY.md §2; the cockpit lists these.",
     ["_TEMPLATE.md — copy to start a new skill", "one file per skill"],
     "A skill declares reads/writes/qc/trigger. New skills start read-mostly + output-to-drafts so "
     "they can't do harm before you trust them."),
    ("jobs", "Jobs — promoted skills on a schedule",
     "Promoted skills bound to a trigger (cron/event). Hermes' loop runs due jobs.",
     ["one file per job: the skill ref + trigger + last-run/next-run"],
     "Created when you promote a skill. The cockpit 'Scheduled jobs' panel renders these."),

    (".wom", "System — config, schema & QC logs",
     "System internals (not your content).",
     ["sync-state.json — last git SHA / sheet rev (echo suppression)",
      "schema/ — column schemas that drive the blocking QC gate",
      "qc-log/ — every QC decision (repaired/blocked) for audit"],
     "Agents read schema/ before writing; the QC gate logs here. Don't put knowledge here."),
    (".wom/schema", "System · Schemas (QC source of truth)",
     "Column/type schemas the QC gate enforces before any write (kills malformed cells).",
     ["tasks.yaml — per-column type + single-value/no-pipe rules", "(add schemas per data type)"],
     "The Structural Validator loads these. Update here to change what 'valid' means."),
    (".wom/qc-log", "System · QC log",
     "Append-only record of QC decisions (what was auto-repaired vs blocked, with the reason).",
     ["one file per day"], "Audit trail; the Improvement loop mines this for recurring failures."),
]

FRONT = "---\nkind: index\nfolder: {path}\n---\n\n"


def _md(title, purpose, contents, notes) -> str:
    body = f"# {title}\n\n> {purpose}\n\n## Contents\n"
    body += "\n".join(f"- {c}" for c in contents) + "\n\n## For agents\n" + notes + "\n"
    return body


def scaffold(root: Path) -> list[str]:
    specs = list(FOLDERS)
    # generate per-project subfolders
    for proj in PROJECTS:
        ppath = f"10-wiki/projects/{proj}"
        title = proj.replace("-", " ").title()
        specs.append((ppath, f"Project · {title}",
                      f"Living rollup of {title}: scope, key dates, open RFIs/submittals, schedule "
                      f"risk, decisions, and the team. Agents keep this current from the subfolders.",
                      ["rfis/", "submittals/", "schedule/", "meetings/", "closeout/",
                       "index.md (this rollup) — the one-page state of the project"],
                      "Single source of project state. Update the rollup whenever a subfolder note "
                      "changes. Link people ([[Turner GC]]) and products used."))
        for sub, (stitle, sdesc) in PROJECT_SUBS.items():
            specs.append((f"{ppath}/{sub}", f"{title} · {stitle}", sdesc,
                          ["one note per item + the log", "frontmatter ties it to the project"],
                          "Keep the log current; surface anything overdue to the board via a task."))

    written = []
    for path, title, purpose, contents, notes in specs:
        d = root if path == "." else root / path
        d.mkdir(parents=True, exist_ok=True)
        f = d / "index.md"
        f.write_text(FRONT.format(path=path) + _md(title, purpose, contents, notes), encoding="utf-8")
        written.append(str(f.relative_to(root)))
    return written


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    here = Path(__file__).resolve().parents[1]
    ap.add_argument("--root", default=str(here / "backend" / "data" / "vault"))
    args = ap.parse_args()
    out = scaffold(Path(args.root))
    print(f"wrote {len(out)} index.md files under {args.root}")
    for p in out:
        print("  ", p)
