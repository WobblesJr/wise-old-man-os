"""Realistic MOCK dataset for Wise Old Man OS.

This is the single source of truth the mock adapters read from. Scope-aware:
most collections come in {"personal": [...], "work": [...]} form.

Dates are relative to a fixed "today" so the UI always looks current without
needing real clock math at import time. The API stamps real timestamps where it
matters; here we use friendly day labels.
"""
from __future__ import annotations

# --------------------------------------------------------------------------- #
# TASKS  — columns mirror the "G-Suite Dashboard" sheet exactly:
#   ! / Description / Start / Follow-up / Due / Owner / Ball in Court /
#   Category / Subcategory / Action / Status
#   action ∈ {action, wait, hold, read, event}   -> color spine
#   status ∈ {not_started, in_progress, completed, delegated, blocked}
# --------------------------------------------------------------------------- #

TASKS = {
    "personal": [
        {"id": "p-t1", "bang": "!", "description": "Renew passport before Italy trip",
         "start": "2026-06-20", "followup": "2026-06-28", "due": "2026-07-10",
         "owner": "Gavin", "ball_in_court": "Me", "category": "Travel", "subcategory": "Documents",
         "action": "action", "status": "in_progress"},
        {"id": "p-t2", "bang": "", "description": "Wait on dentist to confirm cleaning slot",
         "start": "2026-06-22", "followup": "2026-06-26", "due": "2026-06-30",
         "owner": "Gavin", "ball_in_court": "Dr. Pham office", "category": "Health", "subcategory": "Dental",
         "action": "wait", "status": "blocked"},
        {"id": "p-t3", "bang": "", "description": "Read 'The Pragmatic Programmer' ch. 4-6",
         "start": "2026-06-18", "followup": "", "due": "2026-07-05",
         "owner": "Gavin", "ball_in_court": "Me", "category": "Learning", "subcategory": "Reading",
         "action": "read", "status": "in_progress"},
        {"id": "p-t4", "bang": "!", "description": "Pay quarterly estimated taxes",
         "start": "2026-06-24", "followup": "2026-06-27", "due": "2026-06-30",
         "owner": "Gavin", "ball_in_court": "Me", "category": "Finance", "subcategory": "Taxes",
         "action": "action", "status": "not_started"},
        {"id": "p-t5", "bang": "", "description": "Hold: decide on gym membership renewal",
         "start": "2026-06-15", "followup": "2026-07-01", "due": "2026-07-15",
         "owner": "Gavin", "ball_in_court": "Me", "category": "Health", "subcategory": "Fitness",
         "action": "hold", "status": "not_started"},
        {"id": "p-t6", "bang": "", "description": "DC United vs Inter Miami — buy tickets",
         "start": "2026-06-25", "followup": "", "due": "2026-07-12",
         "owner": "Gavin", "ball_in_court": "Me", "category": "Social", "subcategory": "Events",
         "action": "event", "status": "not_started"},
        {"id": "p-t7", "bang": "", "description": "Delegated: ask brother to water plants while away",
         "start": "2026-06-21", "followup": "2026-07-08", "due": "2026-07-09",
         "owner": "Gavin", "ball_in_court": "Marcus", "category": "Home", "subcategory": "Errands",
         "action": "wait", "status": "delegated"},
        {"id": "p-t8", "bang": "", "description": "Update OSRS goals spreadsheet",
         "start": "2026-06-23", "followup": "", "due": "2026-06-29",
         "owner": "Gavin", "ball_in_court": "Me", "category": "Hobby", "subcategory": "OSRS",
         "action": "action", "status": "completed"},
    ],
    "work": [
        {"id": "w-t1", "bang": "!", "description": "Submit RFI on mechanical room clearances",
         "start": "2026-06-22", "followup": "2026-06-26", "due": "2026-06-27",
         "owner": "Gavin", "ball_in_court": "Me", "category": "Project Alpha", "subcategory": "RFI",
         "action": "action", "status": "in_progress"},
        {"id": "w-t2", "bang": "", "description": "Wait on GC response to schedule recovery plan",
         "start": "2026-06-19", "followup": "2026-06-26", "due": "2026-07-01",
         "owner": "Gavin", "ball_in_court": "Turner GC", "category": "Project Alpha", "subcategory": "Schedule",
         "action": "wait", "status": "blocked"},
        {"id": "w-t3", "bang": "", "description": "Read updated mechanical spec section 23 05 00",
         "start": "2026-06-24", "followup": "", "due": "2026-06-30",
         "owner": "Gavin", "ball_in_court": "Me", "category": "Project Beta", "subcategory": "Specs",
         "action": "read", "status": "not_started"},
        {"id": "w-t4", "bang": "!", "description": "Manpower-loaded schedule for Level 3 buildout",
         "start": "2026-06-20", "followup": "2026-06-26", "due": "2026-06-28",
         "owner": "Gavin", "ball_in_court": "Me", "category": "Project Alpha", "subcategory": "Planning",
         "action": "action", "status": "in_progress"},
        {"id": "w-t5", "bang": "", "description": "Hold: VE option on chilled water piping",
         "start": "2026-06-18", "followup": "2026-07-02", "due": "2026-07-10",
         "owner": "Gavin", "ball_in_court": "Me", "category": "Project Beta", "subcategory": "VE",
         "action": "hold", "status": "not_started"},
        {"id": "w-t6", "bang": "", "description": "Pre-con meeting — Level 4 rough-in",
         "start": "2026-06-29", "followup": "", "due": "2026-06-29",
         "owner": "Gavin", "ball_in_court": "Me", "category": "Project Alpha", "subcategory": "Meeting",
         "action": "event", "status": "not_started"},
        {"id": "w-t7", "bang": "", "description": "Delegated submittal log cleanup to coordinator",
         "start": "2026-06-21", "followup": "2026-06-27", "due": "2026-07-03",
         "owner": "Gavin", "ball_in_court": "Priya (coord)", "category": "Project Beta", "subcategory": "Submittals",
         "action": "wait", "status": "delegated"},
        {"id": "w-t8", "bang": "", "description": "Close out punchlist items from last walkthrough",
         "start": "2026-06-17", "followup": "", "due": "2026-06-24",
         "owner": "Gavin", "ball_in_court": "Me", "category": "Project Alpha", "subcategory": "Closeout",
         "action": "action", "status": "completed"},
    ],
}

