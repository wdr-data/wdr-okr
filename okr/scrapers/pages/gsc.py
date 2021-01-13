"""Collect and clean up data from the Google Search Console API.
"""

import datetime as dt
from typing import Any, Dict, List, Literal, Optional, Union

from ..common.google import webmasters_service
from ...models import Property

Dimension = Literal["page", "device", "date", "query", "country", "searchAppearance"]


def fetch_data(
    property: Property,
    start_date: dt.date,
    *,
    end_date: Optional[dt.date] = None,
    dimensions: Optional[List[Dimension]] = None,
) -> List[Dict[str, Any]]:
    """Query Google Search Console API for data.

    Args:
        property (Property): Property to request data for.
        start_date (dt.date): Earliest day to request information for.
        end_date (Optional[dt.date]): Latest day to request information for. Default to ``None``. Will be set to ``start_date`` if ``None``.
        dimensions (Optional[List[Dimension]], optional): Dimensions to request from
            API. Defaults to ``None``. Will be set to ``["page", "device"]`` if ``None``.

    Returns:
        List[Dict[str, Any]]: Response from API.
    """
    if end_date is None:
        end_date = start_date

    if dimensions is None:
        dimensions = ["page", "device"]

    request = {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "dimensions": dimensions,
        "rowLimit": 25000,
        "startRow": 0,
        "dataState": "all",
    }

    response = (
        webmasters_service.searchanalytics()
        .query(siteUrl=property.url, body=request)
        .execute()
    )

    return response.get("rows", [])
