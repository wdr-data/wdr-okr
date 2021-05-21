""" SEO Bot for SEO-Checkup """

import os
from typing import List, Generator

from loguru import logger
import tweepy

from .trend_filters import trend_filters_dict
from .pytrends_patch import TrendReq
from .teams_message import generate_adaptive_card
from ..teams_tools import generate_teams_payload, send_to_teams
from okr.scrapers.common.types import JSON
from okr.scrapers.common.utils import local_now

WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK_SEO_BOT")
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET")


def _check_trend_filters(words) -> bool:

    # Read and combine filter entries
    trend_filters = []
    for filter_list in trend_filters_dict:
        trend_filters.extend(trend_filters_dict[filter_list])
    trend_filters = set(trend_filters)

    # Filter
    for filter_word in trend_filters:
        for entry in words:
            if filter_word.lower() in entry.lower():
                logger.debug('"{}" found in "{}" ({})', filter_word, entry, words)
                return True

    logger.debug("Skipping after no match in: {}", words)
    return False


def _filter_trends(trending_searches: JSON) -> Generator[JSON, None, None]:
    # check every item with _check_trend_filters, yield only if they pass the filter
    for item in trending_searches:
        words = []
        # read title
        words.append(item["detail"]["title"])
        # read entity names
        words.extend(item["detail"]["entityNames"])
        # read article headlines
        articles = next(
            w for w in item["detail"]["widgets"] if w["id"] == "NEWS_ARTICLE"
        )
        words.extend([article["title"] for article in articles["articles"]])
        # read related queries
        related_queries = next(
            w for w in item["detail"]["widgets"] if w["id"] == "RELATED_QUERIES"
        )
        words.extend(related_queries["request"].get("term", []))

        if _check_trend_filters(words):
            yield item


def _get_google_trends() -> Generator[JSON, None, None]:
    utc_offset = local_now().utcoffset()

    pytrends = TrendReq(hl="de-DE", tz=str(-int(utc_offset.seconds / 60)), geo="DE")
    trending_searches = pytrends.realtime_trending_searches()

    for item in trending_searches:
        item["detail"] = pytrends.story_by_id(item["id"])

    yield from _filter_trends(trending_searches)


def _get_twitter_trends(woid: str = "23424829") -> List[JSON]:
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
    api = tweepy.API(auth)
    result = api.trends_place(woid)[0]
    return result["trends"]


def run():
    google_trends_data = _get_google_trends()
    twitter_trends_data = _get_twitter_trends()

    adaptive_card = generate_adaptive_card(google_trends_data, twitter_trends_data)
    payload = generate_teams_payload(adaptive_card)

    # Send payload to MS Teams
    result = send_to_teams(payload, WEBHOOK_URL)
    logger.debug(result)
