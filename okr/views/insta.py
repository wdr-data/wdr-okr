from datetime import date, datetime
from pytz import timezone

from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from ..models.insta import *
from .. import quintly

berlin = timezone("Europe/Berlin")


@require_POST
@csrf_exempt
def trigger_insights(request, interval):

    for insta in Insta.objects.all():

        df = quintly.get_insta_insights(insta.quintly_profile_id, interval=interval)

        for index, row in df.iterrows():
            defaults = {
                "reach": row.reach,
                "impressions": row.impressions,
                "followers": row.followers,
                "followers_change": row.followersChange,
                "posts_change": row.postsChange,
            }

            if interval == "daily":
                defaults.update(
                    {
                        "text_message_clicks_day": row.textMessageClicksDay,
                        "email_contacts_day": row.emailContactsDay,
                    }
                )

            obj, created = InstaInsight.objects.update_or_create(
                insta=insta,
                time=date.fromisoformat(row.time),
                interval=interval,
                defaults=defaults,
            )

    return HttpResponse("ok")


@require_POST
@csrf_exempt
def trigger_stories(request):

    for insta in Insta.objects.all():
        df = quintly.get_insta_stories(insta.quintly_profile_id)

        for index, row in df.iterrows():
            defaults = {
                "time": berlin.localize(datetime.fromisoformat(row.time)),
                "caption": row.caption,
                "reach": row.reach,
                "impressions": row.impressions,
                "replies": row.replies,
                "story_type": row.type,
                "link": row.link,
                "exits": row.exits,
            }

            obj, created = InstaStory.objects.update_or_create(
                insta=insta, external_id=row.externalId, defaults=defaults,
            )

    return HttpResponse("ok")
