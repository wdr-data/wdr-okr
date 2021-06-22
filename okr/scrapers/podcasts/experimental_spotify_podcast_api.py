"""This module provides a class to connect to an unofficial Spotify API
that provides podcast analytics. It relies on using cookies generated
manually by logging in with the appropriate user at podcasters.spotify.com.

Cookies supposedly last 1 year.
"""

import os
from typing import Dict, Optional
import datetime as dt
from time import sleep
from threading import RLock
from loguru import logger

import requests
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_exponential

BASE_URL = os.environ.get("EXPERIMENTAL_SPOTIFY_BASE_URL")
AUTH_URL = os.environ.get("EXPERIMENTAL_SPOTIFY_AUTH_URL")
CLIENT_ID = os.environ.get("EXPERIMENTAL_SPOTIFY_CLIENT_ID")
SP_AC = os.environ.get("EXPERIMENTAL_SPOTIFY_SP_AC")
SP_DC = os.environ.get("EXPERIMENTAL_SPOTIFY_SP_DC")
SP_KEY = os.environ.get("EXPERIMENTAL_SPOTIFY_SP_KEY")

DELAY_BASE = 2.0


class ExperimentalSpotifyPodcastAPI:
    """Representation of the experimental Spotify podcast API."""

    def __init__(self):
        self._bearer: Optional[str] = None
        self._bearer_expires: Optional[dt.datetime] = None
        self._auth_lock = RLock()

    @retry(wait=wait_exponential(), stop=stop_after_attempt(7))
    def _authenticate(self):
        """Retrieves a Bearer token for the experimental Spotify API, valid 1 hour."""

        with self._auth_lock:
            logger.info("Retrieving Bearer for experimental Spotify API")
            response = requests.get(
                f"{AUTH_URL}?client_id={CLIENT_ID}",
                cookies={
                    "sp_ac": SP_AC,
                    "sp_dc": SP_DC,
                    "sp_key": SP_KEY,
                },
            )
            response.raise_for_status()
            response_json = response.json()
            self._bearer = response_json["access_token"]
            expires_in = response_json["expires_in"]
            self._bearer_expires = dt.datetime.now() + dt.timedelta(seconds=expires_in)

    def _ensure_auth(self):
        """Checks if Bearer token expires soon. If so, requests a new one."""

        with self._auth_lock:
            if self._bearer is None or self._bearer_expires < (
                dt.datetime.now() - dt.timedelta(minutes=5)
            ):
                self._authenticate()

    @staticmethod
    def _build_url(*path: str) -> str:
        return f"{BASE_URL}{'/'.join(path)}"

    @staticmethod
    def _date_params(start: dt.date, end: dt.date) -> Dict[str, str]:
        return {
            "start": start.isoformat(),
            "end": end.isoformat(),
        }

    def _request(self, url: str, *, params: Optional[Dict[str, str]] = None) -> dict:
        delay = DELAY_BASE
        for attempt in range(6):
            sleep(delay)
            self._ensure_auth()
            response = requests.get(
                url,
                params=params,
                headers={"Authorization": f"Bearer {self._bearer}"},
            )

            if response.status_code in (429, 502, 503, 504):
                delay *= 2
                logger.log(
                    ("INFO" if attempt < 3 else "WARNING"),
                    'Got {} for URL "{}", next delay: {}s',
                    response.status_code,
                    url,
                    delay,
                )
                continue

            elif response.status_code == 401:
                self._authenticate()
                continue

            if not response.ok:
                logger.error("Error in experimental API:")
                logger.info(response.status_code)
                logger.info(response.headers)
                logger.info(response.text)
                response.raise_for_status()

            return response.json()

        raise Exception("All retries failed!")

    def podcast_followers(self, podcast_id: str, start: dt.date, end: dt.date) -> dict:
        """Loads historic follower data for podcast.

        Args:
            podcast_id (str): ID of the podcast to request data for.
            start (dt.date): Earliest date to request data for.
            end (dt.date): Most recent date to request data for.

        Returns:
            dict: Response data from API.
        """
        url = self._build_url(
            "shows",
            podcast_id,
            "followers",
        )
        return self._request(url, params=self._date_params(start, end))

    def podcast_aggregate(
        self,
        podcast_id: str,
        start: dt.date,
        end: Optional[dt.date] = None,
    ) -> dict:
        """Loads podcast demographics data.

        Args:
            podcast_id (str): ID of the podcast to request data for.
            start (dt.date): Earliest date to request data for.
            end (Optional[dt.date], optional): Most recent date to request data for.
              Defaults to None. Will be set to ``start`` if None.

        Returns:
            dict: [description]
        """
        if end is None:
            end = start

        url = self._build_url(
            "shows",
            podcast_id,
            "aggregate",
        )
        return self._request(url, params=self._date_params(start, end))

    def episode_performance(self, episode_id: str) -> dict:
        """Loads episode performance data.

        Args:
            episode_id (str): ID of the episode to request data for.

        Returns:
            dict: Response data from API.
        """

        url = self._build_url("episodes", episode_id, "performance")
        return self._request(url)

    def episode_aggregate(
        self,
        episode_id: str,
        start: dt.date,
        end: Optional[dt.date] = None,
    ) -> dict:
        """Loads episode demographics data.

        Args:
            episode_id (str): ID of the episode to request data for.
            start (dt.date): Earliest date to request data for.
            end (Optional[dt.date], optional): Most recent date to request data for.
              Defaults to None. Will be set to ``start`` if None.

        Returns:
            dict: [description]
        """
        if end is None:
            end = start

        url = self._build_url(
            "episodes",
            episode_id,
            "aggregate",
        )
        return self._request(url, params=self._date_params(start, end))


experimental_spotify_podcast_api = ExperimentalSpotifyPodcastAPI()
