#!/usr/bin/env python3
"""Wise Old Man OS — console responder.

Makes a REAL agent answer in the website's Workspace chat. It polls the shared
console (/api/console/messages), and for any new message addressed to one of the
agents it speaks for, it generates a reply with the Anthropic API and posts it
back (/api/console/message). Run this on the SAME host as the backend that serves
your live site (it talks to it over localhost with the service token, so it never
needs to go through Cloudflare Access).

Two engines for generating the reply:
  --engine api  (default)  via the Anthropic API   — needs ANTHROPIC_API_KEY
  --engine cli             via the `claude` CLI     — uses your Claude SUBSCRIPTION login,
                           NO API key needed (`claude` must be installed + `claude login` done)

Env (read from the process env, or from backend/.env / .env if present — never printed):
  WOM_SERVICE_TOKEN   bearer token the backend accepts as a 'machine' identity (required)
  ANTHROPIC_API_KEY   key used to generate replies            (only for --engine api)
  WOM_BASE_URL        backend base URL (default http://127.0.0.1:8787)
  WOM_WORKER_MODEL    optional model id (api default: claude-sonnet-4-6; cli: the CLI default)
  WOM_CLAUDE_BIN      path to the claude CLI (default: 'claude')

Usage:
  # subscription (no API key) — drives the claude CLI:
  python3 tools/console_worker.py --agent claude-code --engine cli
  # API key:
  python3 tools/console_worker.py --agent hermes,claude-code
  python3 tools/console_worker.py --agent hermes --backfill     # also answer history once
"""
from __future__ import annotations

import argparse, json, os, shutil, subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Each agent id the website can address, with the persona it answers as.
PERSONAS = {
    "hermes": (
        "You are Hermes, the orchestrator agent for Gavin's 'Wise Old Man OS' — a personal+work "
        "command center for a construction/MEP project manager. You plan, prioritize, and route "
        "coding/build work to Claude Code, and you stage actions for Gavin's approval (you never send "
        "for real without approval). The app currently runs on MOCK data. Reply in the Workspace chat: "
        "concise, concrete, friendly, 1-4 sentences. If asked to do something that needs real "
        "credentials or a real send, say you'll stage it as an approval."
    ),
    "claude-code": (
        "You are Claude Code, the coding agent running on Gavin's machine for 'Wise Old Man OS'. You "
        "edit the repo, build features, and stage anything that changes files as an approval. Reply in "
        "the Workspace chat: concise, practical, 1-4 sentences. Mention when something would need a "
        "commit/push or real credentials."
    ),
    "cowork": (
        "You are Cowork, a pairing agent for Gavin's 'Wise Old Man OS'. You think out loud with Gavin "
        "and keep Hermes in the loop. Reply in the Workspace chat: warm, concise, 1-4 sentences."
    ),
}
NAMES = {"you": "Gavin", "hermes": "Hermes", "claude-code": "Claude Code", "cowork": "Cowork"}


def load_dotenv() -> None:
    """Best-effort: populate env from backend/.env (without overriding real env)."""
    for p in (ROOT / "backend" / ".env", ROOT / ".env"):
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            os.environ.setdefault(k, v)


def _http(method: str, url: str, headers: dict, body: dict | None = None, timeout: int = 60) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode() or "{}")


def fetch_messages(base: str, token: str, limit: int = 40) -> list[dict]:
    out = _http("GET", f"{base}/api/console/messages?limit={limit}",
                {"Authorization": f"Bearer {token}"})
    return out.get("messages", [])


