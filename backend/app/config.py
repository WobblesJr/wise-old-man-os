"""Central config. Reads .env if present; otherwise falls back to mock-safe defaults.

Nothing here requires a secret to boot — every credential has a __STUB__ default
so the app runs on mock data out of the box.
"""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    # Load repo-root .env then backend/.env (backend wins if both set a key).
    _ROOT = Path(__file__).resolve().parents[2]
    load_dotenv(_ROOT / ".env")
    load_dotenv(_ROOT / "backend" / ".env")
except Exception:  # dotenv optional; defaults still apply
    pass


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


class Settings:
    # --- runtime ---
    DATA_MODE: str = _env("WOM_DATA_MODE", "mock").lower()  # mock | live
    TASK_STORE: str = _env("WOM_TASK_STORE", "vault").lower()  # vault (durable, git) | mock
    ENV: str = _env("WOM_ENV", "dev")
    HOST: str = _env("WOM_HOST", "127.0.0.1")
    PORT: int = int(_env("WOM_PORT", "8787"))

    BACKEND_DIR: Path = Path(__file__).resolve().parents[1]
    REPO_ROOT: Path = Path(__file__).resolve().parents[2]
    DB_PATH: Path = Path(_env("WOM_DB_PATH", str(BACKEND_DIR / "data" / "wom.db")))

    CORS_ORIGINS: list[str] = [
        o.strip()
        for o in _env(
            "WOM_CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8787",
        ).split(",")
        if o.strip()
    ]

    # --- google personal (stubbed) ---
    GOOGLE_CLIENT_ID: str = _env("GOOGLE_CLIENT_ID", "__STUB_GOOGLE_CLIENT_ID__")
    GSUITE_DASHBOARD_SHEET_ID: str = _env("GSUITE_DASHBOARD_SHEET_ID", "__STUB_SHEET_ID__")
    GSUITE_DASHBOARD_TAB: str = _env("GSUITE_DASHBOARD_TAB", "Tasks")

    # --- work (blocked) ---
    LIMBACH_DRIVE_ROOT: str = _env("LIMBACH_DRIVE_ROOT", "__STUB_BLOCKED_PENDING_IT__")

    # --- infra ---
    CLOUDFLARE_TUNNEL_HOSTNAME: str = _env("CLOUDFLARE_TUNNEL_HOSTNAME", "__STUB_TUNNEL_HOSTNAME__")

    @property
    def is_mock(self) -> bool:
        return self.DATA_MODE != "live"

    def credential_status(self) -> dict[str, bool]:
        """True = a real (non-stub) value is present. Drives the cockpit 'connections' panel."""
        def real(v: str) -> bool:
            return bool(v) and not v.startswith("__STUB")
        return {
            "google_personal": real(self.GOOGLE_CLIENT_ID),
            "gsuite_sheet": real(self.GSUITE_DASHBOARD_SHEET_ID),
            "limbach_work": real(self.LIMBACH_DRIVE_ROOT),
            "cloudflare_tunnel": real(self.CLOUDFLARE_TUNNEL_HOSTNAME),
        }


settings = Settings()
