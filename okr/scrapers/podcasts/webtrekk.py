"""Retrieve and process data from Webtrekk API."""

import datetime as dt
from typing import Dict
import re

from ..common.webtrekk import Webtrekk
from ..common.webtrekk.types import (
    AnalysisConfig,
    AnalysisObject,
    Filter,
    FilterRule,
    Metric,
)


def cleaned_webtrekk_audio_data(date: dt.date) -> Dict:
    """Retrieve and process data from Webtrekk API for a specific date.

    Args:
        date (dt.date): Date to request data for.

    Returns:
        Dict: Reply from API.
    """

    config = AnalysisConfig(
        [
            AnalysisObject("Medien"),
        ],
        metrics=[
            Metric(
                "Medienansichten",
                sort_order="desc",
            ),
            Metric(
                "Medienansichten vollständig",
            ),
            Metric(
                "Spieldauer",
            ),
        ],
        analysis_filter=Filter(
            filter_rules=[
                FilterRule("Medien", "=", "*audio*"),
                FilterRule("Medien", "!=", "*Livestream*", link="and"),
            ],
        ),
        start_time=date,
        stop_time=date,
        row_limit=10000,
    )

    webtrekk = Webtrekk()

    with webtrekk.session():
        analysis = webtrekk.get_analysis_data(dict(config))

    data = analysis["analysisData"]
    date_start = analysis["timeStart"]
    date_end = analysis["timeStop"]
    print(f"Start scraping Webtrekk Data between {date_start} and {date_end}.")

    # Loop over episodes
    data_dict = {}
    for element in data:

        # Find ZMDB ID
        match = re.match(r".*?mdb-(\d+)(_AMP)?$", element[0])

        if not match:
            continue

        zmdb_id = int(match.group(1))

        # Process data
        item = {
            "media_views": int(element[1]),
            "media_views_complete": int(element[2]),
            "playing_time": dt.timedelta(seconds=int(element[3])),
        }

        if zmdb_id in data_dict:
            data_dict[zmdb_id]["media_views"] += item["media_views"]
            data_dict[zmdb_id]["media_views_complete"] += item["media_views_complete"]
            data_dict[zmdb_id]["playing_time"] += item["playing_time"]
        else:
            data_dict[zmdb_id] = item

    return data_dict


def cleaned_webtrekk_picker_data(date: dt.date) -> Dict:
    """

    Args:
        date (dt.date): Date to request data for.

    Returns:
        Dict: Reply from API.
    """

    config = AnalysisConfig(
        [
            AnalysisObject("CG3"),
        ],
        metrics=[
            Metric(
                "Visits",
                sort_order="desc",
            ),
            Metric(
                "Visits",
                metric_filter=FilterRule("Werbemittel", "=", "*"),
            ),
            Metric(
                "Ausstiege",
            ),
        ],
        analysis_filter=Filter(
            filter_rules=[
                FilterRule("CG2", "=", "Podcast-Picker WDR"),
            ],
        ),
        start_time=date,
        stop_time=date,
        row_limit=100,
    )

    webtrekk = Webtrekk()

    with webtrekk.session():
        analysis = webtrekk.get_analysis_data(dict(config))

    data = analysis["analysisData"]
    date_start = analysis["timeStart"]
    date_end = analysis["timeStop"]
    print(f"Start scraping Webtrekk Data between {date_start} and {date_end}.")

    # Loop over episodes
    data_dict = {}
    for element in data:
        print(element)

    return data_dict
