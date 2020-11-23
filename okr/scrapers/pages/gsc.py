"""
Collect and clean up data from the Google Search Console API.
"""

import datetime as dt
from typing import Any, Dict, List, Literal, Optional, Union

from ..common.google import webmasters_service
from ...models import Property

Dimension = Literal["page", "device", "date", "query", "country", "searchAppearance"]


def fetch_day(
    property: Property, date: dt.date, *, dimensions: Optional[List[Dimension]] = None
) -> List[Dict[str, Any]]:
    if dimensions is None:
        dimensions = [
            "page",
            "device",
        ]

    request = {
        "startDate": date.isoformat(),
        "endDate": date.isoformat(),
        "dimensions": dimensions,
        "rowLimit": 25000,
        "startRow": 0,
    }

    response = (
        webmasters_service.searchanalytics()
        .query(siteUrl=property.url, body=request)
        .execute()
    )

    return response.get("rows", [])