def post_message(base: str, token: str, scope: str, agent: str, to_agent: str, text: str) -> None:
    _http("POST", f"{base}/api/console/message",
          {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
          {"scope": scope, "agent": agent, "to_agent": to_agent, "text": text})


def generate_reply(api_key: str, model: str, persona: str, thread: list[dict], me: str) -> str:
    """Ask Anthropic for a reply, given the recent thread for context."""
    convo = "\n".join(f"{NAMES.get(m['agent'], m['agent'])}: {m['text']}" for m in thread[-12:])
    user = (f"This is the Workspace chat thread (most recent last):\n\n{convo}\n\n"
            f"Write {NAMES.get(me, me)}'s next reply to the most recent message. Reply text only.")
    out = _http("POST", "https://api.anthropic.com/v1/messages",
                {"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                {"model": model, "max_tokens": 400, "system": persona,
                 "messages": [{"role": "user", "content": user}]})
    parts = [c.get("text", "") for c in out.get("content", []) if c.get("type") == "text"]
    return ("".join(parts)).strip() or "(no reply)"


def generate_reply_cli(claude_bin: str, model: str, persona: str, thread: list[dict], me: str) -> str:
    """Generate a reply by invoking the `claude` CLI headlessly (uses the subscription login)."""
    convo = "\n".join(f"{NAMES.get(m['agent'], m['agent'])}: {m['text']}" for m in thread[-12:])
    user = (f"This is the Workspace chat thread (most recent last):\n\n{convo}\n\n"
            f"Write {NAMES.get(me, me)}'s next reply to the most recent message. "
            f"Reply with the message text only — do not use tools or take any actions.")
    cmd = [claude_bin, "-p", user, "--output-format", "text", "--append-system-prompt", persona]
    if model:
        cmd += ["--model", model]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
    if out.returncode != 0:
        raise RuntimeError((out.stderr or out.stdout or "claude CLI failed").strip()[:400])
    return (out.stdout or "").strip() or "(no reply)"


def state_path(agent: str) -> Path:
    return ROOT / "tools" / f".console_worker_{agent}.json"


def load_seen(agent: str) -> int:
    p = state_path(agent)
    if p.exists():
        try:
            return int(json.loads(p.read_text())["last_id"])
        except Exception:
            return 0
    return 0


def save_seen(agent: str, last_id: int) -> None:
    state_path(agent).write_text(json.dumps({"last_id": last_id}))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", default="hermes",
                    help="comma list of agent ids to answer for: hermes,claude-code,cowork")
    ap.add_argument("--poll", type=float, default=4.0, help="seconds between polls")
    ap.add_argument("--backfill", action="store_true", help="also answer messages already in history")
    ap.add_argument("--engine", choices=["api", "cli"], default="api",
                    help="reply engine: 'api' (ANTHROPIC_API_KEY) or 'cli' (your Claude subscription)")
    ap.add_argument("--claude-bin", default=os.environ.get("WOM_CLAUDE_BIN", "claude"),
                    help="path to the claude CLI (for --engine cli)")
    args = ap.parse_args()

    load_dotenv()
    token = os.environ.get("WOM_SERVICE_TOKEN", "")
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    base = os.environ.get("WOM_BASE_URL", "http://127.0.0.1:8787").rstrip("/")
    model = os.environ.get("WOM_WORKER_MODEL", "")  # api falls back below; cli uses its own default

    agents = [a.strip() for a in args.agent.split(",") if a.strip() in PERSONAS]
    if not agents:
        print("No valid --agent (choose from: %s)" % ", ".join(PERSONAS)); return 2
    if not token or token.startswith("__STUB"):
        print("WOM_SERVICE_TOKEN is not set (or is a stub). Set it so the worker can authenticate."); return 2
    if args.engine == "api":
        if not api_key:
            print("ANTHROPIC_API_KEY is not set. Set it, or use --engine cli to use your Claude subscription."); return 2
        if not model:
            model = "claude-sonnet-4-6"
    else:  # cli (subscription)
        if not shutil.which(args.claude_bin):
            print("The 'claude' CLI was not found (looked for '%s'). Install Claude Code + run `claude login`, "
                  "or pass --claude-bin /path/to/claude." % args.claude_bin); return 2

    # initialize 'seen' watermark so we don't answer the whole backlog unless asked
    seen = {a: (0 if args.backfill else load_seen(a)) for a in agents}
    if not args.backfill:
        try:
            mx = max([m["id"] for m in fetch_messages(base, token)] or [0])
            for a in agents:
                if seen[a] == 0:
                    seen[a] = mx
        except Exception as e:
            print("Could not reach the backend at %s: %s" % (base, e)); return 2

    print("console_worker up — answering for %s against %s via %s%s. Ctrl-C to stop."
          % (", ".join(agents), base, args.engine, (" ("+model+")" if model else "")))
    while True:
        try:
            msgs = fetch_messages(base, token)
            for a in agents:
                persona = PERSONAS[a]
                # new messages addressed to me, not authored by me
                todo = [m for m in msgs if m["id"] > seen[a] and m.get("to_agent") == a and m.get("agent") != a]
                for m in todo:
                    try:
                        reply = (generate_reply_cli(args.claude_bin, model, persona, msgs, a)
                                 if args.engine == "cli"
                                 else generate_reply(api_key, model, persona, msgs, a))
                        post_message(base, token, m.get("scope", "work"), a, m.get("agent", "you"), reply)
                        print("  %s -> %s: %s" % (a, m.get("agent"), reply[:80]))
                    except Exception as e:
                        print("  reply failed for %s (msg %s): %s" % (a, m.get("id"), e))
                    seen[a] = max(seen[a], m["id"])
                    save_seen(a, seen[a])
        except urllib.error.HTTPError as e:
            print("HTTP %s from backend — check WOM_SERVICE_TOKEN / WOM_BASE_URL" % e.code)
        except Exception as e:
            print("poll error: %s" % e)
        time.sleep(args.poll)


if __name__ == "__main__":
    sys.exit(main())
