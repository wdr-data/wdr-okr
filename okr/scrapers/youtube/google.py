""" Methods for scraping YouTube data with Quintly """

import datetime as dt
from typing import Generator, Optional

from google.cloud import bigquery
import numpy as np
import pandas as pd

from ..common import utils
from ..common.google import bigquery_client, insert_table_name, iter_results


def get_bigquery_basic(
    bigquery_suffix: str,
    *,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
) -> Generator[pd.Series, None, None]:
    """Read YouTube Video data from BigQuery.

    Args:
        bigquery_suffix (str): BigQuery dataset/table suffix.
        start_date (Optional[dt.date], optional): Date of earliest data to
          request. This date refers to the partition field value, not the date
          of the data itself. Defaults to None. Will be set to 7 days if None.
        end_date (Optional[dt.date], optional): Date of latest data to
          request. This date refers to the partition field value, not the date
          of the data itself. Defaults to None. Will be set to today if None.

    Returns:
        pd.DataFrame: BigQuery response data.
    """

    today = utils.local_today()

    if start_date is None:
        start_date = today - dt.timedelta(days=7)

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
  AND `video_id` IS NOT NULL
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

    def df_cleaner(df: pd.DataFrame) -> pd.DataFrame:
        # Convert to date
        df.date = pd.to_datetime(df.date).dt.date
        return df.replace({np.nan: None})

    yield from iter_results(
        bigquery_client,
        query,
        job_config,
        df_cleaner,
    )


def get_bigquery_traffic_source(
    bigquery_suffix: str,
    start_date: dt.date,
    *,
    end_date: Optional[dt.date] = None,
) -> Generator[pd.Series, None, None]:
    """Read YouTube Video traffic source data from BigQuery.

    Args:
        bigquery_suffix (str): BigQuery dataset/table suffix.
        start_date (dt.date): Date of earliest data to
          request. This date refers to the partition field value, not the date
          of the data itself.
        end_date (Optional[dt.date], optional): Date of latest data to
          request. This date refers to the partition field value, not the date
          of the data itself. Defaults to None. Will be set to today if None.

    Yields:
        pd.Series: BigQuery response data.
    """

    if end_date is None:
        end_date = utils.local_today()

    query = """
SELECT
  `video_id`,
  `traffic_source_type`,
  SUM(`views`) AS `views`,
  SUM(`watch_time_minutes`) AS `watch_time_minutes`
FROM
  `@table_name`
WHERE
  DATE(_PARTITIONTIME) >= @start_date
  AND DATE(_PARTITIONTIME) <= @end_date
  AND `video_id` IS NOT NULL
GROUP BY
  `video_id`,
  `traffic_source_type`
    """.strip()

    query = insert_table_name(query, "p_channel_traffic_source_a2_", bigquery_suffix)

    job_config = bigquery.QueryJobConfig(
        default_dataset=f"wdr-okr.youtube_channel_{bigquery_suffix}",
        query_parameters=[
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date.isoformat()),
            bigquery.ScalarQueryParameter("end_date", "DATE", end_date.isoformat()),
        ],
    )

    def df_cleaner(df: pd.DataFrame) -> pd.DataFrame:
        return df.replace({np.nan: None})

    yield from iter_results(
        bigquery_client,
        query,
        job_config,
        df_cleaner,
    )


