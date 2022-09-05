"""Read and process YouTube data."""

import datetime as dt
from time import sleep
from typing import Dict, Mapping, Optional
import json
from collections import defaultdict

from django.db.utils import IntegrityError
from django.db.models import Q
from loguru import logger
from sentry_sdk import capture_exception
import pandas as pd

from ...models.youtube import (
    YouTube,
    YouTubeAnalytics,
    YouTubeDemographics,
    YouTubeTrafficSource,
    YouTubeVideo,
    YouTubeVideoAnalytics,
    YouTubeVideoDemographics,
    YouTubeVideoTrafficSource,
    YouTubeVideoExternalTraffic,
    YouTubeVideoSearchTerm,
)
from . import quintly, google
from ..common.utils import BERLIN, local_today, to_timedelta


def scrape_full(youtube: YouTube):
    """Initiate scraping for YouTube data from Quintly.

    Args:
        youtube (YouTube): YouTube object to scrape data for.
    """
    logger.info("Starting full YouTube scrape of {}", youtube)

    youtube_filter = Q(id=youtube.id)

    start_date = dt.date(2019, 1, 1)

    sleep(1)

    scrape_channel_analytics(start_date=start_date, youtube_filter=youtube_filter)
    scrape_videos(start_date=start_date, youtube_filter=youtube_filter)
    scrape_video_analytics(start_date=start_date, youtube_filter=youtube_filter)
    scrape_video_traffic_sources(start_date=start_date, youtube_filter=youtube_filter)
    scrape_video_external_traffic(start_date=start_date, youtube_filter=youtube_filter)
    scrape_video_search_terms(start_date=start_date, youtube_filter=youtube_filter)
    scrape_video_demographics(start_date=start_date, youtube_filter=youtube_filter)

    logger.success("Finished full YouTube scrape of {}", youtube)


def _scrape_youtube_demographics(
    youtube: YouTube,
    row: pd.Series,
):
    """Scrape YouTube demographics data from Quintly.

    Args:
        json_str (str): JSON string to scrape data from.
    """
    demographics_data = json.loads(row.viewsPercentageByAgeAndGender)

    for demo in demographics_data:
        defaults = {
            "views_percentage": demo["value"],
            "quintly_last_updated": BERLIN.localize(
                dt.datetime.fromisoformat(row.importTime)
            ),
        }

        gender = YouTubeDemographics.Gender(demo["gender"])
        age_range = YouTubeDemographics.AgeRange(
            demo["ageGroupName"].replace(" years", "")
        )

        try:
            YouTubeDemographics.objects.update_or_create(
                youtube=youtube,
                date=dt.date.fromisoformat(row.time),
                gender=gender,
                age_range=age_range,
                defaults=defaults,
            )
        except IntegrityError as e:
            capture_exception(e)
            logger.exception(
                "Data for channel demographics at {} failed integrity check:\n{}",
                row.time,
                row,
            )


def _scrape_youtube_traffic_source(
    youtube: YouTube,
    row: pd.Series,
):
    """Scrape YouTube traffic source data from Quintly.

    Args:
        json_str (str): JSON string to scrape data from.
    """
    json_data_views = json.loads(row.viewsByTrafficSource)
    json_data_minutes_watched = json.loads(row.estimatedMinutesWatchedByTrafficSource)

    json_data = defaultdict(lambda: [None, None])

    for data in json_data_views:
        source_type = YouTubeTrafficSource.SourceType[data["trafficSource"]]
        json_data[source_type][0] = data["value"]

    for data in json_data_minutes_watched:
        source_type = YouTubeTrafficSource.SourceType[data["trafficSource"]]
        json_data[source_type][1] = data["value"]

    for source_type, (views, minutes_watched) in json_data.items():
        defaults = {
            "views": views,
            "watch_time": to_timedelta(minutes_watched * 60)
            if minutes_watched is not None
            else None,
            "quintly_last_updated": BERLIN.localize(
                dt.datetime.fromisoformat(row.importTime)
            ),
        }

        try:
            YouTubeTrafficSource.objects.update_or_create(
                youtube=youtube,
                date=dt.date.fromisoformat(row.time),
                source_type=source_type,
                defaults=defaults,
            )
        except IntegrityError as e:
            capture_exception(e)
            logger.exception(
                "Data for channel traffic source at {} failed integrity check:\n{}",
                row.time,
                row,
            )


