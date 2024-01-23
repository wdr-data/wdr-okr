"""Collect page data from the Sophora API."""

import os
from typing import Dict, Generator, Optional, Union
import datetime as dt

from loguru import logger
import requests
from solrq import Q, Range
from rfc3986 import urlparse
from pytz import UTC

from ...models.pages import SophoraNode
from ..common.types import JSON

SOPHORA_API_BASE = os.environ.get("SOPHORA_API_BASE")


def _sophora_api_url(*path: str) -> str:
    return f"{SOPHORA_API_BASE}{'/'.join(path)}"


def get_document_by_sophora_id(sophora_id: str) -> JSON:
    """Read data about page with sophora_id from Sophora API.

    Args:
        sophora_id (str): Sophora ID to request data for.

    Returns:
        dict: JSON dict of response data.
    """
    url = _sophora_api_url("getDocumentBySophoraId", sophora_id)

    response = requests.get(url)
    response.raise_for_status()

    return response.json()


def get_documents_in_node(
    node: SophoraNode,
    *,
    document_type: Optional[str] = None,
    sort_field: Optional[str] = "modificationDate_dt",
    sort_order: Optional[str] = "desc",
    max_age: Union[dt.timedelta, dt.datetime, None] = None,
    force_exact: bool = False,
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

    params = {
        "structureNodePath": node_str,
    }

    if document_type is not None:
        params["documentType"] = document_type

    if sort_field is not None:
        params["sortField"] = sort_field

    if sort_order is not None:
        params["sortOrder"] = sort_order

    if max_age is not None:
        if isinstance(max_age, dt.timedelta) and max_age.total_seconds() > 0:
            max_age = -max_age
        elif isinstance(max_age, dt.datetime):
            max_age = max_age.astimezone(UTC)

        # Encode filter query with solrq
        params["filterQueries"] = Q(modificationDate_dt=Range(max_age, dt.timedelta()))

    url = _sophora_api_url(
        "getDocumentsByStructureNodePath",
        "EXACT" if use_exact else "STARTS",
        "1",
        "20",
    )
    logger.info("Paging through URL {}", url)

    while True:
        response = requests.get(url, params=params)
        response.raise_for_status()
        logger.debug(response.request.url)

        response_data = response.json()
        yield from response_data["data"]

        if "moreLink" not in response_data or response_data["moreLink"] is None:
            break
        else:
            url = response_data["moreLink"]["moreUrl"]

            # Remove badly unescaped query from URL
            parsed = urlparse(url)
            url = parsed.copy_with(query=None, fragment=None).unsplit()
