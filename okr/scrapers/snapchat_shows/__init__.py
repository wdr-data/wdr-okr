"""Read and process data for SnapchatShow from Quintly."""

# from datetime import date, datetime
import datetime as dt
from time import sleep
from typing import Optional

from django.db.utils import IntegrityError
from django.db.models import Q
from loguru import logger
from sentry_sdk import capture_exception

from ...models.snapchat_shows import (
    SnapchatShow,
    SnapchatShowInsight,
    SnapchatShowStory,
)
from . import quintly
from ..common.utils import as_local_tz, to_timedelta


def scrape_full(snapchat_show: SnapchatShow):
    """Initiate scraping for Snapchat show data from Quintly.

    Args:
        snapchat_show (SnapchatShow): SnapchatShow object to collect data for.
    """
    logger.info("Starting full Snapchat show scrape of {}", snapchat_show.name)

    snapchat_show_filter = Q(id=snapchat_show.id)
    start_date = dt.date(2019, 1, 1)

    sleep(1)

    scrape_insights(start_date=start_date, snapchat_show_filter=snapchat_show_filter)
    scrape_stories(start_date=start_date, snapchat_show_filter=snapchat_show_filter)
    logger.success("Finished full Snapchat show scrape of {}", snapchat_show.name)


def scrape_insights(
    *,
    start_date: Optional[dt.date] = None,
    snapchat_show_filter: Optional[Q] = None,
):
    """Retrieve Snapchat show insights data from Quintly.

    Results are saved in :class:`~okr.models.snapchat_shows.SnapchatShowInsight`.

    Args:
        start_date (Optional[dt.date], optional): Earliest date to request data for.
            Defaults to None.
        snapchat_show_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.snapchat_shows.SnapchatShow` object. Defaults to None.
    """
    snapchat_shows = SnapchatShow.objects.all()

    if snapchat_show_filter:
        snapchat_shows = snapchat_shows.filter(snapchat_show_filter)

    for snapchat_show in snapchat_shows:
        logger.debug("Scraping insights for {}", snapchat_show.name)
        df = quintly.get_snapchat_show_insights(
            snapchat_show.quintly_profile_id, start_date=start_date
        )

        for index, row in df.iterrows():
            if row.importTime is None:
                continue

            defaults = {
                "daily_uniques": row.dailyUniques,
                "monthly_uniques": row.monthlyUniques,
                "subscribers": row.subscribers,
                "loyal_users": row.loyalUsers,
                "frequent_users": row.frequentUsers,
                "returning_users": row.returningUsers,
                "new_users": row.newUsers,
                "gender_demographics_male": row.genderDemographicsMaleUsers,
                "gender_demographics_female": row.genderDemographicsFemaleUsers,
                "gender_demographics_unknown": row.genderDemographicsUnknownGenderUsers,
                "age_demographics_13_to_17": row.ageDemographicsAgeRange13To17Users,
                "age_demographics_18_to_24": row.ageDemographicsAgeRange18To24Users,
                "age_demographics_25_to_34": row.ageDemographicsAgeRange25To34Users,
                "age_demographics_35_plus": row.ageDemographicsAgeRange35PlusUsers,
                "age_demographics_unknown": row.ageDemographicsUnknownAgeUsers,
                "total_time_viewed": to_timedelta(row.totalTimeViewed),
                "average_time_spent_per_user": to_timedelta(
                    row.averageTimeSpentPerUser
                ),
                "unique_topsnaps_per_user": row.uniqueTopsnapsPerUser,
                "unique_topsnap_views": row.uniqueTopsnapViews,
                "topsnap_views": row.topsnapViews,
                "attachment_conversion": row.attachmentConversion,
                "attachment_article_views": row.attachmentArticleViews,
                "attachment_video_views": row.attachmentVideoViews,
                "screenshots": row.screenshots,
                "shares": row.shares,
                "quintly_last_updated": as_local_tz(row.importTime),
            }

            try:
                obj, created = SnapchatShowInsight.objects.update_or_create(
                    snapchat_show=snapchat_show,
                    date=dt.date.fromisoformat(row.time),
                    defaults=defaults,
                )
            except IntegrityError as e:
                capture_exception(e)
                logger.exception(
                    "Data for Snapchat show insights on date {} failed integrity check:\n{}",
                    row.time,
                    defaults,
                )