# --------------------------------------------------------------------------- #
# APPROVALS — things the agent drafted and is waiting on a one-tap OK to do.
# --------------------------------------------------------------------------- #

APPROVALS = {
    "personal": [
        {"id": "p-a1", "kind": "email_send", "title": "Reply to dentist re: reschedule",
         "summary": "Confirm Tuesday 9:00 AM cleaning, ask to move to afternoon.",
         "target": "Dr. Pham Dental <front@phamdental.example>", "draft_id": "p-d1",
         "risk": "low", "status": "pending"},
        {"id": "p-a2", "kind": "calendar_create", "title": "Add 'Passport appointment' to calendar",
         "summary": "Mon Jul 6, 10:30 AM at USPS Main St. 45 min + travel buffer.",
         "target": "Personal calendar", "draft_id": None, "risk": "low", "status": "pending"},
        {"id": "p-a3", "kind": "sheet_write", "title": "Mark 'OSRS goals' task complete",
         "summary": "Set status=completed on row p-t8 in G-Suite Dashboard.",
         "target": "G-Suite Dashboard / Tasks", "draft_id": None, "risk": "low", "status": "pending"},
    ],
    "work": [
        {"id": "w-a1", "kind": "email_send", "title": "Send RFI cover note to GC",
         "summary": "Attach RFI-014, request response by Fri to protect schedule.",
         "target": "Turner GC <pm@turner.example>", "draft_id": "w-d1",
         "risk": "medium", "status": "pending"},
        {"id": "w-a2", "kind": "schedule_post", "title": "Post manpower schedule draft to team",
         "summary": "Share Level 3 manpower-loaded schedule v0.3 in #project-alpha.",
         "target": "Discord #project-alpha", "draft_id": "w-d2", "risk": "low", "status": "pending"},
    ],
}

