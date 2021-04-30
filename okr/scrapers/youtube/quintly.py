""" Methods for scraping YouTube data with Quintly """

import datetime
from typing import Optional

import numpy as np
import pandas as pd

from ..common import quintly as common_quintly
from ..common import utils


@common_quintly.requires_quintly
def get_youtube_analytics(
    profile_id: int,
    *,
    interval: str = "daily",
    start_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Read YouTube data via Quintly API.

    Args:
        profile_id (int): ID of profile to request data for.
        interval (str, optional): Description of interval. Defaults to "daily".
        start_date (Optional[datetime.date], optional): Date of earliest data to
          request. Defaults to None. Will be set to include at least two intervals
          if None.


    Returns:
        pd.DataFrame: API response data.
    """
    profile_ids = [profile_id]

    today = utils.local_today()

    if start_date is None:
        if interval == "daily":
            start_date = today - datetime.timedelta(days=7)
        elif interval == "weekly":
            start_date = today - datetime.timedelta(days=14)
        elif interval == "monthly":
            start_date = today - datetime.timedelta(days=60)

    end_date = today

    # Scrape "youtubeAnalytics" table
    table = "youtubeAnalytics"
    fields = [
        "time",
        "views",
        "likes",
        "dislikes",
        "estimatedMinutesWatched",
        "averageViewDuration",
        "subscribersGained",
    ]

    df_youtube_analytics = common_quintly.quintly.run_query(
        profile_ids,
        table,
        fields,
        start_date,
        end_date,
        interval=interval,
    )

    df_youtube_analytics.time = df_youtube_analytics.time.str[:10]
    df_youtube_analytics.time = df_youtube_analytics.time.astype("str")

    # Scrape "youtube" table
    table = "youtube"
    fields = [
        "time",
        "subscribers",
    ]

    df_youtube = common_quintly.quintly.run_query(
        profile_ids,
        table,
        fields,
        start_date,
        end_date,
        interval=interval,
    )

    df_youtube.time = df_youtube.time.str[:10]
    df_youtube.time = df_youtube.time.astype("str")

    df = df_youtube.merge(df_youtube_analytics, on="time", how="inner")

    df = df.replace({np.nan: None})

    return df
