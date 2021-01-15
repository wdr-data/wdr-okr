"""Retrieve and process data from Webtrekk API."""

import datetime as dt
from typing import Dict, Optional
import re
import html

from rfc3986 import urlparse

from ..common.webtrekk import Webtrekk
from ..common.webtrekk.types import (
    AnalysisConfig,
    AnalysisObject,
    Filter,
    FilterRule,
    Metric,
)
from okr.scrapers.common.utils import local_yesterday


def cleaned_webtrekk_page_data(date: Optional[dt.date] = None) -> Dict:
    """Retrieve and process data from Webtrekk API for a specific date.

    Args:
        date (Optional[dt.date], optional): Date to request data for. Defaults
            to None.

    Returns:
        Dict: Reply from API.
    """
    date = local_yesterday()
    analysis_objects = [
        AnalysisObject("Seiten-URL"),
        AnalysisObject("Seiten"),
    ]
    metrics = [
        Metric(
            "Visits",
        ),
        Metric(
            "Einstiege",
            sort_order="desc",
        ),
        Metric(
            "Visits (Kampagnen)",
        ),
        Metric(
            "Bounces",
        ),
        Metric(
            "Verweildauer (Sekunden)",
        ),
        Metric(
            "Page Impressions",
        ),
        Metric(
            "Ausstiege",
        ),
    ]

    config_all = AnalysisConfig(
        analysis_objects,
        metrics=metrics,
        analysis_filter=Filter(
            filter_rules=[
                FilterRule("CG2", "=", "Nachrichten"),
            ],
        ),
        start_time=date,
        stop_time=date,
        row_limit=10,
    )
    config_search = AnalysisConfig(
        analysis_objects,
        metrics=metrics,
        analysis_filter=Filter(
            filter_rules=[
                FilterRule("CG2", "=", "Nachrichten"),
                FilterRule("Einstiegsquellen-Typen", "=", "Suchmaschinen", link="and"),
            ],
        ),
        start_time=date,
        stop_time=date,
        row_limit=10,
    )

    webtrekk = Webtrekk()

    with webtrekk.session():
        analysis_all = webtrekk.get_analysis_data(dict(config_all))
        analysis_search = webtrekk.get_analysis_data(dict(config_search))

    data_all = analysis_all["analysisData"]
    data_search = analysis_search["analysisData"]
    date_start = analysis_all["timeStart"]
    date_end = analysis_all["timeStop"]
    print(
        f"Start scraping Webtrekk Data for pages between {date_start} and {date_end}."
    )

    data_dict = {}
    for element in data_all:
        key = _parse_row(element)

        if key is None:
            continue

        item = {
            "visits": int(element[2]),
            "entries": int(element[3]),
            "visits_campaign": int(element[4]),
            "bounces": int(element[5]),
            "length_of_stay": int(element[6]),
            "impressions": int(element[7]),
            "exits": int(element[8]),
        }

        data_dict[key] = item

    for element in data_search:
        key = _parse_row(element)

        if key is None:
            continue

        item = {
            "visits_search": int(element[2]),
            "entries_search": int(element[3]),
            "visits_campaign_search": int(element[4]),
            "bounces_search": int(element[5]),
            "length_of_stay_search": int(element[6]),
            "impressions_search": int(element[7]),
            "exits_search": int(element[8]),
        }

        if key in data_dict:
            data_dict[key].update(item)
        else:
            data_dict[key] = item

    return data_dict


def _parse_row(element):
    if element[1] == "-":
        return None

    parsed = urlparse(element[0])
    # check if url part of property
    if not parsed.host.endswith("wdr.de") or not parsed.path.startswith("/nachrichten"):
        return None

    # get cononical url and get_parameters
    query = parsed.query
    url = parsed.copy_with(query=None, fragment=None).unsplit()

    # parse headline
    headline_raw = html.unescape(element[1].split("_")[-1])
    headline = re.sub(r"<.*?>", "", headline_raw)

    return url, headline, query
