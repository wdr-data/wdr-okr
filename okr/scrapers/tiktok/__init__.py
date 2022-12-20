"""Read and process data for TikTok from Quintly."""

import datetime as dt
import json
from time import sleep
from typing import Optional

from django.db.models import Q
from loguru import logger
from sentry_sdk import capture_exception

from ...models.tiktok import (
    TikTok,
    TikTokData,
    TikTokPost,
    TikTokHashtag,
    TikTokTag,
)
from . import quintly
from ..common.utils import BERLIN, to_timedelta


def scrape_full(tiktok: TikTok):
    """Initiate scraping for daily, weekly, and monthly TikTok data from Quintly.

    Args:
        tiktok (TikTok): TikTok object to collect data for.
    """
    tiktok_filter = Q(id=tiktok.id)
    start_date = dt.date(2021, 1, 1)

    logger.info('Starting full scrape for TikTok account "{}"', tiktok.name)

    sleep(1)

    scrape_data(start_date=start_date, tiktok_filter=tiktok_filter)

    scrape_posts(start_date=start_date, tiktok_filter=tiktok_filter)

    logger.success('Finished full scrape for TikTok account "{}"', tiktok.name)


def scrape_data(
    *,
    start_date: Optional[dt.date] = None,
    tiktok_filter: Optional[Q] = None,
):
    """Retrieve TikTok data from Quintly.

    Results are saved in :class:`~okr.models.tiktok.TikTok`.

    Args:
        start_date (Optional[date], optional): Earliest date to request data for.
          Defaults to None.
        tiktok_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.tiktok.TikTok` object. Defaults to None.
    """
    tiktoks = TikTok.objects.all()

    if tiktok_filter:
        tiktoks = tiktoks.filter(tiktok_filter)

    for tiktok in tiktoks:
        try:
            _scrape_data_tiktok(start_date, tiktok)
        except Exception as e:
            logger.error(
                'Failed to scrape TikTok data for TikTok "{}": {}',
                tiktok.name,
                e,
            )
            capture_exception(e)


def _scrape_data_tiktok(start_date, tiktok):
    df = quintly.get_tiktok(tiktok.quintly_profile_id, start_date=start_date)

    for index, row in df.iterrows():
        date = dt.date.fromisoformat(row.time)

        # Count all videos in this account until the given date
        total_videos = TikTokPost.objects.filter(
            tiktok=tiktok,
            created_at__lte=BERLIN.localize(dt.datetime.combine(date, dt.time.max)),
        ).count()

        defaults = {
            "followers": row.followers,
            "followers_change": row.followersChange,
            "following": row.following,
            "following_change": row.followingChange,
            "likes": row.likes,
            "likes_change": row.likesChange,
            "videos": total_videos,
            "videos_change": row.ownVideos,
        }

        obj, created = TikTokData.objects.update_or_create(
            tiktok=tiktok,
            date=date,
            defaults=defaults,
        )


def scrape_posts(
    *, start_date: Optional[dt.date] = None, tiktok_filter: Optional[Q] = None
):
    """Retrieve data for TikTok posts from Quintly.

    Results are saved in :class:`~okr.models.tiktok.TikTokPost`.

    Args:
        start_date (Optional[date], optional): Earliest date to request data for.
          Defaults to None.
        tiktok_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.tiktok.TikTok` object. Defaults to None.
    """
    tiktoks = TikTok.objects.all()

    if tiktok_filter:
        tiktoks = tiktoks.filter(tiktok_filter)

    for tiktok in tiktoks:
        try:
            _scrape_posts_tiktok(start_date, tiktok)
        except Exception as e:
            logger.error(
                'Failed to scrape TikTok posts for TikTok "{}": {}',
                tiktok.name,
                e,
            )
            capture_exception(e)


def _scrape_posts_tiktok(start_date, tiktok):
    df = quintly.get_tiktok_posts(tiktok.quintly_profile_id, start_date=start_date)

    for index, row in df.iterrows():
        defaults = {
            "created_at": BERLIN.localize(dt.datetime.fromisoformat(row.time)),
            "link": row.link,
            "description": row.description,
            "video_length": to_timedelta(row.videoLength),
            "video_cover_url": row.videoCoverUrl,
            "likes": row.likes,
            "comments": row.comments,
            "shares": row.shares,
            "views": row.views,
        }

        tiktok_post, created = TikTokPost.objects.update_or_create(
            tiktok=tiktok, external_id=row.externalId, defaults=defaults
        )

        for hashtag in json.loads(row.hashtags):
            tiktok_hashtag, created = TikTokHashtag.objects.get_or_create(
                hashtag=hashtag,
            )
            tiktok_post.hashtags.add(tiktok_hashtag)

        for tag_dict in json.loads(row.postTags):
            tiktok_tag, created = TikTokTag.objects.get_or_create(
                name=tag_dict["name"],
            )
            tiktok_post.tags.add(tiktok_tag)
