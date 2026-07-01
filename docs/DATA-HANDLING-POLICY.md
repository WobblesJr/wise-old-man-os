# Data-Flow & Retention Policy — Wise Old Man OS

**Prepared for:** Limbach IT / Security Review  
**System:** Wise Old Man OS (Hermes Agent + FastAPI backend)  
**Requested scope:** Read-only Google Drive access (My Drive + PM Shared Drives)  
**Document date:** June 29, 2026  
**Status:** Proposed integration — no Google Drive access is currently live.

---

## 1. What It Reads

The proposed integration requests **one OAuth scope**: `https://www.googleapis.com/auth/drive.readonly`. This grants read-only access to:

- The user's **My Drive** and any **Shared Drives** the OAuth client is permitted to see.
- File metadata (name, id, modified date, owner) and file **content** for Google-native formats (Docs, Sheets, Slides) via the Drive API export endpoint.
- **Cannot** create, modify, delete, upload, or share any files. The scope is enforced by Google's OAuth server at the API call level — the app never receives a token with write permissions.

**Current state:** `WOM_DATA_MODE=mock` — no real Drive/Sheets API calls are made. All data displayed is static sample data included in the repo. The `drive_bridge.py` adapter that would handle Drive reads is **stubbed with TODO comments** (`# TODO(live): LiveDriveBridge — BLOCKED pending IT`). No Live adapater has been implemented.

**Gap:** The backend has a `google_personal.py` adapter for Gmail/Calendar/Drive with a stub class (`MockGooglePersonal`). The live version exists only as comments and a TODO. No Drive read code has been written or tested.

---

## 2. Data Flow

```
Google Drive (read-only)
        │
        │  Drive API (REST, HTTPS)
        ▼
  Hermes Backend — FastAPI on localhost:8787
        │
        ├── SQLite cache ── backend/data/wom.db
        ├── Vault files ─── backend/data/vault/tasks/*.md
        └── Console messages (SQLite) ── multi-agent chat history
              │
              │  POST /api/agent/signal
              │  (task summaries & beliefs — not raw document text)
              ▼
     Hermes Agent ── runs on same WSL VM
              │
              │  Anthropic API (Claude Max, OAuth)
              │
              ▼
     Claude Sonnet 4 (external AI model)
              │
              │  Response returned to Hermes agent
              ▼
     Only visible to user (Gavin) via dashboard
```

**Key points:**

- The backend (FastAPI) is the only component that would make Drive API calls. It **never** sends raw document text to any AI model. The backend makes **zero LLM/API calls to Anthropic or any AI provider** — there is no ANTHROPIC_API_KEY or similar credential in the backend's configuration (`config.py` confirms this).
- **Hermes Agent** (a separate process on the same WSL VM) is the AI agent. When the user asks a question, Hermes may call the backend API (e.g., `GET /api/tasks`) to retrieve task summaries, then send a **formatted prompt** containing that structured data to Claude via Anthropic's API. The user's raw Drive document text is never forwarded.
- Outputs (strategy, delegation suggestions, status reports) are returned to the user only — either via Discord or the web dashboard.

---

## 3. What Is Stored vs. Discarded

### Persisted on disk (`~/wise-old-man-os/backend/data/`)

| Item | Location | Format | Content |
|------|----------|--------|---------|
| SQLite cache | `backend/data/wom.db` (`~350 KB`) | SQLite | Cached task rows, agent signals, console messages, approvals, usage logs |
| Task vault | `backend/data/vault/tasks/personal.md` and `work.md` | Markdown tables | Task descriptions, due dates, owners, status fields |
| Priority overlay | `backend/data/vault/overlay/priorities.json` | JSON | Task priority levels assigned by Hermes |

### Read-and-discard (not persisted)

- Google Drive file content or metadata (once processed into task data, the raw document text is discarded)
- Gmail inbox (scanned for actionable items, discarded after processing)
- Console API request/response bodies (processed live, not logged to disk)

### What is NOT stored

- Raw document text from Drive files
- Email body content
- Full web pages scraped via Firecrawl (written to `.firecrawl/` cache, not the persistent vault)
- User session tokens (Google OAuth token is stored for credential refresh only — see below)

### Credential storage

