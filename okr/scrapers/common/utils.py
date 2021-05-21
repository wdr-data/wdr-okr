"""Provides helper functions for dates."""

import datetime as dt
from typing import Iterator, List, Optional, TypeVar

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


def date_param(
    date: Optional[dt.date],
    *,
    default: Optional[dt.date] = None,
    earliest: Optional[dt.date] = None,
    latest: Optional[dt.date] = None,
) -> Optional[dt.date]:
    """For when you have an optional date parameter in your function but you want to limit the
    range of dates allowed. Also allows you to set a default.

    Args:
        date (Optional[dt.date]): The date you want to filter.
        default (Optional[dt.date]): Provide a default in case the date is None.
        earliest (Optional[dt.date]): The earliest date you want to allow.
        latest (Optional[dt.date]): The latest date you want to allow.

    Returns:
        Optional[dt.date]: The resulting date, or None if both ``date`` and ``default`` are ``None``.
    """
    if date is None:
        return default

    if earliest:
        date = max(earliest, date)

    if latest:
        date = min(latest, date)

    return date


T = TypeVar("T")


def chunk_list(list_: List[T], chunk_size: int) -> Iterator[List[T]]:
    for i in range(0, len(list_), chunk_size):
        yield list_[i : i + chunk_size]
