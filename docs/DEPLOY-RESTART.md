# Restart / redeploy the backend

## TL;DR — what actually needs a restart
- **Static files** (`preview/index.html`, icons, manifest — e.g. the iOS safe-area fix): the server
  serves them fresh from disk every request. **No restart.** Just get the new file on the server
  (`git pull`) and refresh the PWA on the phone (pull-to-refresh, or close/reopen; once = re-add to
  Home Screen if stubborn — the service worker is network-first so it self-updates).
- **Python/backend code** (`backend/app/**`): restart uvicorn (below). If you run with `--reload`
  (the `run.sh`/`run.ps1` default), it auto-reloads on save — no manual restart in dev.

## Manual restart
```bash
# if running via systemd (recommended):
sudo systemctl restart wom
# if you launched it by hand:
pkill -f 'uvicorn app.main:app'; cd backend && WOM_HOST=0.0.0.0 python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8787
```

## Recommended: run it as a service (stays up, restarts on crash + boot)
A long-running server belongs in **systemd**, not cron. Cron is only good for the *periodic git-pull*.
```bash
sudo cp deploy/wom.service /etc/systemd/system/wom.service
sudo sed -i "s/USER/$USER/g" /etc/systemd/system/wom.service   # fix the paths
sudo systemctl daemon-reload
sudo systemctl enable --now wom        # start now + on every boot
systemctl status wom                    # verify it's listening on 0.0.0.0:8787
```

## The cron job (periodic git-pull only — systemd owns liveness)
**Division of responsibility:** systemd runs the server and keeps it alive (crash + boot). Cron's
*only* job is to pull new commits on a schedule; when code changed, `deploy.sh` asks systemd to
restart (`systemctl restart wom`). Don't use a cron `@reboot` to launch the server — systemd's
`enable --now` already starts it on boot, and two launchers would fight for port 8787.
```bash
chmod +x tools/deploy.sh
crontab -e
# one line — periodic pull; restart is delegated to systemd inside the script:
*/10 * * * * WOM_REPO_DIR=$HOME/wise-old-man-os /bin/bash $HOME/wise-old-man-os/tools/deploy.sh >>/tmp/wom-deploy.log 2>&1
```
`deploy.sh` skips the restart entirely on static-only pulls (the server serves those fresh).

> Prereq: the VM pulls from a **git remote**, so push the repo (and the vault repo) to GitHub first
> (Milestone 2 / your private `wom-vault`). Until then, `git pull` has nothing to pull.

## Hand-off prompt (paste to Hermes or Claude Code on the VM)
> Set up the Wise Old Man OS backend to run continuously and auto-deploy on this Ubuntu machine. The
> repo is cloned at `$HOME/wise-old-man-os` (adjust if different).
>
> **Architecture — keep these two jobs separate:** **systemd** owns *running and keeping the backend
> alive* (auto-restart on crash, auto-start on boot). **cron** does *only* the periodic git-pull and
> delegates any restart back to systemd. A bare cron job can't keep a server alive or survive reboots
> reliably, so do NOT use cron to launch the server (no `@reboot` start line) — that would double-launch
> and fight for port 8787.
>
> 1. **systemd (the runner):** install `deploy/wom.service` as `wom` — replace `USER` with the real
>    user, point `WorkingDirectory` at `backend/`, `EnvironmentFile` at the repo-root `.env`, bind
>    `0.0.0.0:8787`, `Restart=always`. `daemon-reload`, then `enable --now` (this also covers boot).
> 2. **cron (pull only):** add ONE entry — every 10 minutes run `tools/deploy.sh` (with `WOM_REPO_DIR`
>    set). It git-pulls the repo + the `backend/data/vault` sub-repo, runs `pip install -r
>    requirements.txt`, and **when code changed restarts via `systemctl restart wom`** (skips the
>    restart on static-only pulls). No `@reboot` line — systemd already covers boot.
> 3. **Verify:** `systemctl status wom` is active + enabled; `curl -s localhost:8787/api/health`
>    returns ok; `cloudflared` reaches `http://localhost:8787`.
> Report back `systemctl status wom`, the one-line crontab, and the health-check output.