# --------------------------------------------------------------------------- #
# DRAFTS — full bodies behind the approvals (and standalone drafts).
# --------------------------------------------------------------------------- #

DRAFTS = {
    "p-d1": {"id": "p-d1", "kind": "email", "to": "front@phamdental.example",
             "subject": "Re: Cleaning appointment",
             "body": "Hi — Tuesday 9:00 AM works, but an afternoon slot would be ideal if "
                     "anything opens up. Either way please confirm. Thanks!\n\n— Gavin"},
    "w-d1": {"id": "w-d1", "kind": "email", "to": "pm@turner.example",
             "subject": "RFI-014 — Mechanical room clearances",
             "body": "Please find RFI-014 attached regarding clearances at the L2 mechanical "
                     "room. A response by Friday keeps the rough-in sequence on track.\n\n"
                     "Regards,\nGavin"},
    "w-d2": {"id": "w-d2", "kind": "discord", "to": "#project-alpha",
             "subject": "Manpower schedule v0.3",
             "body": "Posting Level 3 manpower-loaded schedule v0.3 for review. Peak crew week "
                     "of 7/13 at 14 workers. Flag conflicts by EOD Thursday."},
}

# --------------------------------------------------------------------------- #
# INBOX — unified message surface (email/Discord/system).
# --------------------------------------------------------------------------- #

INBOX = {
    "personal": [
        {"id": "p-i1", "source": "gmail", "from": "USPS", "subject": "Your appointment options",
         "snippet": "Several passport appointment slots are available next week...",
         "unread": True, "ts": "2h ago"},
        {"id": "p-i2", "source": "gmail", "from": "DC United", "subject": "Presale starts today",
         "snippet": "Members get first access to the Inter Miami match...",
         "unread": True, "ts": "5h ago"},
        {"id": "p-i3", "source": "discord", "from": "#osrs-clan", "subject": "Raids tonight?",
         "snippet": "We're forming a team for ToB at 8...", "unread": False, "ts": "Yesterday"},
    ],
    "work": [
        {"id": "w-i1", "source": "gmail", "from": "Turner GC", "subject": "RE: Schedule recovery",
         "snippet": "We can meet Thursday to walk the recovery plan...", "unread": True, "ts": "1h ago"},
        {"id": "w-i2", "source": "gmail", "from": "Priya (coord)", "subject": "Submittal log updated",
         "snippet": "Cleaned up the open items, 3 still need your sign-off...", "unread": True, "ts": "3h ago"},
        {"id": "w-i3", "source": "discord", "from": "#project-alpha", "subject": "Field photos",
         "snippet": "Posted today's L3 rough-in progress photos...", "unread": False, "ts": "Yesterday"},
    ],
}

# --------------------------------------------------------------------------- #
# SUGGESTED NEXT STEPS — the hero tile. Each has a one-tap action.
# action_kind maps to a backend action endpoint (all stubbed/no-op in mock).
# --------------------------------------------------------------------------- #

