from datetime import date

from django.db.utils import IntegrityError

from ...models.youtube import *
from ..common import quintly


def scrape_analytics(interval):
    for youtube in YouTube.objects.all():

        df = quintly.get_youtube_analytics(
            youtube.quintly_profile_id, interval=interval
        )

        for index, row in df.iterrows():
            defaults = {
                "views": row.views,
                "likes": row.likes,
                "dislikes": row.dislikes,
                "estimated_minutes_watched": row.estimatedMinutesWatched,
                "average_view_duration": row.averageViewDuration,
            }

            try:
                obj, created = YouTubeAnalytics.objects.update_or_create(
                    youtube=youtube,
                    time=date.fromisoformat(row.time),
                    interval=interval,
                    defaults=defaults,
                )
            except IntegrityError:
                print(
                    f"Data for analytics with interval {interval} at {row.time} failed integrity check:",
                    defaults,
                    sep="\n",
                )
