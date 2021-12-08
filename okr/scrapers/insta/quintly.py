""" Methods for scraping insta data with Quintly """

import datetime
from typing import Optional

import numpy as np
import pandas as pd

from ..common import quintly as common_quintly
from ..common import utils


@common_quintly.requires_quintly
def get_insta_insights(
    profile_id: int,
    *,
    start_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Read data for posts on Instagram profile via Quintly API.

    Args:
        profile_id (int): ID of profile to request data for.
        start_date ([type], optional): Date of earliest data to request. Defaults to
          None. Will be set to include at least two intervals if None.

    Returns:
        pd.DataFrame: API response data.
    """
    profile_ids = [profile_id]

    today = utils.local_today()

    start_date = start_date or today - datetime.timedelta(days=7)

    end_date = today

    table = "instagram"
    fields = [
        "time",
        "followers",
    ]

    df_insta = common_quintly.quintly.run_query(
        profile_ids,
        table,
        fields,
        start_date,
        end_date,
        interval="daily",
    )

    table = "instagramInsights"

    fields = [
        "time",
        "importTime",
        "reachDay",
        "reachWeek",
        "reachDays28",
        "impressionsDay",
        "textMessageClicksDay",
        "emailContactsDay",
        "profileViewsDay",
    ]

    df_insta_insights = common_quintly.quintly.run_query(
        profile_ids,
        table,
        fields,
        start_date,
        end_date,
        interval="daily",
    )

    df_insta.time = df_insta.time.str[:10]
    df_insta.time = df_insta.time.astype("str")
    df_insta_insights.time = df_insta_insights.time.str[:10]
    df_insta_insights.time = df_insta_insights.time.astype("str")

    df = df_insta.merge(df_insta_insights, on="time", how="inner")

    df = df.replace({np.nan: None})

    return df


@common_quintly.requires_quintly
def get_insta_stories(
    profile_id: int,
    *,
    start_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Read data for stories on Instagram profile via Quintly API.

    Args:
        profile_id (int): ID of profile to request data for.
        start_date (Optional[datetime.date], optional): Date of earliest possible
          data to request. Defaults to None. Will be set to today's date one week ago if
          None.

    Returns:
        pd.DataFrame: API response data.
    """
    profile_ids = [profile_id]
    table = "instagramInsightsStories"
    fields = [
        "externalId",
        "time",
        "importTime",
        "caption",
        "reach",
        "impressions",
        "replies",
        "tapsForward",
        "tapsBack",
        "type",
        "link",
        "exits",
    ]
    start_date = start_date or datetime.date.today() - datetime.timedelta(days=7)
    end_date = datetime.date.today()
    df = common_quintly.quintly.run_query(
        profile_ids, table, fields, start_date, end_date
    )

    df = df.replace({np.nan: None})

    return df


@common_quintly.requires_quintly
def get_insta_posts(
    profile_id: int,
    *,
    start_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Read data for posts on Instagram profile via Quintly API.

    Args:
        profile_id (int): ID of profile to request data for.
        start_date (Optional[datetime.date], optional): Date of earliest possible
          data to request. Defaults to None. Will be set to today's date one week ago if
          None.

    Returns:
        pd.DataFrame:  API response data.
    """

    profile_ids = [profile_id]
    table = "instagramInsightsOwnPosts"
    fields = [
        "externalId",
        "importTime",
        "impressions",
        "comments",
        "likes",
        "link",
        "message",
        "reach",
        "saved",
        "time",
        "type",
        "videoViews",
    ]
    start_date = start_date or datetime.date.today() - datetime.timedelta(days=120)
    end_date = datetime.date.today()

    df = common_quintly.quintly.run_query(
        profile_ids, table, fields, start_date, end_date
    )

    df = df.replace({np.nan: None})

    return df


@common_quintly.requires_quintly
def get_insta_igtv(
    profile_id: int,
    *,
    start_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Read data for IGTV on Instagram profile via Quintly API.

    Args:
        profile_id (int): ID of profile to request data for.
        start_date (Optional[datetime.date], optional): Date of earliest possible
          data to request. Defaults to None. Will be set to today's date one week ago if
          None.

    Returns:
        pd.DataFrame:  API response data.
    """
    profile_ids = [profile_id]
    table = "instagramInsightsTvPosts"
    fields = [
        "externalId",
        "time",
        "importTime",
        "message",
        "videoTitle",
        "likes",
        "comments",
        "reach",
        "impressions",
        "saved",
        "videoViews",
        "link",
    ]
    start_date = start_date or datetime.date.today() - datetime.timedelta(days=120)
    end_date = datetime.date.today()
    df = common_quintly.quintly.run_query(
        profile_ids, table, fields, start_date, end_date
    )

    df = df.replace({np.nan: None})

    return df


@common_quintly.requires_quintly
def get_insta_comments(
    profile_id: int,
    *,
    start_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Read data for comments on Instagram profile via Quintly API.

    Args:
        profile_id (int): ID of profile to request data for.
        start_date (Optional[datetime.date], optional): Date of earliest possible
          data to request. Defaults to None. Will be set to today's date one week ago if
          None.

    Returns:
        pd.DataFrame:  API response data.
    """

    profile_ids = [profile_id]
    table = "instagramInsightsComments"
    fields = [
        "externalId",
        "externalPostId",
        "time",
        "isAccountAnswer",
        "username",
        "message",
        "likes",
        "isReply",
        "parentCommentId",
        "isHidden",
        "importTime",
    ]
    start_date = start_date or datetime.date.today() - datetime.timedelta(days=120)
    end_date = datetime.date.today()

    df = common_quintly.quintly.run_query(
        profile_ids, table, fields, start_date, end_date
    )

    df = df.replace({np.nan: None})

    return df


@common_quintly.requires_quintly
def get_insta_demographics(
    profile_id: int,
    *,
    start_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Read data for Instagram demographics via Quintly API.

    Args:
        profile_id (int): ID of profile to request data for.
        start_date ([type], optional): Date of earliest data to request. Defaults to
          None. Will be set to include at least two intervals if None.

    Returns:
        pd.DataFrame: API response data.
    """
    profile_ids = [profile_id]

    today = utils.local_today()

    start_date = start_date or today - datetime.timedelta(days=7)

    end_date = today

    table = "instagramInsights"

    fields = [
        "time",
        "importTime",
        "audienceGenderAndAge",
    ]

    df = common_quintly.quintly.run_query(
        profile_ids,
        table,
        fields,
        start_date,
        end_date,
        interval="daily",
    )

    df = df.replace({np.nan: None})

    return df


@common_quintly.requires_quintly
def get_insta_hourly_followers(
    profile_id: int,
    *,
    start_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Read data for Instagram hourly followers via Quintly API.

    Args:
        profile_id (int): ID of profile to request data for.
        start_date ([type], optional): Date of earliest data to request. Defaults to
          None. Will be set to include at least two intervals if None.

    Returns:
        pd.DataFrame: API response data.
    """
    profile_ids = [profile_id]

    today = utils.local_today()

    start_date = start_date or today - datetime.timedelta(days=7)

    end_date = today

    table = "instagramInsights"

    fields = [
        "time",
        "importTime",
        "onlineFollowers",
    ]

    df = common_quintly.quintly.run_query(
        profile_ids,
        table,
        fields,
        start_date,
        end_date,
        interval="daily",
    )

    df = df.replace({np.nan: None})

    return df