SUGGESTIONS = {
    "personal": [
        {"id": "p-s1", "title": "Book your passport appointment",
         "rationale": "Due Jul 10 and you have 2 RFI-free mornings next week.",
         "action_label": "Add to calendar", "action_kind": "approve", "ref": "p-a2", "urgency": "high"},
        {"id": "p-s2", "title": "Pay quarterly estimated taxes",
         "rationale": "Due Jun 30 — 5 days. Not started yet.",
         "action_label": "Open checklist", "action_kind": "open_task", "ref": "p-t4", "urgency": "high"},
        {"id": "p-s3", "title": "Confirm dentist reschedule",
         "rationale": "Draft reply ready; they're waiting on you.",
         "action_label": "Review & send", "action_kind": "approve", "ref": "p-a1", "urgency": "med"},
        {"id": "p-s4", "title": "Grab DC United presale tickets",
         "rationale": "Presale started 5h ago; you flagged this match.",
         "action_label": "Open task", "action_kind": "open_task", "ref": "p-t6", "urgency": "low"},
    ],
    "work": [
        {"id": "w-s1", "title": "Send RFI-014 cover note to GC",
         "rationale": "Protects the L2 rough-in sequence; draft is ready.",
         "action_label": "Review & send", "action_kind": "approve", "ref": "w-a1", "urgency": "high"},
        {"id": "w-s2", "title": "Finish Level 3 manpower-loaded schedule",
         "rationale": "Due Jun 28; v0.3 drafted, needs your crew-curve sign-off.",
         "action_label": "Open task", "action_kind": "open_task", "ref": "w-t4", "urgency": "high"},
        {"id": "w-s3", "title": "Accept Thursday recovery-plan meeting",
         "rationale": "Turner GC replied 1h ago proposing Thursday.",
         "action_label": "Add to calendar", "action_kind": "open_inbox", "ref": "w-i1", "urgency": "med"},
        {"id": "w-s4", "title": "Sign off 3 open submittals",
         "rationale": "Priya cleaned the log; 3 items need you.",
         "action_label": "Open inbox", "action_kind": "open_inbox", "ref": "w-i2", "urgency": "low"},
    ],
}

# --------------------------------------------------------------------------- #
# TODAY — calendar + time-boxed items.
# --------------------------------------------------------------------------- #

TODAY = {
    "personal": [
        {"id": "p-c1", "time": "12:30 PM", "title": "Lunch with Marcus", "where": "Cava", "kind": "event"},
        {"id": "p-c2", "time": "3:00 PM", "title": "Call: car insurance renewal", "where": "Phone", "kind": "action"},
        {"id": "p-c3", "time": "8:00 PM", "title": "OSRS raid (ToB)", "where": "Discord", "kind": "event"},
    ],
    "work": [
        {"id": "w-c1", "time": "9:00 AM", "title": "Daily huddle — Project Alpha", "where": "Trailer", "kind": "event"},
        {"id": "w-c2", "time": "11:00 AM", "title": "Coordination call — MEP clash", "where": "Teams", "kind": "event"},
        {"id": "w-c3", "time": "2:00 PM", "title": "Walk L3 rough-in", "where": "Site", "kind": "action"},
    ],
}

# --------------------------------------------------------------------------- #
# USAGE LEDGER — token volume + Max-plan usage. Drives cockpit + dashboard tile.
# --------------------------------------------------------------------------- #

USAGE = {
    "plan": "Claude Max 20x",
    "window_resets_in": "3h 12m",
    "plan_usage_pct": 41,            # % of current 5-hour window consumed
    "tokens_today": 1_284_500,
    "tokens_week": 7_932_100,
    "by_day": [
        {"day": "Thu", "tokens": 980_000},
        {"day": "Fri", "tokens": 1_420_000},
        {"day": "Sat", "tokens": 640_000},
        {"day": "Sun", "tokens": 720_000},
        {"day": "Mon", "tokens": 1_510_000},
        {"day": "Tue", "tokens": 1_377_600},
        {"day": "Wed", "tokens": 1_284_500},
    ],
    "ledger": [
        {"id": "u1", "ts": "09:14", "agent": "Inbox triage", "model": "claude-opus-4-8",
         "tokens": 18420, "cost_note": "Max plan", "scope": "work"},
        {"id": "u2", "ts": "09:02", "agent": "Suggestion engine", "model": "claude-opus-4-8",
         "tokens": 9650, "cost_note": "Max plan", "scope": "personal"},
        {"id": "u3", "ts": "08:47", "agent": "RFI drafter", "model": "claude-opus-4-8",
         "tokens": 22110, "cost_note": "Max plan", "scope": "work"},
        {"id": "u4", "ts": "08:30", "agent": "Schedule builder", "model": "claude-opus-4-8",
         "tokens": 41200, "cost_note": "Max plan", "scope": "work"},
        {"id": "u5", "ts": "07:55", "agent": "Memory sync", "model": "claude-haiku-4-5",
         "tokens": 3300, "cost_note": "Max plan", "scope": "personal"},
    ],
}

