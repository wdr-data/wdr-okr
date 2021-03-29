""" Methods for scraping YouTube data with Quintly """

import datetime
from typing import Optional
from loguru import logger

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
    table = "youtubeAnalytics"

    today = utils.local_today()

    if start_date is None:
        if interval == "daily":
            start_date = today - datetime.timedelta(days=7)
        elif interval == "weekly":
            start_date = today - datetime.timedelta(days=14)
        elif interval == "monthly":
            start_date = today - datetime.timedelta(days=60)

    end_date = today

    fields = [
        "time",
        "views",
        "likes",
        "dislikes",
        "estimatedMinutesWatched",
        "averageViewDuration",
    ]

    df = common_quintly.quintly.run_query(
        profile_ids,
        table,
        fields,
        start_date,
        end_date,
        interval=interval,
    )

    df.time = df.time.str[:10]
    df.time = df.time.astype("str")
    df = df.replace({np.nan: None})

    logger.debug(df)
    return df
