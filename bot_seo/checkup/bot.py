""" SEO Bot for to dos """

import os

from loguru import logger

from .pytrends_patch import TrendReq
from .teams_message import _generate_adaptive_card
from ..teams_tools import generate_teams_payload, send_to_teams
from okr.scrapers.common.types import JSON

WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK_SEO_BOT")


def _get_google_trends() -> JSON:
    pytrends = TrendReq(hl="de-DE", tz="120", geo="DE")
    return pytrends.realtime_trending_searches()


def run():
    google_trends_data = _get_google_trends()

    adaptive_card = _generate_adaptive_card(google_trends_data)
    payload = generate_teams_payload(adaptive_card)

    # Send payload to MS Teams
    result = send_to_teams(payload, WEBHOOK_URL)
    logger.debug(result)
