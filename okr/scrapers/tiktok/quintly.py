""" Methods for scraping TikTok data with Quintly """

import datetime
from typing import Optional

import numpy as np
import pandas as pd

from ..common import quintly as common_quintly
from ..common import utils


@common_quintly.requires_quintly
def get_tiktok(
    profile_id: int,
    *,
    interval: str = "daily",
    start_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Read data for TikTok profile via Quintly API.

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

    table = "tiktok"
    fields = [
        "time",
        "followers",
        "followersChange",
        "following",
        "followingChange",
        "likes",
        "likesChange",
        "videos",
        "videosChange",
    ]

    df = common_quintly.quintly.run_query(
        profile_ids,
        table,
        fields,
        start_date,
        end_date,
        interval=interval,
    )

    # Skip adjustments if the dataframe is empty cause it will fail
    if df.empty:
        return df

    df.time = df.time.str[:10]
    df.time = df.time.astype("str")

    df = df.replace({np.nan: None})

    return df


@common_quintly.requires_quintly
def get_tiktok_posts(
    profile_id: int,
    *,
    start_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Read data for posts on TikTok profile via Quintly API.

    Args:
        profile_id (int): ID of profile to request data for.
        start_date (Optional[datetime.date], optional): Date of earliest possible
          data to request. Defaults to None. Will be set to today's date one week ago if
          None.

    Returns:
        pd.DataFrame:  API response data.
    """
    profile_ids = [profile_id]
    table = "tiktokOwnPosts"
    fields = [
        "externalId",
        "time",
        "link",
        "description",
        "hashtags",
        "challenges",
        "videoLength",
        "videoCoverUrl",
        "musicId",
        "musicTitle",
        "postTags",
        "likes",
        "comments",
        "shares",
        "views",
    ]

    today = utils.local_today()

    start_date = start_date or today - datetime.timedelta(days=365)
    end_date = today

    df = common_quintly.quintly.run_query(
        profile_ids,
        table,
        fields,
        start_date,
        end_date,
    )

    df = df.replace({np.nan: None})

    return df
