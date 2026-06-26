# Hermes (Wise Old Man) — orchestrator setup checklist

Everything to install / connect / configure on the **Hermes agent** so it can run as the
always-on orchestrator that drives this dashboard, spawns sub-agents, and continually thinks.

**Status legend:** ✅ have · 🟡 need from you · 🔴 blocked · 🆕 to build (in this repo) · 🌐 public/no-key

Hermes lives in the **Ubuntu VM** on the Windows host. The WOM dashboard (FastAPI) is the shared
bus + display. Hermes READS state and WRITES beliefs/actions over the API.

---

## 0. The brain (Hermes runtime itself)
| Item | What / why | Status | Provide |
|------|-----------|--------|---------|
| **Anthropic API key** | Hermes's own reasoning + every sub-agent it spawns. | 🟡 | `ANTHROPIC_API_KEY` in the VM. |
| **Model choice** | Orchestration/reasoning → `claude-opus-4-8`; cheap high-frequency sub-tasks → `claude-haiku-4-5-20251001`; mid → `claude-sonnet-4-6`. | ✅ ids known | — |
| **Agent runtime** | The "continually think" loop + sub-agent spawning. Use the **Claude Agent SDK** (or Claude Code's task spawning, already connected). | 🟡 | Install SDK in the VM; a long-running daemon/loop. |
| **Sub-agent pattern** | Hermes = orchestrator; spawns scoped sub-agents (triage, drafter, scheduler, researcher) and a verifier. | 🆕 design | Define the roster (see §4 Skills). |
| **Scratch memory** | Working state between think-cycles (what it already decided/sent). | 🟡 | A local store or reuse the memory vault (§3). |

---

## 1. Connection to the WOM dashboard (the shared bus)
Hermes talks to the backend over HTTP. Network path VM→Windows: host IP:8787 on the VM network,
or the public `https://wise-old-man.xyz` tunnel.

**Reads (state):** `GET /api/dashboard?scope=` · `/api/tasks` · `/api/approvals` · `/api/warboard` ·
`/api/cockpit` · `/api/usage` · `/api/agent/signals` · **SSE `/api/agent/stream`**.
**Writes (act — all draft-everything, nothing auto-sends):**
`POST /api/agent/signal` (post a belief — LIVE on the board) · `/api/agent/priority` (set a task's
P0–P4 — overlay, not the sheet) · `/api/console/message` (multi-agent shared console) · `/api/capture` ·
`/api/tasks` (quick-add) · `PATCH /api/tasks/{id}` · `/api/approvals/decide` · `/api/actions/{schedule,run}` ·
`/api/warboard/run` · `/api/chaser/run` · `/api/refresh` · `/api/delegations*` (🆕).

| Item | Status | Provide |
|------|--------|---------|
| **Network path VM→Windows backend** | 🟡 | host IP:port or the tunnel URL. |
| **Shared control token** | 🟡🆕 | A bearer token on the write/control endpoints so the public domain can't drive local agents. (Ties to parked auth — needed once public.) |
| **The API contract** | ✅ built | All endpoints above exist except `/api/delegations*`. |

---

## 2. OAuth / accounts
| Connector | Scopes / detail | Status | Provide |
|-----------|-----------------|--------|---------|
| **Google — Personal** (Gmail, Calendar, Drive, Sheets) | `gmail.readonly`, `calendar` (read; write for events), `drive.readonly`, **`spreadsheets` (read+write)** | 🟡 | OAuth client id+secret + one-time consent token. (NEEDS #1) |
| **G-Suite Dashboard Sheet** | the task source-of-truth; sheet id + tab + column order | 🟡 | Sheet ID (+ confirm columns). (NEEDS #2) |
| **Limbach — Work** (Drive/Graph) | work files bridge | 🔴 pending IT | Graph app reg or synced path. (NEEDS #4) |
| **Discord** | notify + console relay + war-board fan-out | 🟡 | bot token + default channel id. |
| **Anthropic** | the brain (§0) | 🟡 | API key. |

---

## 3. Connectors / data sources (adapters)
Each is a clean interface in `backend/app/adapters/` (mock now → swap to live).
| Adapter | Source | Status | Needs |
|---------|--------|--------|-------|
| GooglePersonal | Gmail/Calendar/Drive/Sheets | 🟡 | OAuth (§2) |
| SheetTasks | the G-Suite Dashboard sheet (read+append+update) | 🟡 | Sheet ID (§2) |
| DriveBridge | Limbach work files | 🔴 | IT (§2) |
| Feeds → OSRS Hiscores | `secure.runescape.com/.../index_lite.ws?player=` | 🌐 | just the username |
| Feeds → OSRS Wiki prices | `prices.runescape.wiki/api/v1/osrs/latest` | 🌐 | — |
| Feeds → News | a news provider | 🟡 | `NEWS_API_KEY` |
| Feeds → World Cup / DC events | a source (curated ok) | 🟡 | pick a source or keep curated |
| Memory (Obsidian git vault) | recall + write facts | 🟡 | vault path + git remote |
| Discord | post/relay | 🟡 | bot token (§2) |

---

## 4. Skills (capabilities Hermes runs / delegates to sub-agents)
Already modeled in the cockpit; each maps to a dashboard surface.
| Skill | Does | Surface | Status |
|-------|------|---------|--------|
| Inbox triage | cluster/summarize unread, propose replies | Inbox + Approvals | ✅ logic, 🟡 live data |
| RFI drafter | draft construction RFIs | Approvals (email_send) | ✅ mock |
| Manpower schedule | build manpower-loaded xlsx | delegation → file | ✅ `tools/manpower_schedule.py` |
| Suggestion engine | rank next-best actions | hero | ✅ rules |
| **Risk scorer** | band every task green/amber/red | whole board | ✅ `risk.py` |
| **Ball-in-Court chaser** | auto-draft escalation nudges | Approvals + Ledger | ✅ `chaser.py` |
| **War-Board** | one brief, fan out to Discord+Memory | band + 6am cron | ✅ `warboard.py` |
| **Belief poster** | post real-time judgments to the board | ✦ HERMES strip | ✅ `POST /api/agent/signal` |
| **Delegation dispatcher** | hand build/coding jobs to Claude Code/Cowork | delegation rail | 🆕 contract designed |
| Memory keeper | write/recall facts | Memory tile | 🟡 vault |
| Feed watcher | OSRS/news/events | (feeds) | 🌐/🟡 |
| Quick capture | note → task/draft | quick-capture | ✅ mock |

**New sub-agents to define on Hermes:** triage, drafter, scheduler/backsolver, researcher, verifier
(adversarial check before any draft becomes an approval).

---

## 5. Cron jobs (scheduled thinking — "Hermes cron")
Each is a schedule that calls a dashboard endpoint (or runs a skill then posts results).
| Job | Cadence | Calls | Status |
|-----|---------|-------|--------|
| Cache/refresh | every ~10 min | `POST /api/refresh` | ✅ |
| **Morning War-Board fan-out** | weekday ~6am | `POST /api/warboard/run` → Discord+Memory | ✅ |
| Ball-in-Court chaser sweep | every ~15 min | `POST /api/chaser/run` | ✅ |
| Inbox triage | every ~15 min | triage skill → approvals | 🟡 live |
| Suggestion refresh | hourly | rebuild hero | ✅ rules |
| Sheet ↔ cache sync | every ~10 min | Sheets read/write | 🟡 live |
| Feeds pull | every ~6 h | OSRS/news | 🌐/🟡 |
| Memory git push | nightly | commit+push vault | 🟡 |
| End-of-day nudge | ~6 pm | post a display-only signal | 🆕 (Phase 3) |
| **Continuous think loop** | always | read board → form beliefs → `POST /api/agent/signal` | 🆕 (Hermes core) |

Runner: **Hermes itself** is the cron driver (it already drives Claude Code), or a `cron`/systemd
timer in the VM hitting the endpoints.

---

## 6. Control bridge → Claude Code + Cowork
Lets Hermes (and you, from the board) dispatch build/coding jobs to run **on the Windows machine**.
| Item | Status | Provide |
|------|--------|---------|
| `delegations` table + `/api/delegations*` endpoints + rail UI | 🆕 to build (contract ready) | — |
| Claude Code invocation command (+ how task context passed) | 🟡 | the entrypoint Hermes/runner uses |
| Cowork invocation (confirm = Claude Cowork; Windows or VM?) | 🟡 | confirm + entrypoint |
| Runner | 🟡 | Hermes as runner, or a small Windows worker |
See `docs/ARCHITECTURE-AGENTS.md`. Draft-everything: dispatch + apply are both taps.

---

## 7. Infra / hosting
| Item | Status | Provide |
|------|--------|---------|
| Domain **wise-old-man.xyz** | ✅ chosen | — |
| Cloudflare tunnel + DNS + **HTTPS** (required for PWA install) | 🟡 | stand up `cloudflared` → backend |
| VPS / host for the backend | 🟡 | where FastAPI runs (or the Windows host) |
| VM↔host networking | 🟡 | path for Hermes to reach the backend |
| Auth gate (single-user, later multi-user) | 🅿️ backburner | `docs/BACKLOG.md` |

---

## Minimum to "go live" (do these first, in order)
1. **Anthropic API key** in the VM + the Agent-SDK think-loop → Hermes can reason + spawn sub-agents.
2. **Network path + shared token** → Hermes can read the board and `POST /api/agent/signal` for real.
   *(At this point the HERMES layer is live with zero other creds.)*
3. **Google OAuth + Sheet ID** → flips tasks/inbox/calendar from mock to real (the biggest jump).
4. **Discord bot token** → war-board + chaser fan-out actually post.
5. **Cloudflare tunnel + HTTPS on wise-old-man.xyz** → phone install + public access.
6. Build the **`/api/delegations*`** bridge here, then wire the Claude Code/Cowork runner.

Everything else (Limbach, news/feeds, memory vault) can follow without blocking the core loop.
