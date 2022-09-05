"""Read and process data for Instagram from Quintly."""

import datetime as dt
import json
from time import sleep
from typing import Dict, Generator, Optional

from django.db.utils import IntegrityError
from django.db.models import Q, Sum
from loguru import logger
from sentry_sdk import capture_exception
from bulk_sync import bulk_sync

from ...models.insta import (
    Insta,
    InstaInsight,
    InstaPost,
    InstaStory,
    InstaIGTV,
    InstaIGTVData,
    InstaComment,
    InstaDemographics,
    InstaHourlyFollowers,
    InstaVideoData,
    InstaReelData,
)
from . import quintly
from ..common.utils import BERLIN, local_today


def scrape_full(insta: Insta):
    """Initiate scraping for daily, weekly, and monthly Instagram data from Quintly.

    Args:
        insta (Insta): Instagram object to collect data for.
    """

    logger.info('Starting full scrape for Instagram account "{}"', insta.name)

    insta_filter = Q(id=insta.id)
    start_date = dt.date(2019, 1, 1)

    sleep(1)

    scrape_insights(start_date=start_date, insta_filter=insta_filter)
    scrape_stories(start_date=start_date, insta_filter=insta_filter)
    scrape_posts(start_date=start_date, insta_filter=insta_filter)
    scrape_igtv(start_date=start_date, insta_filter=insta_filter)
    scrape_comments(start_date=start_date, insta_filter=insta_filter)
    scrape_demographics(start_date=start_date, insta_filter=insta_filter)
    scrape_hourly_followers(start_date=start_date, insta_filter=insta_filter)

    logger.success('Finished full scrape for Instagram account "{}"', insta.name)


def scrape_insights(
    *,
    start_date: Optional[dt.date] = None,
    insta_filter: Optional[Q] = None,
):
    """Retrieve Instagram insights data from Quintly.

    Results are saved in :class:`~okr.models.insta.InstaInsight`.

    Args:
        start_date (Optional[dt.date], optional): Earliest date to request data for.
            Defaults to None.
        insta_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.insta.Insta` object. Defaults to None.
    """
    instas = Insta.objects.all()

    if insta_filter:
        instas = instas.filter(insta_filter)

    for insta in instas:
        try:
            _scrape_insights_insta(start_date, insta)
        except Exception as e:
            capture_exception(e)


def _scrape_insights_insta(start_date, insta):
    logger.info(f"Scraping Instagram insights for {insta.name}")
    df = quintly.get_insta_insights(insta.quintly_profile_id, start_date=start_date)

    for index, row in df.iterrows():
        if row.importTime is None:
            continue

        defaults = {
            "quintly_last_updated": BERLIN.localize(
                dt.datetime.fromisoformat(row.importTime)
            ),
            "reach": row.reachDay,
            "reach_7_days": row.reachWeek,
            "reach_28_days": row.reachDays28,
            "impressions": row.impressionsDay,
            "followers": row.followers,
            "text_message_clicks_day": row.textMessageClicksDay,
            "email_contacts_day": row.emailContactsDay,
            "profile_views": row.profileViewsDay,
        }

        try:
            obj, created = InstaInsight.objects.update_or_create(
                insta=insta,
                date=dt.date.fromisoformat(row.time),
                defaults=defaults,
            )
        except IntegrityError as e:
            capture_exception(e)
            logger.exception(
                "Data for insights on {} failed integrity check:\n{}",
                row.time,
                defaults,
            )


def scrape_stories(
    *, start_date: Optional[dt.date] = None, insta_filter: Optional[Q] = None
):
    """Retrieve data for Instagram stories from Quintly.

    Results are saved in :class:`~okr.models.insta.InstaStory`.

    Args:
        start_date (Optional[dt.date], optional): Earliest date to request data for.
            Defaults to None.
        insta_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.insta.Insta` object. Defaults to None.
    """
    instas = Insta.objects.all()

    if insta_filter:
        instas = instas.filter(insta_filter)

    for insta in instas:
        try:
            _scrape_stories_insta(start_date, insta)
        except Exception as e:
            capture_exception(e)


