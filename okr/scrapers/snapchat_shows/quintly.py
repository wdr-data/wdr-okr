""" Methods for scraping facebook data with Quintly """

import datetime
from typing import Optional

import numpy as np
import pandas as pd

from ..common import quintly as common_quintly
from ..common import utils


@common_quintly.requires_quintly
def get_snapchat_show_insights(
    profile_id: int,
    *,
    start_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Read data for Snapchat show stories via Quintly API.

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

    table = "snapchatShowInsights"
    fields = [
        "importTime",
        "intervalStartTime",
        "dailyUniques",
        "monthlyUniques",
        "subscribers",
        "loyalUsers",
        "frequentUsers",
        "returningUsers",
        "newUsers",
        "genderDemographicsMaleUsers",
        "genderDemographicsFemaleUsers",
        "genderDemographicsUnknownGenderUsers",
        "ageDemographicsAgeRange13To17Users",
        "ageDemographicsAgeRange18To24Users",
        "ageDemographicsAgeRange25To34Users",
        "ageDemographicsAgeRange35PlusUsers",
        "ageDemographicsUnknownAgeUsers",
        "totalTimeViewed",
        "averageTimeSpentPerUser",
        "uniqueTopsnapsPerUser",
        "uniqueTopsnapViews",
        "topsnapViews",
        "attachmentConversion",
        "attachmentArticleViews",
        "attachmentVideoViews",
        "screenshots",
        "shares",
    ]

    df = common_quintly.quintly.run_query(
        profile_ids,
        table,
        fields,
        start_date,
        end_date,
    )

    # Skip adjustments if the dataframe is empty cause it will fail
    if df.empty:
        return df

    df["time"] = df.intervalStartTime.str[:10]
    df.time = df.time.astype("str")

    df = df.replace({np.nan: None})

    return df


@common_quintly.requires_quintly
def get_snapchat_show_stories(
    profile_id: int,
    *,
    start_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Read data for Snapchat show stories via Quintly API.

    Args:
        profile_id (int): ID of profile to request data for.
        start_date (Optional[datetime.date], optional): Date of earliest possible
          data to request. Defaults to None. Will be set to today's date one week ago if
          None.

    Returns:
        pd.DataFrame:  API response data.
    """
    profile_ids = [profile_id]
    table = "snapchatShowInsightsStories"
    fields = [
        "id",
        "createTime",
        "startTime",
        "firstLiveTime",
        "spotlightEndTime",
        "spotlightDuration",
        "title",
        "state",
        "genderDemographicsMaleUsers",
        "genderDemographicsFemaleUsers",
        "genderDemographicsUnknownGenderUsers",
        "ageDemographicsAgeRange13To17Users",
        "ageDemographicsAgeRange18To24Users",
        "ageDemographicsAgeRange25To34Users",
        "ageDemographicsAgeRange35PlusUsers",
        "ageDemographicsUnknownAgeUsers",
        "viewTime",
        "averageViewTimePerUser",
        "totalViews",
        "uniqueViewers",
        "uniqueCompleters",
        "completionRate",
        "shares",
        "uniqueSharers",
        "viewersFromShares",
        "screenshots",
        "subscribers",
        "topsnapViewTime",
        "topsnapAverageViewTimePerUser",
        "topsnapTotalViews",
        "topsnapUniqueViews",
        "uniqueTopsnapsPerUser",
        "importTime",
    ]
    start_date = start_date or datetime.date.today() - datetime.timedelta(days=7)
    end_date = datetime.date.today()

    df = common_quintly.quintly.run_query(
        profile_ids,
        table,
        fields,
        start_date,
        end_date,
    )

    df = df.replace({np.nan: None})

    return df


@common_quintly.requires_quintly
def get_snapchat_show_story_snaps(
    profile_id: int,
    *,
    start_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Read data for Snapchat show story snaps via Quintly API.

    Args:
        profile_id (int): ID of profile to request data for.
        start_date (Optional[datetime.date], optional): Date of earliest possible
            data to request. Defaults to None. Will be set to today's date one week ago if
            None.

    Returns:
        pd.DataFrame:  API response data.
    """
    profile_ids = [profile_id]
    table = "snapchatShowInsightsSnaps"
    fields = [
        "id",
        "importTime",
        "storyId",
        "name",
        "position",
        "duration",
        "subscribeOptionsHeadline",
        "tiles",
        "genderDemographicsMaleUsers",
        "genderDemographicsFemaleUsers",
        "genderDemographicsUnknownGenderUsers",
        "ageDemographicsAgeRange13To17Users",
        "ageDemographicsAgeRange18To24Users",
        "ageDemographicsAgeRange25To34Users",
        "ageDemographicsAgeRange35PlusUsers",
        "ageDemographicsUnknownAgeUsers",
        "viewTime",
        "averageViewTimePerUser",
        "totalViews",
        "uniqueViewers",
        "uniqueCompleters",
        "completionRate",
        "shares",
        "uniqueSharers",
        "viewersFromShares",
        "screenshots",
        "dropOffRate",
        "topsnapViewTime",
        "topsnapAverageViewTimePerUser",
        "topsnapTotalViews",
        "topsnapUniqueViews",
    ]
    start_date = start_date or datetime.date.today() - datetime.timedelta(days=7)
    end_date = datetime.date.today()

    df = common_quintly.quintly.run_query(
        profile_ids,
        table,
        fields,
        start_date,
        end_date,
    )

    df = df.replace({np.nan: None})

    return df
