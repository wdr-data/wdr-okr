""" Methods for scraping facebook data with Quintly """

import datetime
from typing import Optional

import numpy as np
import pandas as pd

from ..common import quintly as common_quintly
from ..common import utils


@common_quintly.requires_quintly
def get_facebook_insights(
    profile_id: int,
    *,
    interval: str = "daily",
    start_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Read data for posts on Facebook profile via Quintly API.

    Args:
        profile_id (int): ID of profile to request data for.
        interval (str, optional): Description of interval. Defaults to "daily".
        start_date ([type], optional): Date of earliest data to request. Defaults to
          None. Will be set to include at least two intervals if None.

    Returns:
        pd.DataFrame: API response data.
    """
    profile_ids = [profile_id]

    today = utils.local_today()

    if start_date is None:
        if interval == "daily":
            start_date = today - datetime.timedelta(days=3)
        elif interval == "weekly":
            start_date = today - datetime.timedelta(days=14)
        elif interval == "monthly":
            start_date = today - datetime.timedelta(days=60)

    end_date = today

    table = "facebookInsights"
    fields = [
        "time",
        "page_fans",
        "page_follows",
        "page_impressions_unique",
    ]

    if interval == "daily":
        fields.append("page_fans_online_per_day")

    df_facebook_insights = common_quintly.quintly.run_query(
        profile_ids, table, fields, start_date, end_date, interval=interval
    )

    df_facebook_insights.time = df_facebook_insights.time.str[:10]
    df_facebook_insights.time = df_facebook_insights.time.astype("str")

    df_facebook_insights = df_facebook_insights.replace({np.nan: None})

    return df_facebook_insights


@common_quintly.requires_quintly
def get_facebook_posts(
    profile_id: int,
    *,
    start_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Read data for posts on Facebook profile via Quintly API.

    Args:
        profile_id (int): ID of profile to request data for.
        start_date (Optional[datetime.date], optional): Date of earliest possible
          data to request. Defaults to None. Will be set to today's date one week ago if
          None.

    Returns:
        pd.DataFrame:  API response data.
    """
    profile_ids = [profile_id]
    table = "facebookInsightsOwnPosts"
    fields = [
        "externalId",
        "time",
        "type",
        "link",
        "message",
        "likes",
        "love",
        "wow",
        "haha",
        "sad",
        "angry",
        "comments",
        "shares",
        "post_impressions",
        "post_impressions_unique",
        "is_published",
        "is_hidden",
    ]
    start_date = start_date or datetime.date.today() - datetime.timedelta(days=7)
    end_date = datetime.date.today()

    df_posts_insights = common_quintly.quintly.run_query(
        profile_ids, table, fields, start_date, end_date
    )

    df_posts_insights = df_posts_insights.replace({np.nan: None})

    return df_posts_insights