def _scrape_stories_insta(start_date, insta):
    logger.info(f"Scraping Instagram stories for {insta.name}")
    df = quintly.get_insta_stories(insta.quintly_profile_id, start_date=start_date)

    for index, row in df.iterrows():
        defaults = {
            "created_at": BERLIN.localize(dt.datetime.fromisoformat(row.time)),
            "quintly_last_updated": BERLIN.localize(
                dt.datetime.fromisoformat(row.importTime)
            ),
            "caption": row.caption,
            "reach": row.reach,
            "impressions": row.impressions,
            "replies": row.replies,
            "taps_forward": row.tapsForward,
            "taps_back": row.tapsBack,
            "story_type": row.type,
            "link": row.link,
            "exits": row.exits,
        }

        try:
            obj, created = InstaStory.objects.update_or_create(
                insta=insta, external_id=row.externalId, defaults=defaults
            )
        except IntegrityError as e:
            capture_exception(e)
            logger.exception(
                "Data for story with ID {} failed integrity check:\n{}",
                row.externalId,
                defaults,
            )


def scrape_posts(
    *, start_date: Optional[dt.date] = None, insta_filter: Optional[Q] = None
):
    """Retrieve data for Instagram posts from Quintly.

    Results are saved in :class:`~okr.models.insta.InstaPost`.
    For video posts, additional results are saved in :class:`~okr.models.insta.InstaVideoData`.

    Args:
        start_date (Optional[dt.date], optional): Earliest date to request data for.
            Defaults to None.
        insta_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.insta.Insta` object. Defaults to None.
    """
    instas = Insta.objects.all()

    if insta_filter:
        instas = instas.filter(insta_filter)

    for insta in instas:
        try:
            _scrape_posts_insta(start_date, insta)
        except Exception as e:
            capture_exception(e)


def _scrape_posts_insta(start_date, insta):
    logger.info(f"Scraping Instagram posts for {insta.name}")
    df = quintly.get_insta_posts(insta.quintly_profile_id, start_date=start_date)

    for index, row in df.iterrows():
        defaults = {
            "created_at": BERLIN.localize(dt.datetime.fromisoformat(row.time)),
            "quintly_last_updated": BERLIN.localize(
                dt.datetime.fromisoformat(row.importTime)
            ),
            "message": row.message or "",
            "comments": row.comments,
            "reach": row.reach,
            "impressions": row.impressions,
            "likes": row.likes,
            "saved": row.saved,
            "video_views": row.videoViews,
            "shares": row.shares,
            "post_type": row.type,
            "link": row.link,
        }

        try:
            obj, created = InstaPost.objects.update_or_create(
                insta=insta,
                external_id=row.externalId,
                defaults=defaults,
            )

            # If this is a video or reel post, save additional data
            if row.type.lower() == "video":
                _scrape_video_daily(insta, obj, defaults)
            elif row.type.lower() == "reel":
                _scrape_reel_daily(insta, obj, defaults)

        except IntegrityError as e:
            capture_exception(e)
            logger.exception(
                "Data for post with ID {} failed integrity check:\n{}",
                row.externalId,
                defaults,
            )


def _scrape_video_daily(insta: Insta, post: InstaPost, defaults: dict):
    """Scrape daily stats for video posts from Quintly."""
    # Copy defaults to avoid modifying the original dict
    defaults = defaults.copy()

    # Delete fields that are not part of the daily stats
    remove_fields = [
        "message",
        "created_at",
        "post_type",
        "link",
        "shares",
    ]
    for field in remove_fields:
        del defaults[field]

    today = local_today()
    diff_fields = [
        "comments",
        "likes",
        "reach",
        "impressions",
        "saved",
        "video_views",
    ]

    # Get sum of existing InstaVideoData
    aggregations = [Sum(field) for field in diff_fields]
    last_data = InstaVideoData.objects.filter(
        post=post,
        date__lt=today,
    ).aggregate(*aggregations)

    # If there is data, calculate differences and save
    for field in diff_fields:
        defaults[field] -= last_data[f"{field}__sum"] or 0

    obj, created = InstaVideoData.objects.update_or_create(
        post=post,
        date=today,
        defaults=defaults,
    )


def _scrape_reel_daily(insta: Insta, post: InstaPost, defaults: dict):
    """Scrape daily stats for reel posts from Quintly."""
    # Copy defaults to avoid modifying the original dict
    defaults = defaults.copy()

    # Delete fields that are not part of the daily stats
    remove_fields = [
        "message",
        "created_at",
        "post_type",
        "link",
        "impressions",  # Reels don't have impressions
    ]
    for field in remove_fields:
        del defaults[field]

    today = local_today()
    diff_fields = [
        "comments",
        "likes",
        "reach",
        "saved",
        "video_views",
        "shares",
    ]

    # Get sum of existing InstaVideoData
    aggregations = [Sum(field) for field in diff_fields]
    last_data = InstaReelData.objects.filter(
        post=post,
        date__lt=today,
    ).aggregate(*aggregations)

    # If there is data, calculate differences and save
    for field in diff_fields:
        defaults[field] -= last_data[f"{field}__sum"] or 0

    obj, created = InstaReelData.objects.update_or_create(
        post=post,
        date=today,
        defaults=defaults,
    )


