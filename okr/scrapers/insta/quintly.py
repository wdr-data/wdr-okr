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
    interval: str = "daily",
    start_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Read data for posts on Instagram profile via Quintly API.

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

    table = "instagram"
    fields = ["time", "followers", "followersChange", "postsChange"]

    df_insta = common_quintly.quintly.run_query(
        profile_ids, table, fields, start_date, end_date, interval=interval
    )

    table = "instagramInsights"

    fields = ["time", "reach", "impressions"]
    if interval == "daily":
        fields += ["textMessageClicksDay", "emailContactsDay"]

    df_insta_insights = common_quintly.quintly.run_query(
        profile_ids, table, fields, start_date, end_date, interval=interval
    )

    df_insta.time = df_insta.time.str[:10]
    df_insta.time = df_insta.time.astype("str")
    df_insta_insights.time = df_insta_insights.time.str[:10]
    df_insta_insights.time = df_insta_insights.time.astype("str")

    df = df_insta.merge(df_insta_insights, on="time", how="inner")

    df = df.replace({np.nan: None})

    print(df)
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
        "caption",
        "reach",
        "impressions",
        "replies",
        "type",
        "link",
        "exits",
    ]
    start_date = start_date or datetime.date.today() - datetime.timedelta(days=7)
    end_date = datetime.date.today()
    df = common_quintly.quintly.run_query(profile_ids, table, fields, start_date, end_date)

    df = df.replace({np.nan: None})

    print(df)
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
    table = "instagramOwnPosts"
    fields = ["externalId", "time", "message", "comments", "type", "link"]
    start_date = start_date or datetime.date.today() - datetime.timedelta(days=7)
    end_date = datetime.date.today()

    df_posts = common_quintly.quintly.run_query(profile_ids, table, fields, start_date, end_date)

    table = "instagramInsightsOwnPosts"

    fields = ["externalId", "time", "likes", "reach", "impressions"]

    df_posts_insights = common_quintly.quintly.run_query(
        profile_ids, table, fields, start_date, end_date
    )

    df = df_posts.merge(df_posts_insights, on=["externalId", "time"], how="inner")

    df = df.replace({np.nan: None})

    print(df)
    return df
