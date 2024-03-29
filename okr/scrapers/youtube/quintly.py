""" Methods for scraping YouTube data with Quintly """

import datetime as dt
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
    start_date: Optional[dt.date] = None,
) -> pd.DataFrame:
    """Read YouTube channel analytics data via Quintly API.

    Args:
        profile_id (int): ID of profile to request data for.
        interval (str, optional): Description of interval. Defaults to "daily".
        start_date (Optional[datetime.date], optional): Date of earliest data to
          request. Defaults to None. Will be set to seven days ago if None.


    Returns:
        pd.DataFrame: API response data.
    """
    profile_ids = [profile_id]

    today = utils.local_today()

    if start_date is None:
        start_date = today - dt.timedelta(days=7)

    end_date = today

    # Scrape "youtubeAnalytics" table
    table = "youtubeAnalytics"
    fields = [
        "time",
        "views",
        "likes",
        "dislikes",
        "subscribersLifetime",
        "subscribersGained",
        "subscribersLost",
        "estimatedMinutesWatched",
        "viewsPercentageByAgeAndGender",
        "viewsByTrafficSource",
        "estimatedMinutesWatchedByTrafficSource",
        "importTime",
        "profileId",  # needs to be part of query to receive data for subscribersLifetime
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
def get_youtube_videos(
    profile_id: int,
    *,
    interval: str = "daily",
    start_date: Optional[dt.date] = None,
) -> pd.DataFrame:
    """Read basic data for individual YouTube videos via Quintly API.

    Args:
        profile_id (int): ID of profile to request data for.
        interval (str, optional): Description of interval. Defaults to "daily".
        start_date (Optional[datetime.date], optional): Date of earliest data to
          request. Defaults to None. Will be set to seven days ago if None.


    Returns:
        pd.DataFrame: API response data.
    """
    profile_ids = [profile_id]

    today = utils.local_today()

    if start_date is None:
        start_date = today - dt.timedelta(days=7)

    end_date = today

    # Scrape "youtubeAnalyticsVideos" table
    table = "youtubeAnalyticsVideos"
    fields = [
        "externalId",
        "publishTime",
        "liveBroadcastContent",  # Indicates whether the video is scheduled/unpublished
        "liveActualStartTime",
        "title",
        "description",
        "duration",
        "importTime",
        # "viewsPercentageByAgeAndGender",  # generates " 500 Server Error: Internal Server Error" if included
        # "viewsByTrafficSource",  # generates " 500 Server Error: Internal Server Error" if included
    ]

    df = common_quintly.quintly.run_query(
        profile_ids,
        table,
        fields,
        start_date,
        end_date,
        interval=interval,
    )

    df = df.replace({np.nan: None})

    return df
