"""Set up Google service account credentials and required services.
Requires the ``GOOGLE_SERVICE_ACCOUNT`` environment variable to be set.
"""

import json
import os
import re
from typing import Callable, Generator

from loguru import logger
import pandas as pd
from apiclient.discovery import build
from google.cloud import bigquery
from google.cloud.bigquery.job.query import QueryJobConfig
from google.oauth2 import service_account

try:
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"]),
        scopes=[
            "https://www.googleapis.com/auth/webmasters",
            "https://www.googleapis.com/auth/cloud-platform",
        ],
    )

except KeyError:
    logger.warning(
        "Service account info not found in environment, GSC/BigQuery-related scrapers will fail"
    )
    searchconsole_service = None
    bigquery_client = None

except json.JSONDecodeError:
    logger.warning(
        "Failed to parse service account info, GSC/BigQuery-related scrapers will fail"
    )
    searchconsole_service = None
    bigquery_client = None

else:
    searchconsole_service = build("searchconsole", "v1", credentials=credentials)
    bigquery_client = bigquery.Client(
        credentials=credentials,
        project=credentials.project_id,
    )


def insert_table_name(
    query: str,
    table_prefix: str,
    table_suffix: str,
    placeholder: str = "@table_name",
) -> str:
    """
    Replace @table_name with the actual table name
    BigQuery doesn't support parameterized table names :(
    Sanitizes the suffix, lol

    Args:
        query (str): The query to insert the table name into
        table_prefix (str): The table prefix
        table_suffix (str): The table suffix
        placeholder (str): The placeholder to replace
    """
    table_suffix = re.sub(r"[^a-zA-Z0-9_]", "", table_suffix)
    return query.replace(placeholder, f"{table_prefix}{table_suffix}")


def iter_results(
    bigquery_client: bigquery.Client,
    query: str,
    job_config: QueryJobConfig,
    df_cleaner: Callable[[pd.DataFrame], pd.DataFrame] = None,
) -> Generator[pd.Series, None, None]:
    """
    Page through the results of a query and yield each row as a pandas Series

    Args:
        bigquery_client (bigquery.Client): The BigQuery client
        query (str): The query to run
        job_config (QueryJobConfig): The BigQuery job config

    Returns:
        Generator[pd.Series, None, None]: A generator of pandas Series
    """

    query_job = bigquery_client.query(query, job_config=job_config)
    query_job.result()

    # Get reference to destination table
    destination = bigquery_client.get_table(query_job.destination)

    rows = bigquery_client.list_rows(destination, page_size=10000)

    dfs = rows.to_dataframe_iterable()

    for df in dfs:
        if df_cleaner is not None:
            df = df_cleaner(df)

        for index, row in df.iterrows():
            yield row
