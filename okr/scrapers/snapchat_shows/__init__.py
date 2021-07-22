"""Read and process data for SnapchatShow from Quintly."""

from datetime import date, datetime
from time import sleep
from typing import Optional

from django.db.utils import IntegrityError
from django.db.models import Q
from loguru import logger
from sentry_sdk import capture_exception

from ...models.snapchat_shows import (
    SnapchatShow,
    SnapchatShowInsight,
    SnapchatShowStory,
)
from . import quintly
from ..common.utils import BERLIN


def scrape_full(snapchat_show: SnapchatShow):
    """Initiate scraping for SnapchatShow data from Quintly.

    Args:
        snapchat_show (SnapchatShow): SnapchatShow object to collect data for.
    """
    logger.info("Starting full SnapchatShow scrape of {}", snapchat_show)

    snapchat_show_filter = Q(id=snapchat_show.id)
    start_date = date(2019, 1, 1)

    sleep(1)

    scrape_insights(start_date=start_date, snapchat_show_filter=snapchat_show_filter)

    scrape_stories(start_date=start_date, snapchat_show_filter=snapchat_show_filter)
    logger.success("Finished full SnapchatShow scrape of {}", snapchat_show)


def scrape_insights(
    *,
    start_date: Optional[date] = None,
    snapchat_show_filter: Optional[Q] = None,
):
    """Retrieve SnapchatShow insights data from Quintly.

    Results are saved in :class:`~okr.models.snapchat_shows.SnapchatShowInsight`.

    Args:
        interval (str): Interval to request data for.
        start_date (Optional[date], optional): Earliest date to request data for.
        Defaults to None.
        snapchat_show_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.snapchat_shows.SnapchatShow` object. Defaults to None.
    """
    snapchat_shows = SnapchatShow.objects.all()

    if snapchat_show_filter:
        snapchat_shows = snapchat_shows.filter(snapchat_show_filter)

    for snapchat_show in snapchat_shows:
        logger.debug("Scraping insights for {}", snapchat_show)
        df = quintly.get_snapchatshow_insights(
            snapchat_show.quintly_profile_id, start_date=start_date
        )

        for index, row in df.iterrows():
            defaults = {
                "fans": row.page_fans or 0,
                "follows": row.page_follows or 0,
                "impressions_unique": row.page_impressions_unique or 0,
            }

            try:
                obj, created = SnapchatShowInsight.objects.update_or_create(
                    snapchat_show=snapchat_show,
                    date=date.fromisoformat(row.time),
                    defaults=defaults,
                )
            except IntegrityError as e:
                capture_exception(e)
                logger.exception(
                    "Data for insights on date {} failed integrity check:\n{}",
                    row.time,
                    defaults,
                )


def scrape_stories(
    *, start_date: Optional[date] = None, snapchat_show_filter: Optional[Q] = None
):
    """Retrieve data for SnapchatShow posts from Quintly.

    Results are saved in :class:`~okr.models.snapchat_shows.SnapchatShowPost`.

    Args:
        start_date (Optional[date], optional): Earliest date to request data for.
        Defaults to None.
        snapchatshow_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.snapchat_shows.SnapchatShow` object. Defaults to None.
    """
    snapchat_shows = SnapchatShow.objects.all()

    if snapchat_show_filter:
        snapchat_shows = snapchat_shows.filter(snapchat_show_filter)

    for snapchat_show in snapchat_shows:
        logger.debug("Scraping story insights for {}", snapchat_show)
        df = quintly.get_snapchatshow_stories(
            snapchat_show.quintly_profile_id, start_date=start_date
        )

        for index, row in df.iterrows():
            defaults = {
                "created_at": BERLIN.localize(datetime.fromisoformat(row.time)),
            }

            try:
                obj, created = SnapchatShowStory.objects.update_or_create(
                    snapchat_show=snapchat_show,
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