# --------------------------------------------------------------------------- #
# AGENT / SYSTEM cockpit data.
# --------------------------------------------------------------------------- #

CONNECTIONS = [
    {"id": "c1", "name": "Google — Personal", "scope": "personal",
     "detail": "Gmail · Calendar · Drive · Sheets", "status": "stubbed",
     "note": "OAuth pending (NEEDS-FROM-YOU #1)"},
    {"id": "c2", "name": "G-Suite Dashboard Sheet", "scope": "personal",
     "detail": "Task source-of-truth", "status": "stubbed",
     "note": "Sheet ID pending (NEEDS-FROM-YOU #2)"},
    {"id": "c3", "name": "Limbach — Work", "scope": "work",
     "detail": "Work Drive bridge", "status": "blocked",
     "note": "Pending IT (NEEDS-FROM-YOU #4)"},
    {"id": "c4", "name": "Cloudflare Tunnel", "scope": "both",
     "detail": "Public hostname for VPS", "status": "stubbed",
     "note": "Hostname pending (NEEDS-FROM-YOU #3)"},
    {"id": "c5", "name": "OSRS Feeds", "scope": "personal",
     "detail": "Hiscores + Wiki prices", "status": "mock", "note": "Public APIs; mock for now"},
    {"id": "c6", "name": "Discord", "scope": "both",
     "detail": "Notify + console relay", "status": "stubbed", "note": "Bot token pending"},
    {"id": "c7", "name": "Memory (Obsidian git)", "scope": "both",
     "detail": "Vault sync", "status": "stubbed", "note": "Vault path pending"},
]

SCHEDULED_JOBS = [
    {"id": "j1", "name": "Inbox triage", "cron": "*/15 * * * *", "last": "12m ago",
     "next": "in 3m", "runner": "Hermes cron", "status": "ok"},
    {"id": "j2", "name": "Suggestion refresh", "cron": "0 */1 * * *", "last": "24m ago",
     "next": "in 36m", "runner": "Hermes cron", "status": "ok"},
    {"id": "j3", "name": "Sheet ↔ cache sync", "cron": "*/10 * * * *", "last": "4m ago",
     "next": "in 6m", "runner": "Hermes cron", "status": "stubbed"},
    {"id": "j4", "name": "Feeds pull (OSRS/news)", "cron": "0 */6 * * *", "last": "2h ago",
     "next": "in 4h", "runner": "Hermes cron", "status": "mock"},
    {"id": "j5", "name": "Memory git push", "cron": "0 22 * * *", "last": "—",
     "next": "tonight 22:00", "runner": "Hermes cron", "status": "stubbed"},
]

SKILLS = [
    {"id": "sk1", "name": "Inbox triage", "desc": "Cluster + summarize unread, propose replies", "scope": "both"},
    {"id": "sk2", "name": "RFI drafter", "desc": "Draft construction RFIs from context", "scope": "work"},
    {"id": "sk3", "name": "Manpower schedule", "desc": "Build manpower-loaded schedules (xlsx)", "scope": "work"},
    {"id": "sk4", "name": "Suggestion engine", "desc": "Rank next-best actions across scopes", "scope": "both"},
    {"id": "sk5", "name": "Memory keeper", "desc": "Write/recall facts to Obsidian vault", "scope": "both"},
    {"id": "sk6", "name": "Feed watcher", "desc": "OSRS hiscores/prices, events, news", "scope": "personal"},
    {"id": "sk7", "name": "Quick capture", "desc": "Turn a note into a task/draft", "scope": "both"},
]