def scrape_channel_analytics(  # noqa: C901
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
        try:
            _scrape_channel_analytics_youtube(start_date, youtube)
        except Exception as e:
            capture_exception(e)


def _scrape_channel_analytics_youtube(start_date, youtube):
    logger.info("Scraping Quintly YouTube channel analytics for {}", youtube)

    df = quintly.get_youtube_analytics(
        youtube.quintly_profile_id, start_date=start_date
    )

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

        try:
            _scrape_youtube_demographics(youtube, row)
        except Exception as e:
            capture_exception(e)
            logger.exception(
                "Failed to scrape YouTube demographics data for {} at {}",
                youtube,
                row.time,
            )

        try:
            _scrape_youtube_traffic_source(youtube, row)
        except Exception as e:
            capture_exception(e)
            logger.exception(
                "Failed to scrape YouTube traffic source data for {} at {}",
                youtube,
                row.time,
            )


def scrape_videos(
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
        try:
            _scrape_videos_youtube(start_date, youtube)
        except Exception as e:
            capture_exception(e)


def _scrape_videos_youtube(start_date, youtube):
    logger.info("Scraping basic YouTube video data for {}", youtube)

    df = quintly.get_youtube_videos(youtube.quintly_profile_id, start_date=start_date)

    for index, row in df.iterrows():
        if row.importTime is None:
            logger.debug("importTime is None!")
            continue

            # Ignore scheduled/unpublished videos
        if row.liveBroadcastContent == "upcoming":
            logger.debug(
                "Video {} ({}) is a scheduled live video!",
                row.title,
                row.externalId,
            )
            continue

            # Check whether video was initially a live stream (or currently is a live
            # stream). is_livestream will be False for all videos that were on-demand
            # videos from the beginning - will be True for Videos that are/were live
            # streams
        if row.liveActualStartTime:
            is_livestream = True
        else:
            is_livestream = False

        defaults = {
            "published_at": BERLIN.localize(dt.datetime.fromisoformat(row.publishTime)),
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


def _get_youtube_video(video_id: str, video_cache: Mapping[str, YouTubeVideo]):
    """Get YouTube video object from cache or database."""
    try:
        youtube_video = video_cache[video_id]
    except KeyError:
        youtube_video = YouTubeVideo.objects.filter(
            external_id=video_id,
        ).first()

        if youtube_video is None:
            logger.warning("Video {} not found in database", video_id)

        video_cache[video_id] = youtube_video

    return youtube_video


def scrape_video_analytics(
    *,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
    youtube_filter: Optional[Q] = None,
):
    """Read YouTube video analytics data from BigQuery and store in database.

    Results are saved in
    :class:`~okr.models.youtube.YouTubeVideoAnalytics`.

    Args:
        start_date (Optional[date], optional): Earliest data to request data for.
            Defaults to None.
        end_date (Optional[date], optional): Latest data to request data for.
            Defaults to None.
        youtube_filter (Optional[Q], optional): Q object to filter data with.
            Defaults to None.
    """
    youtubes = YouTube.objects.all()

    if youtube_filter:
        youtubes = youtubes.filter(youtube_filter)

    for youtube in youtubes:
        try:
            _scrape_video_analytics_youtube(start_date, end_date, youtube)
        except Exception as e:
            capture_exception(e)


def _scrape_video_analytics_youtube(start_date, end_date, youtube):
    logger.info("Scraping YouTube video analytics for {}", youtube)

    # Cache videos to prevent multiple queries for the same video
    video_cache: Dict[str, YouTubeVideo] = {}

    rows_iter = google.get_bigquery_basic(
        youtube.bigquery_suffix,
        start_date=start_date,
        end_date=end_date,
    )

    for row in rows_iter:
        defaults = {
            "views": row.views,
            "likes": row.likes,
            "dislikes": row.dislikes,
            "comments": row.comments,
            "shares": row.shares,
            "subscribers_gained": row.subscribers_gained,
            "subscribers_lost": row.subscribers_lost,
            "watch_time": to_timedelta(row.watch_time_minutes * 60),
        }

        # Find video in cache or query database
        youtube_video = _get_youtube_video(row.video_id, video_cache)

        if youtube_video is None:
            continue

        try:
            YouTubeVideoAnalytics.objects.update_or_create(
                youtube_video=youtube_video,
                date=row.date,
                live_or_on_demand=row.live_or_on_demand,
                defaults=defaults,
            )
        except IntegrityError as e:
            capture_exception(e)
            logger.exception(
                "Data for video analytics at {} failed integrity check:\n{}",
                row.time,
                defaults,
            )


def scrape_video_traffic_sources(
    *,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
    youtube_filter: Optional[Q] = None,
):
    """Read YouTube video traffic source data from BigQuery and store in database.

    Results are saved in
    :class:`~okr.models.youtube.YouTubeVideoTrafficSource`.

    Args:
        start_date (Optional[date], optional): Earliest data to request data for.
            This date refers to the partition field value, not the date of the
            data itself. Defaults to None. If None, the start date will be
            set to 6 months in the past.
        end_date (Optional[date], optional): Latest data to request data for.
            Defaults to None.
        youtube_filter (Optional[Q], optional): Q object to filter data with.
            Defaults to None.
    """
    youtubes = YouTube.objects.all()

    if youtube_filter:
        youtubes = youtubes.filter(youtube_filter)

    if start_date is None:
        start_date = local_today() - dt.timedelta(days=31 * 6)

    for youtube in youtubes:
        try:
            _scrape_video_traffic_sources_youtube(start_date, end_date, youtube)
        except Exception as e:
            capture_exception(e)


def _scrape_video_traffic_sources_youtube(start_date, end_date, youtube):
    logger.info("Scraping YouTube video traffic source data for {}", youtube)

    # Cache videos to prevent multiple queries for the same video
    video_cache: Dict[str, YouTubeVideo] = {}

    rows_iter = google.get_bigquery_traffic_source(
        youtube.bigquery_suffix,
        start_date,
        end_date=end_date,
    )

    for row in rows_iter:
        defaults = {
            "views": row.views,
            "watch_time": to_timedelta(row.watch_time_minutes * 60),
        }

        # Find video in cache or query database
        youtube_video = _get_youtube_video(row.video_id, video_cache)

        if youtube_video is None:
            logger.warning("Video {} not found in database", row.video_id)
            continue
        elif youtube_video.published_at.date() < start_date:
            logger.debug(
                "Video {} published before start date {}, skipping to prevent overwriting with bad data",
                youtube_video,
                start_date,
            )
            continue

        try:
            YouTubeVideoTrafficSource.objects.update_or_create(
                youtube_video=youtube_video,
                source_type=YouTubeVideoTrafficSource.SourceType[
                    f"SOURCE_TYPE_{row.traffic_source_type}"
                ],
                defaults=defaults,
            )
        except IntegrityError as e:
            capture_exception(e)
            logger.exception(
                "Data for video analytics at {} failed integrity check:\n{}",
                row.time,
                defaults,
            )


def scrape_video_external_traffic(
    *,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
    youtube_filter: Optional[Q] = None,
):
    """Read YouTube external traffic data for videos from BigQuery and store in database.

    Results are saved in
    :class:`~okr.models.youtube.YouTubeVideoTrafficSource`.

    Args:
        start_date (Optional[date], optional): Earliest data to request data for.
            This date refers to the partition field value, not the date of the
            data itself. Defaults to None. If None, the start date will be
            set to 6 months in the past.
        end_date (Optional[date], optional): Latest data to request data for.
            Defaults to None.
        youtube_filter (Optional[Q], optional): Q object to filter data with.
            Defaults to None.
    """
    youtubes = YouTube.objects.all()

    if youtube_filter:
        youtubes = youtubes.filter(youtube_filter)

    if start_date is None:
        start_date = local_today() - dt.timedelta(days=31 * 6)

    for youtube in youtubes:
        try:
            _scrape_video_external_traffic_youtube(start_date, end_date, youtube)
        except Exception as e:
            capture_exception(e)


def _scrape_video_external_traffic_youtube(start_date, end_date, youtube):
    logger.info("Scraping YouTube video external traffic data for {}", youtube)

    # Cache videos to prevent multiple queries for the same video
    video_cache: Dict[str, YouTubeVideo] = {}

    rows_iter = google.get_bigquery_external_traffic(
        youtube.bigquery_suffix,
        start_date,
        end_date=end_date,
    )

    for row in rows_iter:
        defaults = {
            "views": row.views,
            "watch_time": to_timedelta(row.watch_time_minutes * 60),
        }

        # Find video in cache or query database
        youtube_video = _get_youtube_video(row.video_id, video_cache)

        if youtube_video is None:
            continue
        elif youtube_video.published_at.date() < start_date:
            logger.debug(
                "Video {} published before start date {}, skipping to prevent overwriting with bad data",
                youtube_video,
                start_date,
            )
            continue

        try:
            YouTubeVideoExternalTraffic.objects.update_or_create(
                youtube_video=youtube_video,
                name=row.traffic_source_detail,
                defaults=defaults,
            )
        except IntegrityError as e:
            capture_exception(e)
            logger.exception(
                "Data for video analytics at {} failed integrity check:\n{}",
                row.time,
                defaults,
            )


def scrape_video_search_terms(
    *,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
    youtube_filter: Optional[Q] = None,
):
    """Read YouTube search term data for videos from BigQuery and store in database.

    Results are saved in
    :class:`~okr.models.youtube.YouTubeVideoTrafficSource`.

    Args:
        start_date (Optional[date], optional): Earliest data to request data for.
            This date refers to the partition field value, not the date of the
            data itself. Defaults to None. If None, the start date will be
            set to 6 months in the past.
        end_date (Optional[date], optional): Latest data to request data for.
            Defaults to None.
        youtube_filter (Optional[Q], optional): Q object to filter data with.
            Defaults to None.
    """
    youtubes = YouTube.objects.all()

    if youtube_filter:
        youtubes = youtubes.filter(youtube_filter)

    if start_date is None:
        start_date = local_today() - dt.timedelta(days=31 * 6)

    for youtube in youtubes:
        try:
            _scrape_video_search_terms_youtube(start_date, end_date, youtube)
        except Exception as e:
            capture_exception(e)


def _scrape_video_search_terms_youtube(start_date, end_date, youtube):
    logger.info("Scraping YouTube video search term data for {}", youtube)

    # Cache videos to prevent multiple queries for the same video
    video_cache: Dict[str, YouTubeVideo] = {}

    rows_iter = google.get_bigquery_search_terms(
        youtube.bigquery_suffix,
        start_date,
        end_date=end_date,
    )

    for row in rows_iter:
        defaults = {
            "views": row.views,
            "watch_time": to_timedelta(row.watch_time_minutes * 60),
        }

        # Find video in cache or query database
        youtube_video = _get_youtube_video(row.video_id, video_cache)

        if youtube_video is None:
            continue
        elif youtube_video.published_at.date() < start_date:
            logger.debug(
                "Video {} published before start date {}, skipping to prevent overwriting with bad data",
                youtube_video,
                start_date,
            )
            continue

        try:
            YouTubeVideoSearchTerm.objects.update_or_create(
                youtube_video=youtube_video,
                search_term=row.traffic_source_detail,
                defaults=defaults,
            )
        except IntegrityError as e:
            capture_exception(e)
            logger.exception(
                "Data for video analytics at {} failed integrity check:\n{}",
                row.time,
                defaults,
            )


def scrape_video_demographics(
    *,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
    youtube_filter: Optional[Q] = None,
):
    """Read YouTube demographics data for videos from BigQuery and store in database.

    Results are saved in
    :class:`~okr.models.youtube.YouTubeVideoDemographics`.

    Args:
        start_date (Optional[date], optional): Earliest data to request data for.
            This date refers to the partition field value, not the date of the
            data itself. Defaults to None. If None, the start date will be
            set to 6 months in the past.
        end_date (Optional[date], optional): Latest data to request data for.
            Defaults to None.
        youtube_filter (Optional[Q], optional): Q object to filter data with.
            Defaults to None.
    """
    youtubes = YouTube.objects.all()

    if youtube_filter:
        youtubes = youtubes.filter(youtube_filter)

    if start_date is None:
        start_date = local_today() - dt.timedelta(days=31 * 6)

    for youtube in youtubes:
        try:
            _scrape_video_demographics_youtube(start_date, end_date, youtube)
        except Exception as e:
            capture_exception(e)


def _scrape_video_demographics_youtube(start_date, end_date, youtube):
    logger.info("Scraping YouTube video demographics data for {}", youtube)

    # Cache videos to prevent multiple queries for the same video
    video_cache: Dict[str, YouTubeVideo] = {}

    rows_iter = google.get_bigquery_video_demographics(
        youtube.bigquery_suffix,
        start_date,
        end_date=end_date,
    )

    for row in rows_iter:
        # Find video in cache or query database
        youtube_video = _get_youtube_video(row.video_id, video_cache)

        if youtube_video is None:
            continue
        elif youtube_video.published_at.date() < start_date:
            logger.debug(
                "Video {} published before start date {}, skipping to prevent overwriting with bad data",
                youtube_video,
                start_date,
            )
            continue

        # Convert gender to enum
        gender = row.gender.lower()
        if gender in ["genderUserSpecified", "user_specified"]:
            gender = "gender_other"
        gender = YouTubeVideoDemographics.Gender(row.gender.lower())

        age_range = YouTubeVideoDemographics.AgeRange(
            row.age_group[4:].replace("65_", "65+").replace("_", "-")
        )

        defaults = {
            "views_percentage": row.views_percentage,
        }

        try:
            YouTubeVideoDemographics.objects.update_or_create(
                youtube_video=youtube_video,
                gender=gender,
                age_range=age_range,
                defaults=defaults,
            )
        except IntegrityError as e:
            capture_exception(e)
            logger.exception(
                "Data for video demographics at {} failed integrity check:\n{}",
                row.time,
                defaults,
            )
