from datetime import date, datetime
from pytz import timezone

from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from ..models.youtube import *
from ..scrapers import quintly

berlin = timezone("Europe/Berlin")


@require_POST
@csrf_exempt
def trigger_analytics(request, interval):

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

            obj, created = YouTubeAnalytics.objects.update_or_create(
                youtube=youtube,
                time=date.fromisoformat(row.time),
                interval=interval,
                defaults=defaults,
            )

    return HttpResponse("ok")
