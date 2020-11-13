""" Wrapper for Spotify APIs (using the spotipy library)
"""

import os
from typing import Dict, List, Iterator, TypeVar, Union
import datetime as dt
from enum import Enum
from time import sleep
import logging

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
from requests.exceptions import ReadTimeout

from ..common.utils import local_yesterday

LICENSOR_ID = os.environ.get("SPOTIFY_LICENSOR_ID")


class SpotipyFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().endswith("returned 404 due to error")


spotipy.client.logger.addFilter(SpotipyFilter())


class CustomSpotify(spotipy.Spotify):
    class Precision(Enum):
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

    def podcast_api(self, path: str, *, payload=None, **kwargs) -> Dict:
        if path.startswith("/"):
            path = path[1:]

        url = "https://generic.wg.spotify.com/podcasters-analytics-api/" + path
        return self._internal_call("GET", url, payload, kwargs)

    def licensed_podcasts(self):
        return self.podcast_api(f"licensors/{LICENSOR_ID}/podcasts")

    def podcast_data(
        self,
        podcast_id: str,
        agg_type: str,
        date: Union[dt.date, dt.datetime],
        *,
        precision: Precision = Precision.DAY,
    ):
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
        agg_type: str,
        *,
        start: dt.date = None,
        end: dt.date = None,
    ):
        if start is None:
            start = dt.date(2016, 1, 1)
        if end is None:
            end = local_yesterday()

        return self.podcast_api(
            f"licensors/{LICENSOR_ID}/podcasts/{podcast_id}/{agg_type}/total",
            start=start.isoformat(),
            end=end.isoformat(),
        )["aggregation"][agg_type]["counts"]

    def podcast_followers(self, podcast_id: str):
        return self.podcast_api(
            f"licensors/{LICENSOR_ID}/podcasts/{podcast_id}/followers/total",
        )["aggregation"]["followers"]["counts"]

    def podcast_episodes(self, podcast_id: str):
        return self.podcast_api(
            f"licensors/{LICENSOR_ID}/podcasts/{podcast_id}/episodes"
        )

    def podcast_episode_meta(self, podcast_id: str, episode_id: str):
        return self.podcast_api(
            f"licensors/{LICENSOR_ID}/podcasts/{podcast_id}/episodes/{episode_id}/metadata"
        )

    def podcast_episode_data(
        self, podcast_id: str, episode_id: str, agg_type: str, date: dt.date
    ):
        return self.podcast_api(
            f"licensors/{LICENSOR_ID}/podcasts/{podcast_id}/episodes/{episode_id}/{agg_type}/{date.year}/{date.month}/{date.day}/total"
        )["aggregation"][agg_type]["counts"]

    def podcast_episode_data_all_time(
        self,
        podcast_id: str,
        episode_id: str,
        agg_type: str,
        end: dt.date = None,
    ):
        if end is None:
            end = local_yesterday()

        return self.podcast_api(
            f"licensors/{LICENSOR_ID}/podcasts/{podcast_id}/episodes/{episode_id}/{agg_type}/total",
            start="2016-01-01",
            end=end.isoformat(),
        )["aggregation"][agg_type]["counts"]

T = TypeVar('T')

def _divide_chunks(l: List[T], n: int) ->Iterator[List[T]]:
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i : i + n]


def fetch_all(
    fn: callable, ids: List[str], result_key: str, chunk_size: int = 50
) -> List[Dict]:
    agg = []
    for chunk in _divide_chunks(ids, chunk_size):
        result = fn(chunk)
        agg.extend(result[result_key])
    return agg


auth_manager = SpotifyClientCredentials()
spotify_api = CustomSpotify(auth_manager=auth_manager)
