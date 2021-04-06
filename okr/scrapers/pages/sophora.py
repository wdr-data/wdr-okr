"""Collect page data from the Sophora API."""

import os
from typing import Dict, Generator, Optional
from loguru import logger

import requests

from ...models.pages import Page, SophoraNode

SOPHORA_API_BASE = os.environ.get("SOPHORA_API_BASE")


def _sophora_api_url(*path: str, params: Optional[Dict[str, str]] = None) -> str:
    qs = ""

    if params is not None:
        qs = "?" + "&".join(f"{key}={val}" for key, val in params.items())

    return f"{SOPHORA_API_BASE}{'/'.join(path)}{qs}"


def get_page(page: Page) -> dict:
    """Read data about page from Sophora API.

    Args:
        page (Page): Page to request data for.

    Returns:
        dict: JSON dict of response data.
    """
    url = _sophora_api_url("getDocumentBySophoraId", page.sophora_id)
    return requests.get(url).json()


def get_documents_in_node(
    node: SophoraNode,
    *,
    force_exact=False,
) -> Generator[Dict, None, None]:
    """Request all Sophora documents in a specific node.

    Args:
        node (SophoraNode): Sohopra node to request data for
        force_exact (bool, optional): If true, forces ``EXACT`` matching type instead of
            ``STARTS`` for the sophora node, even if ``node.use_exact_search`` is ``False``.
            Defaults to False.

    Yields:
        Generator[Dict, None, None]: The parsed JSON of individual Sophora documents as retrieved from the API.
    """
    node_str = node.node
    use_exact = force_exact or node.use_exact_search

    if not use_exact:
        node_str = node_str + "/"

    url = _sophora_api_url(
        "getDocumentsByStructureNodePath",
        "EXACT" if use_exact else "STARTS",
        "1",
        "20",
        params={
            "structureNodePath": node_str,
        },
    )
    logger.info("Paging through URL {}", url)

    while True:
        response = requests.get(url).json()
        yield from response["data"]

        if response["moreLink"] is None:
            break
        else:
            url = response["more"]