# --------------------------------------------------------------------------- #
# MEMORY — recent facts (quick-capture surface).
# --------------------------------------------------------------------------- #

MEMORY = {
    "personal": [
        {"id": "m-p1", "text": "Prefers afternoon appointments when possible.", "tag": "preference", "ts": "today"},
        {"id": "m-p2", "text": "Italy trip dates: Jul 12–22. Passport must be valid.", "tag": "travel", "ts": "2d ago"},
        {"id": "m-p3", "text": "OSRS main goal: quest cape before fall.", "tag": "hobby", "ts": "5d ago"},
    ],
    "work": [
        {"id": "m-w1", "text": "GC PM is Dana at Turner; responds fastest mid-morning.", "tag": "contact", "ts": "today"},
        {"id": "m-w2", "text": "Project Alpha peak manpower target: 14 in mid-July.", "tag": "project", "ts": "1d ago"},
        {"id": "m-w3", "text": "VE chilled-water option on hold pending owner decision.", "tag": "project", "ts": "3d ago"},
    ],
}

# --------------------------------------------------------------------------- #
# FEEDS — OSRS hiscores/prices, World Cup, DC events, news.
# --------------------------------------------------------------------------- #

FEEDS = {
    "osrs_hiscores": {"username": "MockedMain", "total_level": 1987, "total_xp": 145_209_331,
                      "combat": 112, "highlights": [
                          {"skill": "Slayer", "level": 95, "xp": 9_120_445},
                          {"skill": "Farming", "level": 91, "xp": 6_010_223},
                          {"skill": "Construction", "level": 84, "xp": 3_120_900}]},
    "osrs_prices": [
        {"item": "Twisted bow", "price": 1_241_000_000, "change_pct": -1.8},
        {"item": "Scythe of vitur", "price": 712_500_000, "change_pct": 0.6},
        {"item": "Dragon claws", "price": 92_400_000, "change_pct": 2.3}],
    "world_cup": [
        {"match": "USA vs Mexico", "when": "Sat 7:00 PM", "stage": "Group", "venue": "Mock Stadium"},
        {"match": "Brazil vs France", "when": "Sun 3:00 PM", "stage": "Group", "venue": "Mock Arena"}],
    "dc_events": [
        {"title": "DC United vs Inter Miami", "when": "Jul 12, 7:30 PM", "venue": "Audi Field"},
        {"title": "Jazz in the Garden", "when": "Jul 4, 5:00 PM", "venue": "National Gallery"}],
    "news": [
        {"title": "Local: Metro extends weekend hours", "source": "WaPo (mock)", "ts": "1h ago"},
        {"title": "Construction costs ease 2% QoQ", "source": "ENR (mock)", "ts": "4h ago"},
        {"title": "RuneScape: new raid teased", "source": "OSRS News (mock)", "ts": "Yesterday"}],
}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def scope_get(collection: dict, scope: str):
    """Return scope slice, defaulting to personal."""
    return collection.get(scope, collection.get("personal", []))


def task_counts(scope: str) -> dict:
    """Counts by action-type and by status for the 'Tasks at a glance' tile."""
    rows = scope_get(TASKS, scope)
    by_action: dict[str, int] = {}
    by_status: dict[str, int] = {}
    mine = 0
    for r in rows:
        if r["status"] == "completed":
            # still count completed in status, but they don't dominate "open"
            pass
        by_action[r["action"]] = by_action.get(r["action"], 0) + 1
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
        if r.get("ball_in_court") == "Me" and r["status"] != "completed":
            mine += 1
    return {
        "total": len(rows),
        "open": sum(1 for r in rows if r["status"] != "completed"),
        "mine": mine,
        "by_action": by_action,
        "by_status": by_status,
    }
