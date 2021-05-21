""" SEO Bot for SEO-Checkup """

import html
import os
import re
from typing import List, Generator

from loguru import logger
import tweepy

from .trend_filters import trend_filters, trend_ignore_filters_dict
from .pytrends_patch import TrendReq
from .teams_message import generate_adaptive_card
from ..teams_tools import generate_teams_payload, send_to_teams
from okr.scrapers.common.types import JSON
from okr.scrapers.common.utils import chunk_list, local_now

WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK_SEO_BOT")
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET")


def _tokenizer(words: list) -> str:
    """Basic tokenizer and normalizer.

    Args:
        words (list): List of words

    Returns:
        str: tokenized and normalized string of words
    """
    words = " ".join(words)
    words = html.unescape(words)

    # Normalize dashes
    dashes = r"[–-—‑−]"
    words = re.sub(dashes, "-", words)

    # Remove non-word characters
    non_words = r"([^\s\w-]|\d)"
    words = re.sub(non_words, "", words)

    # Normalize whitespace
    words = re.sub(r"\s", " ", words)
    words = re.sub(r"\s\s+", " ", words)

    return words.strip().lower()


def _filter_trend(item: JSON) -> bool:
    words = []

    # Read title
    words.append(item["detail"]["title"])

    # Read entity names
    words.extend(item["detail"]["entityNames"])

    # Read article headlines
    articles = next(w for w in item["detail"]["widgets"] if w["id"] == "NEWS_ARTICLE")
    words.extend([article["title"] for article in articles["articles"]])

    # Read related queries
    related_queries = next(
        w for w in item["detail"]["widgets"] if w["id"] == "RELATED_QUERIES"
    )
    words.extend(related_queries["request"].get("term", []))

    # Prepare list of unwanted words/phrases
    trend_ignore_filters = []

    for filter_list in trend_ignore_filters_dict:
        trend_ignore_filters.extend(trend_ignore_filters_dict[filter_list])

    trend_ignore_filters = set(trend_ignore_filters)

    # Remove unwanted words/phrases
    for ignore_filter in trend_ignore_filters:
        for word in words:
            if ignore_filter.lower() in word.lower():
                logger.debug(
                    'Removing "{}" because it is part of trend_ignore_filters',
                    word,
                )
                words.remove(word)

    # Tokenize all words into one string
    words_tokenized = _tokenizer(words)

    # Search for filter matches in words
    result = trend_filters.findall(words_tokenized)

    if result:
        logger.debug("Found {} in {}", result, words)
        return True

    logger.trace("Skipping after no match in: {}", words)
    return False


def _load_trends(pytrends: TrendReq, initial: JSON) -> Generator[JSON, None, None]:
    # First yield included trending stories
    yield from initial["storySummaries"]["trendingStories"]

    ignore_first_n = len(initial["storySummaries"]["trendingStories"])

    # After that, look up more as needed
    for ids in chunk_list(initial["trendingStoryIds"][ignore_first_n:], 15):
        logger.info("Loading additional summaries...")
        yield from pytrends.summary(ids)["trendingStories"]


def _get_google_trends() -> Generator[JSON, None, None]:
    utc_offset = local_now().utcoffset()

    pytrends = TrendReq(hl="de-DE", tz=str(-int(utc_offset.seconds / 60)), geo="DE")
    initial = pytrends.realtime_trending_searches()

    for item in _load_trends(pytrends, initial):
        item["detail"] = pytrends.story_by_id(item["id"])

        if _filter_trend(item):
            yield item


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
