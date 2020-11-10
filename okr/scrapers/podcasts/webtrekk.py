import datetime as dt
from typing import Optional
import re

from ..common.webtrekk import Webtrekk


def cleaned_webtrekk_audio_data(date: Optional[dt.date] = None):
    # get report for date
    webtrekk = Webtrekk()

    with webtrekk.session():
        report_data = webtrekk.get_report_data(
            "audio_daily_export_newslab", start_date=date
        )

    # clean report data zmdb:
    data = report_data["analyses"][0]
    date_start = data["timeStart"]
    date_end = data["timeStop"]
    print(f"Start scraping Webtrekk Data between {date_start} and {date_end}.")
    # loop over episodes
    head = data["analysisTabHead"]
    data_dict = {}
    for element in data["analysisData"]:
        match = re.match(r".*?mdb-(\d+)(_AMP)?$", element[0])

        if not match:
            continue

        zmdb_id = int(match.group(1))

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
