"""Basic functions to connect to Quintly API."""

import os
import functools
from typing import Callable, Optional

from analytics.quintly import QuintlyAPI


quintly = None


def requires_quintly(func: Callable) -> Callable:
    """Decorator function to set up Quintly API.

    Args:
        func (Callable): Function to set up Quintly access for.

    Returns:
        Callable: Wrapper function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global quintly
        if not quintly:
            quintly = QuintlyAPI(
                os.environ.get("QUINTLY_CLIENT_ID"),
                os.environ.get("QUINTLY_CLIENT_SECRET"),
            )
        return func(*args, **kwargs)

    return wrapper


def parse_bool(value: str, default: Optional[bool] = None) -> Optional[bool]:
    """
    Parse bool from some quintly tables being a string with the value "1" or "0"

    Args:
        value (str): The value from the quintly dataframe
        default (Optional[bool]): Default value in case the parsing fails,

    Returns:
        Optional[bool]: The parsed bool, or `default` if parsing unsuccessful.
    """

    try:
        parsed = bool(int(value))
    except (ValueError, TypeError):
        parsed = default

    return parsed
