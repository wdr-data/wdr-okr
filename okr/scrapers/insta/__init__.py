"""Read and process data for Instagram from Quintly."""

from datetime import date, datetime
from time import sleep
from typing import Optional

from django.db.utils import IntegrityError
from django.db.models import Q
from sentry_sdk import capture_exception

from ...models.insta import *
from ..common import quintly
from ..common.utils import BERLIN


def scrape_full(insta: Insta):
    """Initiate scraping for daily, weekly, and monthly Instagram data from Quintly.

    Args:
        insta (Insta): Instagram object to collect data for.
    """
    insta_filter = Q(id=insta.id)
    start_date = date(2019, 1, 1)

    sleep(1)

    scrape_insights("daily", start_date=start_date, insta_filter=insta_filter)
    scrape_insights("weekly", start_date=start_date, insta_filter=insta_filter)
    scrape_insights("monthly", start_date=start_date, insta_filter=insta_filter)

    scrape_stories(start_date=start_date, insta_filter=insta_filter)
    scrape_posts(start_date=start_date, insta_filter=insta_filter)


def scrape_insights(
    interval: str,
    *,
    start_date: Optional[date] = None,
    insta_filter: Optional[Q] = None,
):
    """Retrieve Instagram insights data from Quintly.

    Results are saved in :class:`~okr.models.insta.InstaInsight`.

    Args:
        interval (str): Interval to request data for.
        start_date (Optional[date], optional): Earliest date to request data for.
        Defaults to None.
        insta_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.insta.Insta` object. Defaults to None.
    """
    instas = Insta.objects.all()

    if insta_filter:
        instas = instas.filter(insta_filter)

    for insta in instas:
        df = quintly.get_insta_insights(
            insta.quintly_profile_id, interval=interval, start_date=start_date
        )

        for index, row in df.iterrows():
            defaults = {
                "reach": row.reach or 0,
                "impressions": row.impressions or 0,
                "followers": row.followers or 0,
                "followers_change": row.followersChange or 0,
                "posts_change": row.postsChange or 0,
            }

            if interval == "daily":
                defaults.update(
                    {
                        "text_message_clicks_day": row.textMessageClicksDay or 0,
                        "email_contacts_day": row.emailContactsDay or 0,
                    }
                )

            try:
                obj, created = InstaInsight.objects.update_or_create(
                    insta=insta,
                    date=date.fromisoformat(row.time),
                    interval=interval,
                    defaults=defaults,
                )
            except IntegrityError as e:
                capture_exception(e)
                print(
                    f"Data for {interval} insight for date {row.time} failed integrity check:",
                    defaults,
                    sep="\n",
                )


def scrape_stories(
    *, start_date: Optional[date] = None, insta_filter: Optional[Q] = None
):
    """Retrieve data for Instagram stories from Quintly.

    Results are saved in :class:`~okr.models.insta.InstaStory`.

    Args:
        start_date (Optional[date], optional): Earliest date to request data for.
        Defaults to None.
        insta_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.insta.Insta` object. Defaults to None.
    """
    instas = Insta.objects.all()

    if insta_filter:
        instas = instas.filter(insta_filter)

    for insta in instas:
        df = quintly.get_insta_stories(insta.quintly_profile_id, start_date=start_date)

        for index, row in df.iterrows():
            defaults = {
                "created_at": BERLIN.localize(datetime.fromisoformat(row.time)),
                "caption": row.caption,
                "reach": row.reach or 0,
                "impressions": row.impressions or 0,
                "replies": row.replies or 0,
                "story_type": row.type,
                "link": row.link,
                "exits": row.exits or 0,
            }

            try:
                obj, created = InstaStory.objects.update_or_create(
                    insta=insta, external_id=row.externalId, defaults=defaults
                )
            except IntegrityError as e:
                capture_exception(e)
                print(
                    f"Data for story with ID {row.externalId} failed integrity check:",
                    defaults,
                    sep="\n",
                )


def scrape_posts(
    *, start_date: Optional[date] = None, insta_filter: Optional[Q] = None
):
    """Retrieve data for Instagram posts from Quintly.

    Results are saved in :class:`~okr.models.insta.InstaPost`.

    Args:
        start_date (Optional[date], optional): Earliest date to request data for.
        Defaults to None.
        insta_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.insta.Insta` object. Defaults to None.
    """
    instas = Insta.objects.all()

    if insta_filter:
        instas = instas.filter(insta_filter)

    for insta in instas:
        df = quintly.get_insta_posts(insta.quintly_profile_id, start_date=start_date)

        for index, row in df.iterrows():
            defaults = {
                "created_at": BERLIN.localize(datetime.fromisoformat(row.time)),
                "message": row.message,
                "comments": row.comments or 0,
                "reach": row.reach or 0,
                "impressions": row.impressions or 0,
                "post_type": row.type,
                "likes": row.likes or 0,
                "link": row.link,
            }

            try:
                obj, created = InstaPost.objects.update_or_create(
                    insta=insta, external_id=row.externalId, defaults=defaults
                )
            except IntegrityError as e:
                capture_exception(e)
                print(
                    f"Data for post with ID {row.externalId} failed integrity check:",
                    defaults,
                    sep="\n",
                )
