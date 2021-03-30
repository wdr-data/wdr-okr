"""Set up Google service account credentials and required services.
Requires a ``google-credentials.json`` file in the root directory.
"""

from datetime import date

from loguru import logger
from apiclient.discovery import build
from google.oauth2 import service_account

KEY_PATH = "google-credentials.json"

try:
    credentials = service_account.Credentials.from_service_account_file(
        KEY_PATH,
        scopes=["https://www.googleapis.com/auth/webmasters"],
    )

except FileNotFoundError:
    logger.warning("Service account file not found, GSC-related scrapers will fail")
    webmasters_service = None

else:
    webmasters_service = build("webmasters", "v3", credentials=credentials)
