import os
from typing import List, Dict
import datetime as dt

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from ..common.utils import local_yesterday

LICENSOR_ID = os.environ.get("SPOTIFY_LICENSOR_ID")


class CustomSpotify(spotipy.Spotify):
    def _auth_headers(self):
        headers = super()._auth_headers()
        headers["Accept"] = "application/json"
        return headers

    def podcast_api(self, path: str, *, payload=None, **kwargs) -> Dict:
        if path.startswith("/"):
            path = path[1:]

        url = "https://generic.wg.spotify.com/podcasters-analytics-api/" + path
        return self._internal_call("GET", url, payload, kwargs)

    def licensed_podcasts(self):
        return self.podcast_api(f"licensors/{LICENSOR_ID}/podcasts")

    def podcast_data(self, podcast_id: str, agg_type: str, date: dt.date):
        return self.podcast_api(
            f"licensors/{LICENSOR_ID}/podcasts/{podcast_id}/{agg_type}/{date.year}/{date.month}/{date.day}/total"
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


def _divide_chunks(l: List, n: int):
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
