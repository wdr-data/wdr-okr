"""Read and process data for Twitter from Quintly."""

from datetime import date, datetime
from time import sleep
from typing import Optional

from django.db.utils import IntegrityError
from django.db.models import Q
from loguru import logger
from sentry_sdk import capture_exception

from ...models.twitter import (
    Twitter,
    TwitterInsight,
    Tweet,
)
from . import quintly
from ..common.quintly import parse_bool
from ..common.utils import BERLIN


def scrape_full(twitter: Twitter):
    """Initiate scraping for daily, weekly, and monthly Twitter data from Quintly.

    Args:
        twitter (Twitter): Twitter object to collect data for.
    """
    logger.info("Starting full Twitter scrape of {}", twitter)

    twitter_filter = Q(id=twitter.id)
    start_date = date(2019, 1, 1)

    sleep(1)

    scrape_insights(start_date=start_date, twitter_filter=twitter_filter)

    scrape_tweets(start_date=start_date, twitter_filter=twitter_filter)
    logger.success("Finished full Twitter scrape of {}", twitter)


def scrape_insights(
    *,
    start_date: Optional[date] = None,
    twitter_filter: Optional[Q] = None,
):
    """Retrieve Twitter insights data from Quintly.

    Results are saved in :class:`~okr.models.twitter.TwitterInsight`.

    Args:
        start_date (Optional[date], optional): Earliest date to request data for.
        Defaults to None.
        twitter_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.twitter.Twitter` object. Defaults to None.
    """
    twitters = Twitter.objects.all()

    if twitter_filter:
        twitters = twitters.filter(twitter_filter)

    for twitter in twitters:
        logger.debug("Scraping insights for {}", twitter)
        df = quintly.get_twitter_insights(
            twitter.quintly_profile_id, start_date=start_date
        )

        for index, row in df.iterrows():
            defaults = {
                "followers": row.followers or 0,
            }

            try:
                obj, created = TwitterInsight.objects.update_or_create(
                    twitter=twitter,
                    date=date.fromisoformat(row.time),
                    defaults=defaults,
                )
            except IntegrityError as e:
                capture_exception(e)
                logger.exception(
                    "Data for {} insights for date {} failed integrity check:\n{}",
                    row.time,
                    defaults,
                )


def scrape_tweets(
    *, start_date: Optional[date] = None, twitter_filter: Optional[Q] = None
):
    """Retrieve data for Twitter posts from Quintly.

    Results are saved in :class:`~okr.models.twitter.Tweet`.

    Args:
        start_date (Optional[date], optional): Earliest date to request data for.
        Defaults to None.
        twitter_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.twitter.Twitter` object. Defaults to None.
    """
    twitters = Twitter.objects.all()

    if twitter_filter:
        twitters = twitters.filter(twitter_filter)

    for twitter in twitters:
        logger.debug("Scraping post insights for {}", twitter)
        df = quintly.get_tweets(twitter.quintly_profile_id, start_date=start_date)

        for index, row in df.iterrows():
            defaults = {
                "created_at": BERLIN.localize(datetime.fromisoformat(row.time)),
                "tweet_type": row.type,
                "link": row.link,
                # False is just an empty string in this table
                "is_retweet": parse_bool(row.isRetweet, default=False),
                "message": row.message,
                "favs": row.favs or 0,
                "retweets": row.retweets or 0,
                "replies": row.replies or 0,
            }

            try:
                obj, created = Tweet.objects.update_or_create(
                    twitter=twitter,
                    external_id=row.externalId,
                    defaults=defaults,
                )
            except IntegrityError as e:
                capture_exception(e)
                logger.exception(
                    "Data for tweet with ID {} failed integrity check:\n{}",
                    row.externalId,
                    defaults,
                )
