"""Read and process YouTube data."""

from datetime import date
from time import sleep
from typing import Optional

from django.db.utils import IntegrityError
from django.db.models import Q
from sentry_sdk import capture_exception

from ...models.youtube import *
from . import quintly


def scrape_full(youtube: YouTube):
    """Initiate scraping for daily, weekly, and monthly YouTube data from Quintly.

    Args:
        youtube (YouTube): YouTube object to scrape data for.
    """

    youtube_filter = Q(id=youtube.id)
    start_date = date(2019, 1, 1)

    sleep(1)

    scrape_analytics("daily", start_date=start_date, youtube_filter=youtube_filter)
    scrape_analytics("weekly", start_date=start_date, youtube_filter=youtube_filter)
    scrape_analytics("monthly", start_date=start_date, youtube_filter=youtube_filter)


def scrape_analytics(
    interval: str,
    *,
    start_date: Optional[date] = None,
    youtube_filter: Optional[Q] = None,
):
    """Read YouTube analytics data from Quintly and store in database.

    Results are saved in
    :class:`~okr.models.youtube.YouTubeAnalytics`.

    Args:
        interval (str): Interval to request data for ("daily", "weekly", or "monthly").
        start_date (Optional[date], optional): Earliest data to request data for.
            Defaults to None.
        youtube_filter (Optional[Q], optional): Q object to filter data with.
            Defaults to None.
    """
    youtubes = YouTube.objects.all()

    if youtube_filter:
        youtubes = youtubes.filter(youtube_filter)

    for youtube in youtubes:

        df = quintly.get_youtube_analytics(
            youtube.quintly_profile_id, interval=interval, start_date=start_date
        )

        for index, row in df.iterrows():
            defaults = {
                "views": row.views or 0,
                "likes": row.likes or 0,
                "dislikes": row.dislikes or 0,
                "estimated_minutes_watched": row.estimatedMinutesWatched,
                "average_view_duration": row.averageViewDuration,
            }

            try:
                obj, created = YouTubeAnalytics.objects.update_or_create(
                    youtube=youtube,
                    date=date.fromisoformat(row.time),
                    interval=interval,
                    defaults=defaults,
                )
            except IntegrityError as e:
                capture_exception(e)
                print(
                    f"Data for analytics with interval {interval} at {row.time} failed integrity check:",
                    defaults,
                    sep="\n",
                )