- Google OAuth token: `~/.hermes/google_token.json` (auto-refreshed, encrypted at rest by the host OS filesystem)
- `WOM_SERVICE_TOKEN`: in `~/.env` and the backend `.env` file (plaintext, WSL filesystem)
- `FIRECRAWL_API_KEY`: stored by the Firecrawl CLI credential store
- GitHub PAT: stored in `~/.git-credentials` (plaintext)
- No secrets are written to logs, git commits, or the SQLite database.

---

## 4. Retention

| Data | Retention | Auto-deletion |
|------|-----------|---------------|
| SQLite cache (`wom.db`) | Indefinite — the DB is never automatically pruned. Old rows accumulate. | None |
| Vault task files | Indefinite — committed to git with full history | None |
| Git vault history | Permanent — all commits preserved | None |
| `.firecrawl/` cache | Manual — no auto-cleanup | None |
| Console messages | Indefinite in SQLite | None |
| Hermes watcher log (`/tmp/wom-watcher.log`) | Lost on WSL reboot | Survives WSL restart, but `/tmp` may be cleaned by OS |
| Google OAuth token | Refreshed automatically; retained until revoked | OAuth revocation (via Google Admin) immediately invalidates the token |
| Agent signals / beliefs | Indefinite in SQLite | None |

**On a delete request:** Currently no mechanism to delete individual records. The entire `data/` directory can be removed (`rm -rf backend/data/`), which deletes the SQLite DB and vault files. Git history in the vault would retain past commits unless the repo is destroyed.

---

## 5. Encryption

| Layer | Status | Detail |
|-------|--------|--------|
| **In transit — user to Cloudflare** | ✅ TLS 1.3 | All traffic to `wise-old-man.xyz` is HTTPS, proxied through Cloudflare |
| **In transit — Cloudflare to backend** | 🔶 HTTP (localhost) | Cloudflare tunnel → `http://localhost:8787`. Traffic never leaves the local machine between cloudflared and the backend. On a single-host WSL VM, this is local loopback only. |
| **In transit — backend to Google API** | ✅ TLS | Google's Drive API is accessed via HTTPS (TLS). |
| **In transit — Hermes to Anthropic** | ✅ TLS | Anthropic API uses HTTPS (TLS 1.2+). |
| **At rest — SQLite DB** | ❌ **Not encrypted** | `wom.db` is stored as a plain SQLite file on disk. No encryption at rest. |
| **At rest — vault files** | ❌ **Not encrypted** | Task markdown files are stored as plaintext files. |
| **At rest — `.env` secrets** | ❌ **Not encrypted** | Plaintext on the WSL filesystem. |
| **At rest — host disk** | 🔶 WSL default | WSL uses the host Windows NTFS volume, which can be BitLocker-encrypted at the OS level. The VM itself has no separate disk encryption. |

---

## 6. Where It Runs & Who Can Access

| Property | Detail |
|----------|--------|
| **Host** | Windows Subsystem for Linux (WSL) on a Windows 11 desktop (`GavsComputer`) |
| **OS** | Ubuntu 24.04 (WSL) |
| **Backend process** | FastAPI/uvicorn managed by systemd (`wom.service`) — auto-starts on boot, auto-restarts on crash |
| **Cloudflare tunnel** | `cloudflared` — runs as a Windows service, connects to Cloudflare's edge |
| **Network** | Private home network — no open firewall ports. All external access is via Cloudflare Tunnel (outbound-only). |
| **Auth gate (human)** | Cloudflare Access → Google OAuth — only `gavin.watson.jr@gmail.com` is allowed (enforced by Access policy + backend `ALLOWED_EMAILS`) |
| **Auth gate (machine)** | Bearer token (`WOM_SERVICE_TOKEN`) — a shared secret between Hermes and the backend |
| **Users** | **Single user.** One email allowed. No multi-tenant design. |
| **Remote access** | Dashboard accessible from any browser at `wise-old-man.xyz` (behind Cloudflare Access + Google login) |
| **Reviewer visibility** | Zero. The VM is on a personal Windows desktop, not a corporate-managed environment. IT has no monitoring, no VPN, no remote access to the host. |

---

## 7. Third Parties

Every external service that touches user data:

