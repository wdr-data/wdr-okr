"""Basic functions to connect to Quintly API."""

import os
import functools
from typing import Callable

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
