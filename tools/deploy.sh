#!/usr/bin/env bash
# Wise Old Man OS — pull latest + (re)start the backend. Safe to run from cron.
# Set WOM_REPO_DIR to where the repo lives on this host (the Ubuntu VM).
set -uo pipefail

REPO_DIR="${WOM_REPO_DIR:-$HOME/wise-old-man-os}"
BIND="${WOM_HOST:-0.0.0.0}"          # 0.0.0.0 so the tunnel/VM can reach it
PORT="${WOM_PORT:-8787}"
cd "$REPO_DIR" || { echo "repo not at $REPO_DIR"; exit 1; }

before="$(git rev-parse HEAD 2>/dev/null || echo none)"
git pull --ff-only 2>&1 | sed 's/^/[main] /' || true
# the vault is its own git repo
if [ -d backend/data/vault/.git ]; then
  ( cd backend/data/vault && git pull --ff-only 2>&1 | sed 's/^/[vault] /' || true )
fi
after="$(git rev-parse HEAD 2>/dev/null || echo none)"

cd backend || exit 1
python3 -m pip install -q -r requirements.txt 2>/dev/null || true

# Static-only change (e.g. preview/index.html)? The server serves it fresh — no restart needed.
# Restart only when code actually changed, or if the server isn't running.
running="$(pgrep -f 'uvicorn app.main:app' || true)"
if [ "$before" != "$after" ] || [ -z "$running" ]; then
  if systemctl list-unit-files 2>/dev/null | grep -q '^wom.service'; then
    sudo systemctl restart wom && echo "restarted via systemd"
  else
    pkill -f 'uvicorn app.main:app' 2>/dev/null; sleep 1
    WOM_HOST="$BIND" nohup python3 -m uvicorn app.main:app --host "$BIND" --port "$PORT" \
      >>/tmp/wom.log 2>&1 & echo "restarted (nohup, pid $!)"
  fi
else
  echo "no code change + server up — nothing to restart (static files already served fresh)"
fi
echo "deploy done $(date -u +%FT%TZ)  ${before:0:7} -> ${after:0:7}"