def scrape_stories(
    *, start_date: Optional[dt.date] = None, snapchat_show_filter: Optional[Q] = None
):
    """Retrieve data for Snapchat show stories from Quintly.

    Results are saved in :class:`~okr.models.snapchat_shows.SnapchatShowStory`.

    Args:
        start_date (Optional[dt.date], optional): Earliest date to request data for.
            Defaults to None.
        snapchat_show_filter (Optional[Q], optional): Filter to apply to
            :class:`~okr.models.snapchat_shows.SnapchatShow` object. Defaults to None.
    """
    snapchat_shows = SnapchatShow.objects.all()

    if snapchat_show_filter:
        snapchat_shows = snapchat_shows.filter(snapchat_show_filter)

    for snapchat_show in snapchat_shows:
        logger.debug("Scraping story insights for {}", snapchat_show)
        df = quintly.get_snapchat_show_stories(
            snapchat_show.quintly_profile_id, start_date=start_date
        )

        for index, row in df.iterrows():
            defaults = {
                "create_date_time": as_local_tz(row.createTime),
                "start_date_time": as_local_tz(row.startTime),
                "first_live_date_time": as_local_tz(row.firstLiveTime),
                "spotlight_end_date_time": as_local_tz(row.spotlightEndTime),
                "spotlight_duration": to_timedelta(row.spotlightDuration),
                "title": row.title,
                "state": row.state.lower(),
                "gender_demographics_male": row.genderDemographicsMaleUsers,
                "gender_demographics_female": row.genderDemographicsFemaleUsers,
                "gender_demographics_unknown": row.genderDemographicsUnknownGenderUsers,
                "age_demographics_13_to_17": row.ageDemographicsAgeRange13To17Users,
                "age_demographics_18_to_24": row.ageDemographicsAgeRange18To24Users,
                "age_demographics_25_to_34": row.ageDemographicsAgeRange25To34Users,
                "age_demographics_35_plus": row.ageDemographicsAgeRange35PlusUsers,
                "age_demographics_unknown": row.ageDemographicsUnknownAgeUsers,
                "view_time": to_timedelta(row.viewTime),
                "average_view_time_per_user": to_timedelta(row.averageViewTimePerUser),
                "total_views": row.totalViews,
                "unique_viewers": row.uniqueViewers,
                "unique_completers": row.uniqueCompleters,
                "completion_rate": row.completionRate,
                "shares": row.shares,
                "unique_sharers": row.uniqueSharers,
                "viewers_from_shares": row.viewersFromShares,
                "screenshots": row.screenshots,
                "subscribers": row.subscribers,
                "topsnap_view_time": to_timedelta(row.topsnapViewTime),
                "topsnap_average_view_time_per_user": to_timedelta(
                    row.topsnapAverageViewTimePerUser
                ),
                "topsnap_total_views": row.topsnapTotalViews,
                "topsnap_unique_views": row.topsnapUniqueViews,
                "unique_topsnaps_per_user": row.uniqueTopsnapsPerUser,
                "quintly_last_updated": as_local_tz(row.importTime),
            }

            try:
                obj, created = SnapchatShowStory.objects.update_or_create(
                    snapchat_show=snapchat_show,
                    external_id=row.id,
                    defaults=defaults,
                )
            except IntegrityError as e:
                capture_exception(e)
                logger.exception(
                    "Data for Snapchat story with ID {} failed integrity check:\n{}",
                    row.id,
                    defaults,
                )
