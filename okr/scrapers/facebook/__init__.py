"""Read and process data for Facebook from Quintly."""

from datetime import date, datetime
from time import sleep
from typing import Optional

from django.db.utils import IntegrityError
from django.db.models import Q
from loguru import logger
from sentry_sdk import capture_exception

from ...models.facebook import (
    Facebook,
    FacebookInsight,
    FacebookPost,
)
from . import quintly
from ..common.quintly import parse_bool
from ..common.utils import BERLIN


def scrape_full(facebook: Facebook):
    """Initiate scraping for daily, weekly, and monthly Facebook data from Quintly.

    Args:
        facebook (Facebook): Facebook object to collect data for.
    """
    logger.info("Starting full Facebook scrape of {}", facebook)

    facebook_filter = Q(id=facebook.id)
    start_date = date(2019, 1, 1)

    sleep(1)

    scrape_insights(start_date=start_date, facebook_filter=facebook_filter)

    scrape_posts(start_date=start_date, facebook_filter=facebook_filter)
    logger.success("Finished full Facebook scrape of {}", facebook)


def scrape_insights(
    *,
    start_date: Optional[date] = None,
    facebook_filter: Optional[Q] = None,
):
    """Retrieve Facebook insights data from Quintly.

    Results are saved in :class:`~okr.models.facebook.FacebookInsight`.

    Args:
        start_date (Optional[date], optional): Earliest date to request data for.
            Defaults to None.
        facebook_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.facebook.Facebook` object. Defaults to None.
    """
    facebooks = Facebook.objects.all()

    if facebook_filter:
        facebooks = facebooks.filter(facebook_filter)

    for facebook in facebooks:
        logger.debug("Scraping insights for {}", facebook)
        df = quintly.get_facebook_insights(
            facebook.quintly_profile_id,
            start_date=start_date,
        )

        for index, row in df.iterrows():
            defaults = {
                "fans": row.page_fans or 0,
                "follows": row.page_follows or 0,
                "impressions_unique": row.page_impressions_unique or 0,
                "impressions_unique_7_days": row.page_impressions_unique_week or 0,
                "impressions_unique_28_days": row.page_impressions_unique_28_days or 0,
                "fans_online_per_day": row.page_fans_online_per_day or 0,
            }

            try:
                obj, created = FacebookInsight.objects.update_or_create(
                    facebook=facebook,
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


def scrape_posts(
    *, start_date: Optional[date] = None, facebook_filter: Optional[Q] = None
):
    """Retrieve data for Facebook posts from Quintly.

    Results are saved in :class:`~okr.models.facebook.FacebookPost`.

    Args:
        start_date (Optional[date], optional): Earliest date to request data for.
            Defaults to None.
        facebook_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.facebook.Facebook` object. Defaults to None.
    """
    facebooks = Facebook.objects.all()

    if facebook_filter:
        facebooks = facebooks.filter(facebook_filter)

    for facebook in facebooks:
        logger.debug("Scraping post insights for {}", facebook)
        df = quintly.get_facebook_posts(
            facebook.quintly_profile_id, start_date=start_date
        )

        for index, row in df.iterrows():
            defaults = {
                "created_at": BERLIN.localize(datetime.fromisoformat(row.time)),
                "post_type": row.type,
                "link": row.link,
                "message": row.message,
                "likes": row.likes or 0,
                "love": row.love or 0,
                "wow": row.wow or 0,
                "haha": row.haha or 0,
                "sad": row.sad or 0,
                "angry": row.angry or 0,
                "comments": row.comments or 0,
                "shares": row.shares or 0,
                "impressions_unique": row.post_impressions_unique or 0,
                "is_published": parse_bool(row.is_published),
                "is_hidden": parse_bool(row.is_hidden),
            }

            try:
                obj, created = FacebookPost.objects.update_or_create(
                    facebook=facebook,
                    external_id=row.externalId,
                    defaults=defaults,
                )
            except IntegrityError as e:
                capture_exception(e)
                logger.exception(
                    "Data for post with ID {} failed integrity check:\n{}",
                    row.externalId,
                    defaults,
                )
