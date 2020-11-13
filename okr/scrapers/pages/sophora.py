"""
Collect page data from the Sophora API
"""
import os

import requests

from ...models.pages import Page

SOPHORA_API_BASE = os.environ.get("SOPHORA_API_BASE")


def _sophora_api_url(*path: str) -> str:
    return f"{SOPHORA_API_BASE}{'/'.join(path)}"


def get_page(page: Page) -> dict:
    url = _sophora_api_url("getDocumentBySophoraId", page.sophora_id)
    return requests.get(url).json()
