#!/usr/bin/env python3
"""Generate the random secrets go-live needs (Milestone 1). No accounts/keys required.

Run:  python tools/gen_secrets.py
Copy the printed values. The SERVICE TOKEN must be pasted IDENTICALLY in two places:
the backend .env (WOM_SERVICE_TOKEN) AND Hermes in the VM. The session secret is only
needed if you choose app-level login instead of Cloudflare Access.
"""
import secrets

print("# --- paste into backend .env ---")
print(f"WOM_SERVICE_TOKEN={secrets.token_urlsafe(40)}   # also give this SAME value to Hermes")
print(f"SESSION_SECRET={secrets.token_urlsafe(48)}      # only if app-level login (skip with Cloudflare Access)")
print()
print("Keep these private. Re-running generates new ones (which would log everyone out / "
      "disconnect Hermes), so generate once.")