| Service | Data sent | Terms note |
|---------|-----------|------------|
| **Anthropic** (Claude Sonnet 4) | Task summaries, priorities, and prompts composed by Hermes — **not raw document text**. Accessed via Claude Max (OAuth, paid subscription). | Anthropic's API terms: **Not used for training.** Enterprise-grade API: no training on API inputs/outputs per Anthropic's standard API policy (data not used for model training). |
| **OpenRouter** (DeepSeek) | Same class of data as Anthropic — used for cron jobs (cost-saving). | OpenRouter's terms: API data is not used for training. |
| **Cloudflare** | The hostname `wise-old-man.xyz`, HTTPS traffic metadata, Google login identity assertion. | Cloudflare is acting as CDN/tunnel/access provider — does not inspect request bodies. |
| **Google** (OAuth) | OAuth token exchange, authentication identity | Limited to the scopes granted (profile, email). |
| **GitHub** | Git repo data (vault files, code) | Standard GitHub terms. Repos are private. |
| **Firecrawl** | URLs and web page content that Hermes explicitly searches/scrapes | Standard API terms. Data is not used for training. |
| **Discord** | Cron job output messages delivered to private channels | Discord chat is the delivery channel for notifications. The server is private. |

---

## 8. Controls for IT

| Control | Detail |
|---------|--------|
| **OAuth client** | Google Cloud OAuth 2.0 Desktop client — can be restricted by admin to specific scopes and revoked at any time via Google Admin Console. |
| **Scope** | `drive.readonly` only — read access to authorized Drives. No write, no delete. |
| **User restriction** | Single Google account (`gavin.watson.jr@gmail.com`) hard-coded in `ALLOWED_EMAILS` config. |
| **Audit — Google** | Google Workspace Admin audit logs track all API calls made by the OAuth client: which file was accessed, by whom, and at what time. |
| **Audit — Backend** | Access log is written to systemd journal (`journalctl -u wom`). No structured audit trail is maintained. |
| **Audit — Cloudflare** | Cloudflare Access provides authentication event logs (login attempts, IP, user agent). |
| **Revocation** | IT can revoke the OAuth client in Google Admin Console at any time. This immediately invalidates the stored refresh token. Additionally, deleting `google_token.json` on the VM terminates access. |

---

## 9. Gaps to Fix Before the Review

| # | Finding | Recommended Fix | Effort |
|---|---------|-----------------|--------|
| 1 | **SQLite at rest not encrypted** — `wom.db` stores cached task data with no encryption. | Enable SQLite encryption extension (SEE) or use OS-level file encryption (eCryptfs, LUKS for the WSL mount). | Medium |
| 2 | **Vault files not encrypted** — task markdown in `data/vault/` is plaintext. | Store in an encrypted directory or encrypt individual files before git push. | Medium |
| 3 | **Indefinite retention** — SQLite DB and vault files are never auto-pruned. | Add a retention policy: auto-purge completed tasks after 90 days, archive console messages older than 30 days. | Low |
| 4 | **No structured audit trail** — backend logs to systemd journal only. No queryable access log. | Add structured logging to a separate audit table (who accessed what, when, from where). | Low |
| 5 | **Secrets in plaintext `.env`** — `WOM_SERVICE_TOKEN`, GitHub PAT, Google OAuth token stored as plaintext files on WSL. | Use a secrets manager (e.g., `pass`, Bitwarden CLI) or at minimum set `chmod 600` on `.env` files. | Low |
| 6 | **VM on personal desktop** — no corporate visibility or management. | [CONFIRM: Acceptable risk per IT or deploy to a managed VM.] | Policy decision |
| 7 | **Live Drive adapter is stubbed** — the actual Drive read code doesn't exist yet. The integration is proposed, not built. | Implement and test the Live adapter before the review. | Medium |

---

## 10. Summary

1. **No real Drive access currently exists** — the system runs entirely on mock data. The Drive read-only adapter is unimplemented (stubbed).
2. **The backend never sends document text to any AI model** — raw Drive file content is processed into structured task data locally; only task summaries reach Claude/DeepSeek via Hermes.
3. **Three main gaps to address before sign-off**: no encryption at rest, indefinite data retention, and secrets in plaintext files — all low-to-medium effort fixes.
