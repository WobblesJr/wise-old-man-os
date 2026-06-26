# Agent topology — Hermes ↔ Dashboard ↔ Claude Code / Cowork

How "everything connected" actually wires up, from Gavin's setup (2026-06-25).

## The machines
```
Windows host (this machine)
├─ Wise Old Man OS  — this dashboard UI + FastAPI backend (serves app + API; owns the delegations bus)
├─ Claude Code      — can run here, on the machine
└─ Claude Cowork    — can run here, on the machine
    │
    └─ Ubuntu VM (guest on the Windows host)
        └─ Hermes agent ("Wise Old Man") — the always-on ORCHESTRATOR.
           Already connected to Claude Code; runs it straight from its operating mode.
```

## The connection: a shared "delegations" bus
The FastAPI backend owns a `delegations` table that is the **single queue/bus** all three sides read
and write. Both Hermes (in the VM) and a local runner (on Windows, where the work happens) reach the
backend over HTTP — from the Ubuntu VM that's the Windows host IP on the VM network, or the public
`https://wise-old-man.xyz` tunnel.

```
delegations: id, scope, agent('claude-code'|'cowork'), job_name, task_id|approval_id,
             status(draft→queued→running→done→needs_approval), elapsed_s, tokens, artifact_ref
```

## The flow (draft-everything posture — nothing fires or lands without a tap)
1. **Dispatch** — from the dashboard, "Dispatch to Claude Code/Cowork" on a build/coding task creates a
   delegation in `draft`. Dispatching is itself a **low-risk approval** → on tap, `status=queued`.
2. **Run** — a **runner** claims queued rows and runs the agent on the Windows machine, streaming
   `running` + token spend. The runner can be **Hermes itself** (it already drives Claude Code) reaching
   the backend from the VM, or a small local worker on Windows. Either way it just speaks the table.
3. **Stage** — on completion the output is NOT auto-applied. It's staged as a pending **approval** of an
   existing kind (`email_send`/`sheet_write`/`schedule_post`) and the row flips to `needs_approval`.
4. **Approve** — the rail's "Review output" deep-links into the Batch-Approve Queue; approval routes
   through `decide()` exactly like every other action.

So: dispatching is a tap, and applying the result is a tap. "Connected" shows up as one band badge +
one drawer — never autonomy.

## The two layers: rules engine + Hermes (built)
The board renders **two distinct layers**, always attributed so you know which is which:
- **Rules engine (deterministic code):** `risk()` scoring, the chaser, the war-board. Consistent,
  explainable, always-on baseline. Labeled "rules engine".
- **Hermes layer (agent judgment):** what Hermes *believes/decides* in real time — reprioritizations,
  insights, alerts — posted from the VM and shown LIVE, tagged "✦ HERMES" (violet), separate from the
  rules. Hermes can override/annotate the rules with its own confidence %.

**Channel (built, mock):** `agent_signals` table + `POST /api/agent/signal` (Hermes posts a belief) +
`GET /api/agent/signals` + `POST /api/agent/signal/{id}/{act|dismiss}` + **`GET /api/agent/stream`
(SSE)** for real time. Signals also ride the `/api/dashboard` bundle (`hermes_signals`). The dashboard
opens an `EventSource` and renders a belief the instant it lands; Act/Dismiss resolve back to the server.
This is how a "very code-centric app" gains live agent judgment. Verified: POST a belief → it appears
on the board in <2s with no refresh.

**To go live:** Hermes (VM) just calls `POST /api/agent/signal` whenever it forms a belief (and reads
`/api/agent/signals` for state). Same contract; only the caller changes from a test to Hermes.

## What's built vs. needed
**Build now (mock, this repo):** the `delegations` table + endpoints (create/list/approve-output) + a
mock runner that flips queued→running→done and stages a sample approval; the band badge + drawer.
Contract is real; only the executor is faked.

**Needs from Gavin (to go live) — see NEEDS-FROM-YOU #7:**
- The exact command/entrypoint Hermes (or a Windows runner) uses to invoke **Claude Code** and
  **Cowork** on the machine for a given job + task context.
- The network path from the Ubuntu VM to the Windows FastAPI (host IP:port, or use the tunnel URL).
- Confirm "Cowork" = Claude Cowork, and whether it runs on Windows or in the VM.
- Auth on these control endpoints (a shared token) so the public domain can't trigger local agents —
  this is the one place the parked auth work matters sooner rather than later.
