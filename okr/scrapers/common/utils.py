"""Provides helper functions for dates."""

import datetime as dt
from typing import List

import pytz

BERLIN = pytz.timezone("Europe/Berlin")
UTC = pytz.UTC


def local_now() -> dt.datetime:
    """Generate current datetime (Berlin time zone).

    Returns:
        dt.datetime: Current datetime.
    """
    return dt.datetime.now(tz=BERLIN)


def local_today() -> dt.date:
    """Generate current date (Berlin time zone).

    Returns:
        dt.date: Today's date.
    """
    return dt.datetime.now(BERLIN).date()


def local_yesterday() -> dt.date:
    """Generate yesterday's date (Berlin time zone).

    Returns:
        dt.date: Yesterday's date.
    """
    return local_today() - dt.timedelta(days=1)


def date_range(start: dt.date, end: dt.date) -> List[dt.date]:
    """Generate a list of dates within a range. Start and end are both
    inclusive.

    Args:
        start (dt.date): Start date for range.
        end (dt.date): End date for range.

    Returns:
        List[dt.date]: List of dates between start and end.
    """

    delta = (end - start).days
    return [start + dt.timedelta(days=delta_days) for delta_days in range(delta + 1)]