def scrape_igtv(
    *, start_date: Optional[dt.date] = None, insta_filter: Optional[Q] = None
):
    """Retrieve data for Instagram IGTV videos from Quintly.

    Results are saved in :class:`~okr.models.insta.InstaIGTV`.

    Args:
        start_date (Optional[dt.date], optional): Earliest date to request data for.
            Defaults to None.
        insta_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.insta.Insta` object. Defaults to None.
    """
    instas = Insta.objects.all()

    if insta_filter:
        instas = instas.filter(insta_filter)

    for insta in instas:
        try:
            _scrape_igtv_insta(start_date, insta)
        except Exception as e:
            capture_exception(e)


def _scrape_igtv_insta(start_date, insta):
    logger.info(f"Scraping IGTV for {insta.name}")
    df = quintly.get_insta_igtv(insta.quintly_profile_id, start_date=start_date)

    for index, row in df.iterrows():
        defaults = {
            "created_at": BERLIN.localize(dt.datetime.fromisoformat(row.time)),
            "quintly_last_updated": BERLIN.localize(
                dt.datetime.fromisoformat(row.importTime)
            ),
            "message": row.message or "",
            "video_title": row.videoTitle,
            "likes": row.likes,
            "comments": row.comments,
            "reach": row.reach,
            "impressions": row.impressions,
            "saved": row.saved,
            "video_views": row.videoViews,
            "link": row.link,
        }

        try:
            obj, created = InstaIGTV.objects.update_or_create(
                insta=insta, external_id=row.externalId, defaults=defaults
            )
            _scrape_igtv_daily(insta, obj, defaults)
        except IntegrityError as e:
            capture_exception(e)
            logger.exception(
                "Data for post with ID {} failed integrity check:\n{}",
                row.externalId,
                defaults,
            )


def _scrape_igtv_daily(insta: Insta, igtv: InstaIGTV, defaults: dict):
    """Scrape IGTV daily stats from Quintly."""
    # Copy defaults to avoid modifying the original dict
    defaults = defaults.copy()

    # Delete fields that are not part of the daily stats
    del defaults["created_at"]
    del defaults["message"]
    del defaults["video_title"]
    del defaults["link"]

    today = local_today()
    diff_fields = ["likes", "comments", "reach", "impressions", "saved", "video_views"]

    # Get last InstaIGTVData
    aggregations = [Sum(field) for field in diff_fields]
    last_data = InstaIGTVData.objects.filter(
        igtv=igtv,
        date__lt=today,
    ).aggregate(*aggregations)

    # If there is data, calculate differences and save
    for field in diff_fields:
        defaults[field] -= last_data[f"{field}__sum"] or 0

    obj, created = InstaIGTVData.objects.update_or_create(
        igtv=igtv,
        date=today,
        defaults=defaults,
    )


def scrape_comments(
    *, start_date: Optional[dt.date] = None, insta_filter: Optional[Q] = None
):
    """Retrieve data for Instagram comments from Quintly.

    Results are saved in :class:`~okr.models.insta.InstaComment`.

    Args:
        start_date (Optional[dt.date], optional): Earliest date to request data for.
            Defaults to None.
        insta_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.insta.Insta` object. Defaults to None.
    """
    instas = Insta.objects.all()

    if insta_filter:
        instas = instas.filter(insta_filter)

    for insta in instas:
        try:
            _scrape_comments_insta(start_date, insta)
        except Exception as e:
            logger.exception(f"Failed to scrape comments for {insta.name}")
            capture_exception(e)


def _scrape_comments_insta(start_date, insta):
    logger.info(f"Scraping Instagram comments for {insta.name}")
    dfs = quintly.get_insta_comments(insta.quintly_profile_id, start_date=start_date)

    post_cache: Dict[str, InstaPost] = {}

    for df in dfs:
        comments = list(_scrape_comments_insta_day(insta, post_cache, df))

        # bulk_sync breaks if there are no comments
        if not comments:
            continue

        posts = set(comment.post for comment in comments)

        sync_results = bulk_sync(
            comments,
            ["external_id"],
            Q(post__in=posts),
            batch_size=100,
            skip_deletes=True,
        )
        logger.debug(sync_results)


