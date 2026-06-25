"""GooglePersonal adapter — Gmail / Calendar / Drive / Sheets (personal account)."""
from __future__ import annotations

from ..mock import mock_data as M


class MockGooglePersonal:
    """Serves canned Gmail/Calendar data. No network, no creds."""

    def inbox(self, scope: str) -> list[dict]:
        return M.scope_get(M.INBOX, scope)

    def today(self, scope: str) -> list[dict]:
        return M.scope_get(M.TODAY, scope)

    def create_calendar_event(self, payload: dict) -> dict:
        # MOCK: pretend we created it.
        return {"ok": True, "mock": True, "event": payload,
                "html_link": "https://calendar.google.com/mock-event"}

    def send_email(self, draft: dict) -> dict:
        # MOCK: never actually sends. HARD LIMIT honored.
        return {"ok": True, "mock": True, "sent_to": draft.get("to"),
                "subject": draft.get("subject"), "note": "Mock send — no email left the building."}


# --------------------------------------------------------------------------- #
# TODO(live): LiveGooglePersonal
#   - Build credentials from GOOGLE_CLIENT_ID/SECRET + token at GOOGLE_OAUTH_TOKEN_PATH
#     (google-auth-oauthlib). Refresh as needed.
#   - inbox(): users().messages().list(q="is:unread") + get() for snippets.
#   - today(): calendar events().list(timeMin=startOfDay, timeMax=endOfDay).
#   - create_calendar_event(): events().insert(...).
#   - send_email(): users().messages().send(...)  <-- gate behind explicit approval.
#   Implement the same 4 methods and select it in registry.py.
# --------------------------------------------------------------------------- #
