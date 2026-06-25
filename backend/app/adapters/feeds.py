"""Feeds adapter — OSRS Hiscores + Wiki prices, World Cup, DC events, news."""
from __future__ import annotations

from ..mock import mock_data as M


class MockFeeds:
    def all_feeds(self) -> dict:
        return M.FEEDS


# --------------------------------------------------------------------------- #
# TODO(live): LiveFeeds
#   - OSRS Hiscores: GET secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player=NAME
#     (public, no key) -> parse the CSV-ish body into the highlights shape.
#   - OSRS prices: GET prices.runescape.wiki/api/v1/osrs/latest (public).
#   - News: NEWS_API_KEY provider of choice.
#   - World Cup / DC events: pick a source (or keep curated). Same all_feeds() shape.
# --------------------------------------------------------------------------- #
