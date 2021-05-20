""" SEO Bot for to dos """

import os
from typing import List

from loguru import logger
import tweepy

from .pytrends_patch import TrendReq
from .teams_message import _generate_adaptive_card
from ..teams_tools import generate_teams_payload, send_to_teams
from okr.scrapers.common.types import JSON

WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK_SEO_BOT")
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET")


def _get_google_trends() -> JSON:
    pytrends = TrendReq(hl="de-DE", tz="120", geo="DE")
    return pytrends.realtime_trending_searches()


def _get_twitter_trends(woid: str = "23424829") -> List[JSON]:
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
    api = tweepy.API(auth)
    result = api.trends_place(woid)[0]
    return result["trends"]


def run():
    google_trends_data = _get_google_trends()
    twitter_trends_data = _get_twitter_trends()

    adaptive_card = _generate_adaptive_card(google_trends_data, twitter_trends_data)
    payload = generate_teams_payload(adaptive_card)

    import json

    print(json.dumps(payload["attachments"][0]["content"]))

    # Send payload to MS Teams
    result = send_to_teams(payload, WEBHOOK_URL)
    logger.debug(result)
