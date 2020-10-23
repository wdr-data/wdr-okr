import datetime as dt
from typing import List

import pytz

BERLIN = pytz.timezone("Europe/Berlin")
UTC = pytz.UTC


def local_today() -> dt.date:
    return dt.datetime.now(BERLIN).date()


def local_yesterday() -> dt.date:
    return local_today() - dt.timedelta(days=1)


def date_range(start: dt.date, end: dt.date) -> List[dt.date]:
    """
    start and end are both inclusive
    """
    delta = (end - start).days
    return [start + dt.timedelta(days=delta_days) for delta_days in range(delta + 1)]
