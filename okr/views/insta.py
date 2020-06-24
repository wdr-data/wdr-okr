from datetime import date

from django.http import HttpResponse
from ..models.insta import *
from .. import quintly


def trigger(request):
    # read profile id from db
    # for profile in profiles:

    for insta in Insta.objects.all():

        df = quintly.get_insta_insights(insta.quintly_profile_id)

        for index, row in df.iterrows():
            defaults = {
                "reach": row.reach,
                "impressions": row.impressions,
                "followers": row.followers,
                "followers_change": row.followersChange,
                "posts_change": row.postsChange,
                "text_message_clicks_day": row.textMessageClicksDay,
                "email_contacts_day": row.emailContactsDay,
            }

            obj, created = InstaInsight.objects.update_or_create(
                insta=insta,
                time=date.fromisoformat(row.time),
                interval="daily",
                defaults=defaults,
            )

    return HttpResponse("ok")