def get_bigquery_search_terms(
    bigquery_suffix: str,
    start_date: dt.date,
    *,
    end_date: Optional[dt.date] = None,
) -> Generator[pd.Series, None, None]:
    """Read YouTube Video search term data from BigQuery.

    Args:
        bigquery_suffix (str): BigQuery dataset/table suffix.
        start_date (dt.date): Date of earliest data to
          request. This date refers to the partition field value, not the date
          of the data itself.
        end_date (Optional[dt.date], optional): Date of latest data to
          request. This date refers to the partition field value, not the date
          of the data itself. Defaults to None. Will be set to today if None.

    Yields:
        pd.Series: BigQuery response data.
    """

    if end_date is None:
        end_date = utils.local_today()

    query = """
SELECT
  `video_id`,
  `traffic_source_detail`,
  SUM(`views`) AS `views`,
  SUM(`watch_time_minutes`) AS `watch_time_minutes`
FROM
  `@table_name`
WHERE
  DATE(_PARTITIONTIME) >= @start_date
  AND DATE(_PARTITIONTIME) <= @end_date
  AND `traffic_source_type` = 5
  AND `traffic_source_detail` IS NOT NULL
  AND `video_id` IS NOT NULL
GROUP BY
  `video_id`,
  `traffic_source_detail`
    """.strip()

    query = insert_table_name(query, "p_channel_traffic_source_a2_", bigquery_suffix)

    job_config = bigquery.QueryJobConfig(
        default_dataset=f"wdr-okr.youtube_channel_{bigquery_suffix}",
        query_parameters=[
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date.isoformat()),
            bigquery.ScalarQueryParameter("end_date", "DATE", end_date.isoformat()),
        ],
    )

    def df_cleaner(df: pd.DataFrame) -> pd.DataFrame:
        return df.replace({np.nan: None})

    yield from iter_results(
        bigquery_client,
        query,
        job_config,
        df_cleaner,
    )


def get_bigquery_external_traffic(
    bigquery_suffix: str,
    start_date: dt.date,
    *,
    end_date: Optional[dt.date] = None,
) -> Generator[pd.Series, None, None]:
    """Read YouTube Video external traffic data from BigQuery.

    Args:
        bigquery_suffix (str): BigQuery dataset/table suffix.
        start_date (dt.date): Date of earliest data to
          request. This date refers to the partition field value, not the date
          of the data itself.
        end_date (Optional[dt.date], optional): Date of latest data to
          request. This date refers to the partition field value, not the date
          of the data itself. Defaults to None. Will be set to today if None.

    Yields:
        pd.Series: BigQuery response data.
    """

    if end_date is None:
        end_date = utils.local_today()

    query = """
SELECT
  `video_id`,
  `traffic_source_detail`,
  SUM(`views`) AS `views`,
  SUM(`watch_time_minutes`) AS `watch_time_minutes`
FROM
  `@table_name`
WHERE
  DATE(_PARTITIONTIME) >= @start_date
  AND DATE(_PARTITIONTIME) <= @end_date
  AND `traffic_source_type` = 9
  AND `traffic_source_detail` IS NOT NULL
  AND `video_id` IS NOT NULL
GROUP BY
  `video_id`,
  `traffic_source_detail`
    """.strip()

    query = insert_table_name(query, "p_channel_traffic_source_a2_", bigquery_suffix)

    job_config = bigquery.QueryJobConfig(
        default_dataset=f"wdr-okr.youtube_channel_{bigquery_suffix}",
        query_parameters=[
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date.isoformat()),
            bigquery.ScalarQueryParameter("end_date", "DATE", end_date.isoformat()),
        ],
    )

    def df_cleaner(df: pd.DataFrame) -> pd.DataFrame:
        return df.replace({np.nan: None})

    yield from iter_results(
        bigquery_client,
        query,
        job_config,
        df_cleaner,
    )


