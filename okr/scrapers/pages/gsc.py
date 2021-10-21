"""Collect and clean up data from the Google Search Console API."""

import datetime as dt
from typing import Any, Dict, List, Literal, Optional

from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_exponential

from ..common.google import searchconsole_service
from ...models import Property

Dimension = Literal["page", "device", "date", "query", "country", "searchAppearance"]


@retry(wait=wait_exponential(), stop=stop_after_attempt(3))
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
        end_date (Optional[dt.date]): Latest day to request information for. Default to
            ``None``. Will be set to ``start_date`` if ``None``.
        dimensions (Optional[List[Dimension]], optional): Dimensions to request from
            API. Defaults to ``None``. Will be set to ``["page", "device"]`` if
            ``None``.

    Returns:
        List[Dict[str, Any]]: Response from API.
    """
    if end_date is None:
        end_date = start_date

    if dimensions is None:
        dimensions = ["page", "device"]

    results = []
    start_row = 0
    ROW_LIMIT = 25000

    while True:

        request = {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "dimensions": dimensions,
            "rowLimit": ROW_LIMIT,
            "startRow": start_row,
            "dataState": "all",
        }

        response = (
            searchconsole_service.searchanalytics()
            .query(siteUrl=property.url, body=request)
            .execute()
        )

        start_row += ROW_LIMIT

        result = response.get("rows", [])
        results.extend(result)

        if len(result) == 0:
            break

    return results
