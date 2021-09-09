"""Set up Google service account credentials and required services.
Requires a ``google-credentials.json`` file in the root directory.
"""
import re

from loguru import logger
from apiclient.discovery import build
from google.cloud import bigquery
from google.oauth2 import service_account

KEY_PATH = "google-credentials.json"

try:
    credentials = service_account.Credentials.from_service_account_file(
        KEY_PATH,
        scopes=[
            "https://www.googleapis.com/auth/webmasters",
            "https://www.googleapis.com/auth/cloud-platform",
        ],
    )

except FileNotFoundError:
    logger.warning(
        "Service account file not found, GSC/BigQuery-related scrapers will fail"
    )
    webmasters_service = None
    bigquery_client = None

else:
    webmasters_service = build("webmasters", "v3", credentials=credentials)
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
