from datetime import date
from time import sleep

from django.db.utils import IntegrityError
from django.db.models import Q
from sentry_sdk import capture_exception

from ...models.youtube import *
from ..common import quintly


def scrape_full(youtube):
    youtube_filter = Q(id=youtube.id)
    start_date = date(2019, 1, 1)

    sleep(1)

    scrape_analytics("daily", start_date=start_date, youtube_filter=youtube_filter)
    scrape_analytics("weekly", start_date=start_date, youtube_filter=youtube_filter)
    scrape_analytics("monthly", start_date=start_date, youtube_filter=youtube_filter)


def scrape_analytics(interval, *, start_date=None, youtube_filter=None):
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