def _scrape_comments_insta_day(
    insta: Insta, post_cache: Dict[str, InstaPost], df
) -> Generator[InstaComment, None, None]:
    for index, row in df.iterrows():
        defaults = {
            "created_at": BERLIN.localize(dt.datetime.fromisoformat(row.time)),
            "quintly_last_updated": BERLIN.localize(
                dt.datetime.fromisoformat(row.importTime)
            ),
            "is_account_answer": bool(row.isAccountAnswer),
            "username": row.username,
            "message_length": len(row.message or ""),
            "likes": row.likes,
            "is_reply": bool(row.isReply),
            "parent_comment_id": row.parentCommentId,
            "is_hidden": bool(row.isHidden),
        }

        if row.externalPostId in post_cache:
            post = post_cache[row.externalPostId]
        else:
            post = InstaPost.objects.filter(
                insta=insta,
                external_id=row.externalPostId,
            ).first()
            post_cache[row.externalPostId] = post

        if not post:
            logger.debug(
                "Comment with ID {} and post ID {} has no corresponding post",
                row.externalId,
                row.externalPostId,
            )
            continue

        defaults["post"] = post

        # Build comment object for bulk_sync
        yield InstaComment(external_id=row.externalId, **defaults)


def scrape_demographics(
    *,
    start_date: Optional[dt.date] = None,
    insta_filter: Optional[Q] = None,
):
    """Retrieve Instagram demographics data from Quintly.

    Results are saved in :class:`~okr.models.insta.InstaDemographics`.

    Args:
        start_date (Optional[dt.date], optional): Earliest date to request data for.
            Defaults to None.
        insta_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.insta.Insta` object. Defaults to None.
    """
    instas = Insta.objects.all()

    if insta_filter:
        instas = instas.filter(insta_filter)

    for insta in instas:
        try:
            _scrape_demographics_insta(start_date, insta)
        except Exception as e:
            capture_exception(e)


def _scrape_demographics_insta(start_date, insta):
    logger.info(f"Scraping Instagram demographics for {insta.name}")
    df = quintly.get_insta_demographics(insta.quintly_profile_id, start_date=start_date)

    for index, row in df.iterrows():
        if not row.audienceGenderAndAge:
            continue

        for entry in json.loads(row.audienceGenderAndAge):
            gender, _, age_range = entry["id"].partition("-")
            followers = entry["followers"]

            defaults = {
                "quintly_last_updated": BERLIN.localize(
                    dt.datetime.fromisoformat(row.importTime)
                ),
                "followers": followers,
            }

            try:
                obj, created = InstaDemographics.objects.update_or_create(
                    insta=insta,
                    date=dt.date.fromisoformat(row.time[:10]),
                    age_range=age_range,
                    gender=gender,
                    defaults=defaults,
                )

            except IntegrityError as e:
                capture_exception(e)
                logger.exception(
                    "Data for demographics on {} failed integrity check:\n{}",
                    row.time,
                    insta,
                )


def scrape_hourly_followers(
    *,
    start_date: Optional[dt.date] = None,
    insta_filter: Optional[Q] = None,
):
    """Retrieve Instagram hourly followers data from Quintly.

    Results are saved in :class:`~okr.models.insta.InstaHourlyFollowers`.

    Args:
        start_date (Optional[dt.date], optional): Earliest date to request data for.
            Defaults to None.
        insta_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.insta.Insta` object. Defaults to None.
    """
    instas = Insta.objects.all()

    if insta_filter:
        instas = instas.filter(insta_filter)

    for insta in instas:
        try:
            _scrape_hourly_followers_insta(start_date, insta)
        except Exception as e:
            capture_exception(e)


def _scrape_hourly_followers_insta(start_date, insta):
    logger.info(f"Scraping Instagram hourly followers for {insta.name}")
    df = quintly.get_insta_hourly_followers(
        insta.quintly_profile_id, start_date=start_date
    )

    for index, row in df.iterrows():
        if not row.onlineFollowers:
            continue

        date = dt.date.fromisoformat(row.time[:10])
        for entry in json.loads(row.onlineFollowers):
            hour = entry["id"]
            followers = entry["followers"]
            date_time = BERLIN.localize(
                dt.datetime(date.year, date.month, date.day, hour)
            )

            defaults = {
                "quintly_last_updated": BERLIN.localize(
                    dt.datetime.fromisoformat(row.importTime)
                ),
                "followers": followers,
            }

            try:
                obj, created = InstaHourlyFollowers.objects.update_or_create(
                    insta=insta,
                    date_time=date_time,
                    defaults=defaults,
                )
            except IntegrityError as e:
                capture_exception(e)
                logger.exception(
                    "Data for hourly followers on {} failed integrity check:\n{}",
                    date_time,
                    insta,
                )