def get_bigquery_video_demographics(
    bigquery_suffix: str,
    start_date: dt.date,
    *,
    end_date: Optional[dt.date] = None,
) -> Generator[pd.Series, None, None]:
    """Read YouTube Video demographics data from BigQuery.

    Args:
        bigquery_suffix (str): BigQuery dataset/table suffix.
        start_date (dt.date): Date of earliest data to
          request. This date refers to the partition field value, not the date
          of the data itself.
        end_date (Optional[dt.date], optional): Date of latest data to
          request. This date refers to the partition field value, not the date
          of the data itself. Defaults to None. Will be set to today if None.

    Yields:
        pd.Series: BigQuery response data.
    """

    if end_date is None:
        end_date = utils.local_today()

    query = """
SELECT
  `video_id`,
  `age_group`,
  `gender`,
  SUM(`views`) / MAX(`total_video_views`) * 100 AS `views_percentage`,
FROM (
  SELECT
    `demo`.`date`,
    `demo`.`video_id`,
    `age_group`,
    `gender`,
    `views_percentage`,
    `views` AS `views_day_total`,
    `views` * `views_percentage` / 100 AS `views`,
    `total_video_views`
  FROM (
    SELECT
      `date`,
      `video_id`,
      `age_group`,
      `gender`,
      SUM(`views_percentage`) AS `views_percentage`
    FROM
      `@table_name_demo`
    WHERE
      DATE(_PARTITIONTIME) >= @start_date
      AND DATE(_PARTITIONTIME) <= @end_date
      AND `video_id` IS NOT NULL
    GROUP BY
      `date`,
      `video_id`,
      `age_group`,
      `gender` ) `demo`
  LEFT JOIN (
    SELECT
      `date`,
      `video_id`,
      SUM(`views`) AS `views`
    FROM
      `@table_name_basic`
    WHERE
      DATE(_PARTITIONTIME) >= @start_date
      AND DATE(_PARTITIONTIME) <= @end_date
      AND `video_id` IS NOT NULL
    GROUP BY
      `date`,
      `video_id` ) `basic`
  ON
    `basic`.`date` = `demo`.`date`
    AND `basic`.`video_id` = `demo`.`video_id`

  -- Stupid but works
  -- We need the total video views that influence the calculation
  -- We join the basic table into the demographics table to drop
  -- dates where no demographics data is available.
  LEFT JOIN (
    SELECT
      `demo`.`video_id`,
      SUM(`views`) AS `total_video_views`
    FROM (
      SELECT
        `date`,
        `video_id`
      FROM
        `@table_name_demo`
      WHERE
        DATE(_PARTITIONTIME) >= @start_date
        AND DATE(_PARTITIONTIME) <= @end_date
        AND `video_id` IS NOT NULL
      GROUP BY
        `date`,
        `video_id` ) `demo`
    LEFT JOIN (
      SELECT
        `date`,
        `video_id`,
        SUM(`views`) AS `views`
      FROM
        `@table_name_basic`
      WHERE
        DATE(_PARTITIONTIME) >= @start_date
        AND DATE(_PARTITIONTIME) <= @end_date
        AND `video_id` IS NOT NULL
      GROUP BY
        `date`,
        `video_id` ) `basic`
    ON
      `basic`.`date` = `demo`.`date`
      AND `basic`.`video_id` = `demo`.`video_id`
    GROUP BY
      `demo`.`video_id` ) `total`
  ON
    `total`.`video_id` = `demo`.`video_id`
    )

GROUP BY
  `video_id`,
  `age_group`,
  `gender`
ORDER BY
  `video_id`,
  `gender`,
  `age_group`;
    """.strip()

    query = insert_table_name(
        query,
        "p_channel_demographics_a1_",
        bigquery_suffix,
        placeholder="@table_name_demo",
    )
    query = insert_table_name(
        query,
        "p_channel_basic_a2_",
        bigquery_suffix,
        placeholder="@table_name_basic",
    )

    job_config = bigquery.QueryJobConfig(
        default_dataset=f"wdr-okr.youtube_channel_{bigquery_suffix}",
        query_parameters=[
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date.isoformat()),
            bigquery.ScalarQueryParameter("end_date", "DATE", end_date.isoformat()),
        ],
    )

    def df_cleaner(df: pd.DataFrame) -> pd.DataFrame:
        return df.replace({np.nan: None})

    yield from iter_results(
        bigquery_client,
        query,
        job_config,
        df_cleaner,
    )
