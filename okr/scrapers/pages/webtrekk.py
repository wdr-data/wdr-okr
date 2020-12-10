"""Retrieve and process data from Webtrekk API."""

import datetime as dt
from typing import Dict, Optional
import re
import html

from rfc3986 import urlparse

from ..common.webtrekk import Webtrekk


def cleaned_webtrekk_page_data(date: Optional[dt.date] = None) -> Dict:
    """Retrieve and process data from Webtrekk API for a specific date.

    Args:
        date (Optional[dt.date], optional): Date to request data for. Defaults
          to None.

    Returns:
        Dict: Reply from API.
    """
    webtrekk = Webtrekk()

    with webtrekk.session():
        report_data = webtrekk.get_report_data(
            "url_seiten_daily_export_newslab", start_date=date
        )

    data = report_data["analyses"][0]
    data_search = report_data["analyses"][1]
    date_start = data["timeStart"]
    date_end = data["timeStop"]
    print(
        f"Start scraping Webtrekk Data for pages between {date_start} and {date_end}."
    )

    data_dict = {}
    for element in data["analysisData"]:
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

    for element in data_search["analysisData"]:
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
    get_parameters = parsed.query
    url = parsed.copy_with(query=None, fragment=None).unsplit()

    # parse headline
    headline_raw = html.unescape(element[1].split("_")[-1])
    headline = re.sub(r"<.*?>", "", headline_raw)

    return url, headline, get_parameters
