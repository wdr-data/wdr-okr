""" Methods for scraping YouTube data with Quintly """

import datetime
from typing import Optional

from google.cloud import bigquery
import numpy as np
import pandas as pd

from ..common import utils
from ..common.google import bigquery_client, insert_table_name


def get_bigquery_basic(
    bigquery_suffix: str,
    *,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
) -> pd.DataFrame:
    """Read YouTube Video data from BigQuery.

    Args:
        bigquery_suffix (str): BigQuery dataset/table suffix.
        start_date (Optional[datetime.date], optional): Date of earliest data to
          request. This date refers to the partition field value, not the date
          of the data itself. Defaults to None. Will be set to 7 days if None.
        end_date (Optional[datetime.date], optional): Date of latest data to
          request. This date refers to the partition field value, not the date
          of the data itself. Defaults to None. Will be set to today if None.

    Returns:
        pd.DataFrame: BigQuery response data.
    """

    today = utils.local_today()

    if start_date is None:
        start_date = today - datetime.timedelta(days=7)

    if end_date is None:
        end_date = today

    query = """
SELECT
  `date`,
  `video_id`,
  `live_or_on_demand`,
  SUM(`views`) AS `views`,
  SUM(`likes`) AS `likes`,
  SUM(`dislikes`) AS `dislikes`,
  SUM(`comments`) AS `comments`,
  SUM(`shares`) AS `shares`,
  SUM(`subscribers_gained`) AS `subscribers_gained`,
  SUM(`subscribers_lost`) AS `subscribers_lost`,
  SUM(`watch_time_minutes`) AS `watch_time_minutes`
FROM
  `@table_name`
WHERE
  DATE(_PARTITIONTIME) >= @start_date
  AND DATE(_PARTITIONTIME) <= @end_date
GROUP BY
  `date`,
  `video_id`,
  `live_or_on_demand`
    """.strip()

    query = insert_table_name(query, "p_channel_basic_a2_", bigquery_suffix)

    job_config = bigquery.QueryJobConfig(
        default_dataset=f"wdr-okr.youtube_channel_{bigquery_suffix}",
        query_parameters=[
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date.isoformat()),
            bigquery.ScalarQueryParameter("end_date", "DATE", end_date.isoformat()),
        ],
    )

    # Run the query
    query_job = bigquery_client.query(query, job_config=job_config)
    df = query_job.to_dataframe()

    # Convert to date
    df.date = pd.to_datetime(df.date).dt.date

    df = df.replace({np.nan: None})

    return df
