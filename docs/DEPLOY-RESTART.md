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

## The cron job (auto-pull + restart-if-changed)
`tools/deploy.sh` pulls the repo + the vault sub-repo, reinstalls deps, and restarts **only if code
changed** (static-only pulls skip the restart). Wire it to cron:
```bash
chmod +x tools/deploy.sh
crontab -e
# then add (adjust the path):
@reboot sleep 10 && WOM_REPO_DIR=$HOME/wise-old-man-os /bin/bash $HOME/wise-old-man-os/tools/deploy.sh >>/tmp/wom-deploy.log 2>&1
*/10 * * * * WOM_REPO_DIR=$HOME/wise-old-man-os /bin/bash $HOME/wise-old-man-os/tools/deploy.sh >>/tmp/wom-deploy.log 2>&1
```
With the systemd service installed, `deploy.sh` restarts via `systemctl`; without it, it relaunches
with `nohup`. `@reboot` covers boot; the `*/10` line auto-deploys new commits every 10 minutes.

> Prereq: the VM pulls from a **git remote**, so push the repo (and the vault repo) to GitHub first
> (Milestone 2 / your private `wom-vault`). Until then, `git pull` has nothing to pull.

## Hand-off prompt (paste to Hermes or Claude Code on the VM)
> Set up the Wise Old Man OS backend to run continuously and auto-deploy on this Ubuntu machine.
> The repo is cloned at `$HOME/wise-old-man-os` (adjust if different).
> 1. Install a **systemd service** from `deploy/wom.service` named `wom`: replace `USER` with the real
>    user, point it at `backend/`, load env from the repo-root `.env`, bind `0.0.0.0:8787`, restart on
>    failure, start on boot. `daemon-reload`, then `enable --now`.
> 2. Add two **cron** entries that run `tools/deploy.sh` (with `WOM_REPO_DIR` set): one `@reboot`, one
>    every 10 minutes — it git-pulls the repo + the `backend/data/vault` sub-repo, runs
>    `pip install -r requirements.txt`, and restarts `wom` only when code changed.
> 3. Verify: `systemctl status wom` shows active, `curl -s localhost:8787/api/health` returns ok, and
>    the Cloudflare tunnel (`cloudflared`) reaches `http://localhost:8787`.
> Report back `systemctl status wom`, the installed crontab, and the health-check output.
