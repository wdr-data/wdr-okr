"""Read and process YouTube data."""

import datetime as dt
from time import sleep
from typing import Optional

from django.db.utils import IntegrityError
from django.db.models import Q
from loguru import logger
from sentry_sdk import capture_exception

from ...models.youtube import (
    YouTube,
    YouTubeAnalytics,
    YouTubeVideo,
)
from . import quintly
from ..common.utils import BERLIN, to_timedelta


def scrape_full(youtube: YouTube):
    """Initiate scraping for daily, weekly, and monthly YouTube data from Quintly.

    Args:
        youtube (YouTube): YouTube object to scrape data for.
    """
    logger.info("Starting full YouTube scrape of {}", youtube)

    youtube_filter = Q(id=youtube.id)
    start_date = dt.date(2019, 1, 1)

    sleep(1)

    scrape_channel_analytics(start_date=start_date, youtube_filter=youtube_filter)
    scrape_video_analytics(start_date=start_date, youtube_filter=youtube_filter)

    logger.success("Finished full YouTube scrape of {}", youtube)


def scrape_channel_analytics(
    *,
    start_date: Optional[dt.date] = None,
    youtube_filter: Optional[Q] = None,
):
    """Read YouTube channel analytics data from Quintly and store in database.

    Results are saved in
    :class:`~okr.models.youtube.YouTubeAnalytics`,
    :class:`~okr.models.youtube.YouTubeDemographics`,
    :class:`~okr.models.youtube.YouTubeTrafficSource`.

    Args:
        start_date (Optional[date], optional): Earliest data to request data for.
            Defaults to None.
        youtube_filter (Optional[Q], optional): Q object to filter data with.
            Defaults to None.
    """
    youtubes = YouTube.objects.all()

    if youtube_filter:
        youtubes = youtubes.filter(youtube_filter)

    for youtube in youtubes:
        logger.debug("Scraping YouTube channel analytics for {}", youtube)

        df = quintly.get_youtube_analytics(
            youtube.quintly_profile_id, start_date=start_date
        )

        logger.debug("Dataframe Größe {}", len(df))

        for index, row in df.iterrows():

            if row.importTime is None:
                logger.debug("importTime is None!")
                continue

            defaults = {
                "views": row.views,
                "likes": row.likes,
                "dislikes": row.dislikes,
                "subscribers": row.subscribersLifetime,
                "subscribers_gained": row.subscribersGained,
                "subscribers_lost": row.subscribersLost,
                "watch_time": to_timedelta(row.estimatedMinutesWatched * 60),
                "quintly_last_updated": BERLIN.localize(
                    dt.datetime.fromisoformat(row.importTime)
                ),
            }

            try:
                YouTubeAnalytics.objects.update_or_create(
                    youtube=youtube,
                    date=dt.date.fromisoformat(row.time),
                    defaults=defaults,
                )
            except IntegrityError as e:
                capture_exception(e)
                logger.exception(
                    "Data for channel analytics at {} failed integrity check:\n{}",
                    row.time,
                    defaults,
                )


def scrape_video_analytics(
    *,
    start_date: Optional[dt.date] = None,
    youtube_filter: Optional[Q] = None,
):
    """Read basic YouTube video data from Quintly and store in database.

    Results are saved in
    :class:`~okr.models.youtube.YouTubeVideo`.

    Args:
        start_date (Optional[date], optional): Earliest data to request data for.
            Defaults to None.
        youtube_filter (Optional[Q], optional): Q object to filter data with.
            Defaults to None.
    """
    youtubes = YouTube.objects.all()

    if youtube_filter:
        youtubes = youtubes.filter(youtube_filter)

    for youtube in youtubes:
        logger.debug("Scraping basic YouTube video data for {}", youtube)

        df = quintly.get_youtube_videos(
            youtube.quintly_profile_id, start_date=start_date
        )

        logger.debug("Dataframe Größe {}", len(df))

        for index, row in df.iterrows():

            if row.importTime is None:
                logger.debug("importTime is None!")
                continue

            if row.liveBroadcastContent == "upcoming":
                logger.debug("Video {} is a scheduled live video!", row.title)
                continue

            if row.liveActualStartTime:
                is_livestream = True
            else:
                is_livestream = False

            defaults = {
                "published_at": BERLIN.localize(
                    dt.datetime.fromisoformat(row.publishTime)
                ),
                "is_livestream": is_livestream,
                "title": row.title,
                "description": row.description,
                "duration": to_timedelta(row.duration),
                "quintly_last_updated": BERLIN.localize(
                    dt.datetime.fromisoformat(row.importTime)
                ),
            }

            try:
                YouTubeVideo.objects.update_or_create(
                    youtube=youtube,
                    external_id=row.externalId,
                    defaults=defaults,
                )
            except IntegrityError as e:
                capture_exception(e)
                logger.exception(
                    "Data for basic YouTube video data for {} failed integrity check:\n{}",
                    row.title,
                    defaults,
                )
