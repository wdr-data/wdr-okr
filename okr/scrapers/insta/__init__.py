from datetime import date, datetime
from pytz import timezone

from django.db.utils import IntegrityError

from ...models.insta import *
from ..common import quintly


berlin = timezone("Europe/Berlin")


def scrape_insights(interval, *, start_date=None):
    for insta in Insta.objects.all():

        df = quintly.get_insta_insights(
            insta.quintly_profile_id, interval=interval, start_date=start_date,
        )

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

            try:
                obj, created = InstaInsight.objects.update_or_create(
                    insta=insta,
                    date=date.fromisoformat(row.time),
                    interval=interval,
                    defaults=defaults,
                )
            except IntegrityError:
                print(
                    f"Data for {interval} insight for date {row.time} failed integrity check:",
                    defaults,
                    sep="\n",
                )


def scrape_stories(*, start_date=None):
    for insta in Insta.objects.all():
        df = quintly.get_insta_stories(insta.quintly_profile_id, start_date=start_date)

        for index, row in df.iterrows():
            defaults = {
                "created_at": berlin.localize(datetime.fromisoformat(row.time)),
                "caption": row.caption,
                "reach": row.reach,
                "impressions": row.impressions,
                "replies": row.replies,
                "story_type": row.type,
                "link": row.link,
                "exits": row.exits,
            }

            try:
                obj, created = InstaStory.objects.update_or_create(
                    insta=insta, external_id=row.externalId, defaults=defaults,
                )
            except IntegrityError:
                print(
                    f"Data for story with ID {row.externalId} failed integrity check:",
                    defaults,
                    sep="\n",
                )


def scrape_posts(*, start_date=None):
    for insta in Insta.objects.all():
        df = quintly.get_insta_posts(insta.quintly_profile_id, start_date=start_date)

        for index, row in df.iterrows():
            defaults = {
                "created_at": berlin.localize(datetime.fromisoformat(row.time)),
                "message": row.message,
                "comments": row.comments,
                "reach": row.reach,
                "impressions": row.impressions,
                "post_type": row.type,
                "likes": row.likes,
                "link": row.link,
            }

            try:
                obj, created = InstaPost.objects.update_or_create(
                    insta=insta, external_id=row.externalId, defaults=defaults,
                )
            except IntegrityError:
                print(
                    f"Data for post with ID {row.externalId} failed integrity check:",
                    defaults,
                    sep="\n",
                )