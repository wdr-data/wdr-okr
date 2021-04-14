"""Retrieve and process data from Webtrekk API."""

import datetime as dt
from typing import Dict
import re

from loguru import logger

from ..common.webtrekk import Webtrekk
from ..common.webtrekk.types import (
    AnalysisConfig,
    AnalysisObject,
    Filter,
    FilterRule,
    Metric,
)


def cleaned_audio_data(date: dt.date) -> Dict:
    """Retrieve and process data about audio playbacks
    from Webtrekk API for a specific date.

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
    logger.info("Start scraping Webtrekk Data between {} and {}.", date_start, date_end)

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


def cleaned_picker_data(date: dt.date) -> Dict:
    """Retrieve and process data about Podcast Picker visits
    from Webtrekk API for a specific date.

    Args:
        date (dt.date): Date to request data for.

    Returns:
        Dict: Reply from API.
    """

    config = AnalysisConfig(
        [
            AnalysisObject("Seiten"),
        ],
        metrics=[
            Metric(
                "Visits",
                sort_order="desc",
            ),
            Metric(
                "Visits",
                metric_filter=Filter(
                    filter_rules=[
                        FilterRule("Werbemittel", "=", "*"),
                    ]
                ),
            ),
            Metric(
                "Ausstiege",
            ),
        ],
        analysis_filter=Filter(
            filter_rules=[
                FilterRule("Seiten", "=", "*Podcast-Picker*"),
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
    logger.info("Start scraping Webtrekk Data between {} and {}.", date_start, date_end)

    data_dict = {}
    for element in data[:-1]:
        name = normalize_name(element[0].split("_")[-1])

        item = dict(
            visits=int(element[1]),
            visits_campaign=int(element[2]),
            exits=int(element[3]),
        )

        if name in data_dict:
            data_dict[name]["visits"] += item["visits"]
            data_dict[name]["visits_campaign"] += item["visits_campaign"]
            data_dict[name]["exits"] += item["exits"]
        else:
            data_dict[name] = item

    return data_dict


def normalize_name(s: str) -> str:
    """Strong normalization for podcast names as they seem to have slight
    variations in the Webtrekk data. Lowers string and removes all characters
    except alphanumerics.

    Args:
        s (str): The string to normalize

    Returns:
        str: The normalized string
    """
    s = s.lower()
    s = "".join(re.findall(r"[\d\w]", s))

    return s
