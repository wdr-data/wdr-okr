"""Wrapper for Spotify APIs (using the spotipy library)."""

import os
from typing import Dict, List, Iterator, Literal, TypeVar, Union
import datetime as dt
from enum import Enum
from time import sleep
from typing import Callable, Optional
import logging
from loguru import logger

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
from requests.exceptions import ReadTimeout

from ..common.utils import local_yesterday
from ..common import types

LICENSOR_ID = os.environ.get("SPOTIFY_LICENSOR_ID")

# "followers" is omitted here since we have a special function for that
AggregationType = Literal["starts", "streams", "listeners"]


class SpotipyFilter(logging.Filter):
    """Filter to check reply message for errors."""

    def filter(self, record) -> bool:
        """Check reply message for errors (True/False).

        Args:
            record: Record to check.

        Returns:
            bool: True if no error detected, False if error detected.
        """
        return not record.getMessage().endswith("returned 404 due to error")


spotipy.client.logger.addFilter(SpotipyFilter())


class CustomSpotify(spotipy.Spotify):
    """Custom class based on spotipy.Spotify."""

    class Precision(Enum):
        """Degrees of precision for API requests."""

        YEAR = 1
        MONTH = 2
        DAY = 3
        HOUR = 4

    def _auth_headers(self):
        headers = super()._auth_headers()
        headers["Accept"] = "application/json"
        return headers

    def _internal_call(self, method, url, payload, params):
        error = None
        retries = 3

        for i in range(retries):
            try:
                result = super()._internal_call(method, url, payload, params)
                return result

            except ReadTimeout as e:
                error = e
                spotipy.client.logger.info(
                    f"Got ReadTimeoutError, attempt {i + 1}/{retries}"
                )
                sleep(10 * (i + 1))

            except SpotifyException as e:
                if e.http_status != 429:
                    raise

                error = e
                spotipy.client.logger.info(f"Got RetryError, attempt {i + 1}/{retries}")
                sleep(10 * (i + 1))

        raise error

    def podcast_api(
        self,
        path: str,
        *,
        payload: Optional[types.JSON] = None,
        **kwargs,
    ) -> Dict:
        """Base method to read data from Spotify Podcaster API.

        Args:
            path (str): path to request data from.
            payload (Optional[types.JSON], optional): Additional payload
              for API request. Must be a str if a Content-Type is specified,
              otherwise anything json-serializable. Defaults to None.

        Returns:
            Dict: Results from API.
        """
        if path.startswith("/"):
            path = path[1:]

        url = "https://generic.wg.spotify.com/podcasters-analytics-api/" + path
        return self._internal_call("GET", url, payload, kwargs)

    def licensed_podcasts(self) -> Dict:
        """Get a list of all licensed podcasts.

        Returns:
            Dict: Results from API.
        """
        return self.podcast_api(f"licensors/{LICENSOR_ID}/podcasts")

    def podcast_data(
        self,
        podcast_id: str,
        agg_type: AggregationType,
        date: Union[dt.date, dt.datetime],
        *,
        precision: Precision = Precision.DAY,
    ) -> dict:
        """Read data from Spotify Podcaster API.

        Args:
            podcast_id (str): Podcast ID.
            agg_type (AggregationType): Aggregation type.
            date (Union[dt.date, dt.datetime]): Date to request data for.
            precision (Precision, optional): Degree of precision. Defaults to
              Precision.DAY.

        Returns:
            dict: Results from API.
        """
        path_components = [date.year, date.month, date.day]

        if isinstance(date, dt.datetime):
            path_components.append(date.hour)

        sub_path = "/".join(map(str, path_components[: precision.value]))
        return self.podcast_api(
            f"licensors/{LICENSOR_ID}/podcasts/{podcast_id}/{agg_type}/{sub_path}/total"
        )["aggregation"][agg_type]["counts"]

    def podcast_data_date_range(
        self,
        podcast_id: str,
        agg_type: AggregationType,
        *,
        start: Optional[dt.date] = None,
        end: Optional[dt.date] = None,
    ) -> dict:
        """Read data from Spotify Podcaster API for specific period of time.

        Args:
            podcast_id (str): Podcast ID.
            agg_type (AggregationType): Aggregation type.
            start (Optional[dt.date], optional): Earliest date to request data for.
              Defaults to None. Will be set to 01/01/2016 if None.
            end (Optional[dt.date], optional): Latest date to request data for.
              Defaults to None. Will be set to yesterday's date if None.

        Returns:
            dict: Results from API.
        """
        if start is None:
            start = dt.date(2016, 1, 1)
        if end is None:
            end = local_yesterday()

        return self.podcast_api(
            f"licensors/{LICENSOR_ID}/podcasts/{podcast_id}/{agg_type}/total",
            start=start.isoformat(),
            end=end.isoformat(),
        )["aggregation"][agg_type]["counts"]

    def podcast_followers(self, podcast_id: str) -> dict:
        """Read followers data from Spotify Podcaster API.

        Args:
            podcast_id (str): Podcast ID.

        Returns:
            dict: Results from API.
        """
        return self.podcast_api(
            f"licensors/{LICENSOR_ID}/podcasts/{podcast_id}/followers/total",
        )["aggregation"]["followers"]["counts"]

    def podcast_episodes(self, podcast_id: str) -> dict:
        """Get a list of episodes of a specific podcast from Spotify Podcaster API.

        Args:
            podcast_id (str): Podcast ID.

        Returns:
            dict: Results from API.
        """
        return self.podcast_api(
            f"licensors/{LICENSOR_ID}/podcasts/{podcast_id}/episodes",
        )

    def podcast_episode_meta(self, podcast_id: str, episode_id: str) -> dict:
        """Read meta data for specific episode from Spotify Podcaster API.

        Args:
            podcast_id (str): Podcast ID.
            episode_id (str): Episode ID.

        Returns:
            dict: Results from API.
        """
        return self.podcast_api(
            f"licensors/{LICENSOR_ID}/podcasts/{podcast_id}/episodes/{episode_id}/metadata",
        )

    def podcast_episode_data(
        self,
        podcast_id: str,
        episode_id: str,
        agg_type: AggregationType,
        date: dt.date,
    ) -> dict:
        """Read data for specific episode on specific date from Spotify Podcaster API.

        Args:
            podcast_id (str): Podcast ID.
            episode_id (str): Episode ID.
            agg_type (AggregationType): Aggregation type.
            date (dt.date): Date to request data for.

        Returns:
            dict: Results from API.
        """
        return self.podcast_api(
            f"licensors/{LICENSOR_ID}/podcasts/{podcast_id}/episodes/{episode_id}/{agg_type}/{date.year}/{date.month}/{date.day}/total",
        )["aggregation"][agg_type]["counts"]

    def podcast_episode_data_all_time(
        self,
        podcast_id: str,
        episode_id: str,
        agg_type: AggregationType,
        end: Optional[dt.date] = None,
    ) -> dict:
        """Read long-term data for specific episode from Spotify Podcaster API.

        Args:
            podcast_id (str): Podcast ID.
            episode_id (str): Episode ID.
            agg_type (AggregationType): Aggregation type.
            end (Optional[dt.date], optional): Latest date to include in request.
              Defaults to None. Will be set to yesterday's date if None.

        Returns:
            dict:  Results from API.
        """
        if end is None:
            end = local_yesterday()

        return self.podcast_api(
            f"licensors/{LICENSOR_ID}/podcasts/{podcast_id}/episodes/{episode_id}/{agg_type}/total",
            start="2016-01-01",
            end=end.isoformat(),
        )["aggregation"][agg_type]["counts"]


T = TypeVar("T")


def _divide_chunks(list_: List[T], n: int) -> Iterator[List[T]]:
    # looping till length l
    for i in range(0, len(list_), n):
        yield list_[i : i + n]


def fetch_all(
    fn: Callable,
    ids: List[str],
    result_key: str,
    chunk_size: int = 50,
) -> List[Dict]:
    """Split up larger API requests into chunks.

    Args:
        fn (Callable): Function to use for data request.
        ids (List[str]): IDs to split up into chunks and request data for.
        result_key (str): Result key results dict.
        chunk_size (int, optional): Size of chunks to divide the request into. Defaults
            to 50.

    Returns:
        List[Dict]: List of dicts containing API response.
    """
    agg = []
    for chunk in _divide_chunks(ids, chunk_size):
        result = fn(chunk)
        agg.extend(result[result_key])
    return agg


try:
    auth_manager = SpotifyClientCredentials()
    spotify_api = CustomSpotify(auth_manager=auth_manager)
except spotipy.oauth2.SpotifyOauthError:
    logger.warning("Missing Spotipy credentials! Spotify-related scrapers will fail.")
    spotify_api = None
