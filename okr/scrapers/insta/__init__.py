"""Read and process data for Instagram from Quintly."""

from datetime import date, datetime
from time import sleep
from typing import Optional

from django.db.utils import IntegrityError
from django.db.models import Q
from loguru import logger
from sentry_sdk import capture_exception

from ...models.insta import (
    Insta,
    InstaInsight,
    InstaPost,
    InstaStory,
    InstaIGTV,
)
from . import quintly
from ..common.utils import BERLIN


def scrape_full(insta: Insta):
    """Initiate scraping for daily, weekly, and monthly Instagram data from Quintly.

    Args:
        insta (Insta): Instagram object to collect data for.
    """

    logger.info('Starting full scrape for Instagram account "{}"', insta.name)

    insta_filter = Q(id=insta.id)
    start_date = date(2019, 1, 1)

    sleep(1)

    scrape_insights(start_date=start_date, insta_filter=insta_filter)
    scrape_stories(start_date=start_date, insta_filter=insta_filter)
    scrape_posts(start_date=start_date, insta_filter=insta_filter)
    scrape_igtv(start_date=start_date, insta_filter=insta_filter)

    logger.success('Finished full scrape for Instagram account "{}"', insta.name)


def scrape_insights(
    *,
    start_date: Optional[date] = None,
    insta_filter: Optional[Q] = None,
):
    """Retrieve Instagram insights data from Quintly.

    Results are saved in :class:`~okr.models.insta.InstaInsight`.

    Args:
        interval (str): Interval to request data for.
        start_date (Optional[date], optional): Earliest date to request data for.
        Defaults to None.
        insta_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.insta.Insta` object. Defaults to None.
    """
    instas = Insta.objects.all()

    if insta_filter:
        instas = instas.filter(insta_filter)

    for insta in instas:
        df = quintly.get_insta_insights(insta.quintly_profile_id, start_date=start_date)

        for index, row in df.iterrows():
            defaults = {
                "quintly_last_updated": BERLIN.localize(
                    datetime.fromisoformat(row.importTime)
                ),
                "reach": row.reachDay,
                "reach_7_days": row.reachWeek,
                "reach_28_days": row.reachDays28,
                "impressions": row.impressionsDay,
                "followers": row.followers,
                "text_message_clicks_day": row.textMessageClicksDay,
                "email_contacts_day": row.emailContactsDay,
                "profile_views": row.profileViewsDay,
            }

            try:
                obj, created = InstaInsight.objects.update_or_create(
                    insta=insta,
                    date=date.fromisoformat(row.time),
                    defaults=defaults,
                )
            except IntegrityError as e:
                capture_exception(e)
                logger.exception(
                    "Data for insights on {} failed integrity check:\n{}",
                    row.time,
                    defaults,
                )


def scrape_stories(
    *, start_date: Optional[date] = None, insta_filter: Optional[Q] = None
):
    """Retrieve data for Instagram stories from Quintly.

    Results are saved in :class:`~okr.models.insta.InstaStory`.

    Args:
        start_date (Optional[date], optional): Earliest date to request data for.
        Defaults to None.
        insta_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.insta.Insta` object. Defaults to None.
    """
    instas = Insta.objects.all()

    if insta_filter:
        instas = instas.filter(insta_filter)

    for insta in instas:
        df = quintly.get_insta_stories(insta.quintly_profile_id, start_date=start_date)

        for index, row in df.iterrows():
            defaults = {
                "created_at": BERLIN.localize(datetime.fromisoformat(row.time)),
                "quintly_last_updated": BERLIN.localize(
                    datetime.fromisoformat(row.importTime)
                ),
                "caption": row.caption,
                "reach": row.reach,
                "impressions": row.impressions,
                "replies": row.replies,
                "taps_forward": row.tapsForward,
                "taps_back": row.tapsBack,
                "story_type": row.type,
                "link": row.link,
                "exits": row.exits,
            }

            try:
                obj, created = InstaStory.objects.update_or_create(
                    insta=insta, external_id=row.externalId, defaults=defaults
                )
            except IntegrityError as e:
                capture_exception(e)
                logger.exception(
                    "Data for story with ID {} failed integrity check:\n{}",
                    row.externalId,
                    defaults,
                )


def scrape_posts(
    *, start_date: Optional[date] = None, insta_filter: Optional[Q] = None
):
    """Retrieve data for Instagram posts from Quintly.

    Results are saved in :class:`~okr.models.insta.InstaPost`.

    Args:
        start_date (Optional[date], optional): Earliest date to request data for.
        Defaults to None.
        insta_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.insta.Insta` object. Defaults to None.
    """
    instas = Insta.objects.all()

    if insta_filter:
        instas = instas.filter(insta_filter)

    for insta in instas:
        df = quintly.get_insta_posts(insta.quintly_profile_id, start_date=start_date)

        for index, row in df.iterrows():
            defaults = {
                "created_at": BERLIN.localize(datetime.fromisoformat(row.time)),
                "quintly_last_updated": BERLIN.localize(
                    datetime.fromisoformat(row.importTime)
                ),
                "message": row.message or "",
                "comments": row.comments,
                "reach": row.reach,
                "impressions": row.impressions,
                "likes": row.likes,
                "saved": row.saved,
                "video_views": row.videoViews,
                "post_type": row.type,
                "link": row.link,
            }

            try:
                obj, created = InstaPost.objects.update_or_create(
                    insta=insta, external_id=row.externalId, defaults=defaults
                )
            except IntegrityError as e:
                capture_exception(e)
                logger.exception(
                    "Data for post with ID {} failed integrity check:\n{}",
                    row.externalId,
                    defaults,
                )


def scrape_igtv(*, start_date: Optional[date] = None, insta_filter: Optional[Q] = None):
    """Retrieve data for Instagram IGTV videos from Quintly.

    Results are saved in :class:`~okr.models.insta.InstaIGTV`.

    Args:
        start_date (Optional[date], optional): Earliest date to request data for.
        Defaults to None.
        insta_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.insta.Insta` object. Defaults to None.
    """
    instas = Insta.objects.all()

    if insta_filter:
        instas = instas.filter(insta_filter)

    for insta in instas:

        logger.debug(f"Scraping IGTV for {insta.name}")

        df = quintly.get_insta_igtv(insta.quintly_profile_id, start_date=start_date)

        for index, row in df.iterrows():
            defaults = {
                "created_at": BERLIN.localize(datetime.fromisoformat(row.time)),
                "quintly_last_updated": BERLIN.localize(
                    datetime.fromisoformat(row.importTime)
                ),
                "message": row.message or "",
                "video_title": row.videoTitle,
                "likes": row.likes,
                "comments": row.comments,
                "reach": row.reach,
                "impressions": row.impressions,
                "saved": row.saved,
                "video_views": row.videoViews,
                "link": row.link,
            }

            try:
                obj, created = InstaIGTV.objects.update_or_create(
                    insta=insta, external_id=row.externalId, defaults=defaults
                )
            except IntegrityError as e:
                capture_exception(e)
                logger.exception(
                    "Data for post with ID {} failed integrity check:\n{}",
                    row.externalId,
                    defaults,
                )
