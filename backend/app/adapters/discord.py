"""Discord adapter — notify + console relay. Stubbed (no token)."""
from __future__ import annotations


class MockDiscord:
    def post(self, channel: str, message: str) -> dict:
        # MOCK: never hits Discord. HARD LIMIT honored.
        return {"ok": True, "mock": True, "channel": channel,
                "message": message, "note": "Mock post — nothing sent to Discord."}


# --------------------------------------------------------------------------- #
# TODO(live): LiveDiscord
#   - DISCORD_BOT_TOKEN + DISCORD_DEFAULT_CHANNEL_ID; discord.py or REST webhook.
#   - post(): send to channel. Same shape.
# --------------------------------------------------------------------------- #
