"""
This module provides a class to connect to an unofficial Spotify API
that provides podcast analytics. It relies on using cookies generated
manually by logging in with the appropriate user at podcasters.spotify.com

Cookies supposedly last 1 year.
"""

import os
from typing import Dict, Optional
import datetime as dt
from time import sleep

import requests

BASE_URL = os.environ.get("EXPERIMENTAL_SPOTIFY_BASE_URL")
AUTH_URL = os.environ.get("EXPERIMENTAL_SPOTIFY_AUTH_URL")
CLIENT_ID = os.environ.get("EXPERIMENTAL_SPOTIFY_CLIENT_ID")
SP_AC = os.environ.get("EXPERIMENTAL_SPOTIFY_SP_AC")
SP_DC = os.environ.get("EXPERIMENTAL_SPOTIFY_SP_DC")
SP_KEY = os.environ.get("EXPERIMENTAL_SPOTIFY_SP_KEY")

API_BASE_URL = "https://generic.wg.spotify.com/podcasters/v0/"
DELAY_BASE = 2.0


class ExperimentalSpotifyPodcastAPI:
    def __init__(self):
        self._bearer: Optional[str] = None
        self._bearer_expires: Optional[dt.datetime] = None

    def _authenticate(self):
        """Retrieves a Bearer token for the experimental Spotify API, valid 1 hour."""
        print("Retrieving Bearer for experimental Spotify API")
        response = requests.get(
            f"https://generic.wg.spotify.com/creator-auth-proxy/v1/web/token?client_id={CLIENT_ID}",
            cookies={
                "sp_ac": SP_AC,
                "sp_dc": SP_DC,
                "sp_key": SP_KEY,
            },
        )
        response_json = response.json()
        self._bearer = response_json["access_token"]
        expires_in = response_json["expires_in"]
        self._bearer_expires = dt.datetime.now() + dt.timedelta(seconds=expires_in)

    def _ensure_auth(self):
        """Checks if Bearer token expires soon. If so, requests a new one."""
        if self._bearer is None or self._bearer_expires < (
            dt.datetime.now() - dt.timedelta(minutes=5)
        ):
            self._authenticate()

    @staticmethod
    def _build_url(*path: str, params: Optional[Dict[str, str]] = None) -> str:
        qs = ""

        if params is not None:
            qs = "?" + "&".join(f"{key}={val}" for key, val in params.items())

        return f"{API_BASE_URL}{'/'.join(path)}{qs}"

    @staticmethod
    def _date_params(start: dt.date, end: dt.date) -> Dict[str, str]:
        return {
            "start": start.isoformat(),
            "end": end.isoformat(),
        }

    def _request(self, url: str) -> dict:
        delay = DELAY_BASE
        for _ in range(6):
            sleep(delay)
            self._ensure_auth()
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {self._bearer}"},
            )

            if response.status_code == 429:
                delay *= 2
                print("Got 429, next delay:", delay)
                continue

            if not response.ok:
                print("Error in experimental API:")
                print(response.status_code)
                print(response.headers)
                print(response.text)

            return response.json()

    def podcast_followers(self, podcast_id: str, start: dt.date, end: dt.date) -> dict:
        """Loads historic follower data for podcast."""
        url = self._build_url(
            "shows",
            podcast_id,
            "followers",
            params=self._date_params(start, end),
        )
        return self._request(url)

    def episode_performance(self, episode_id: str) -> dict:
        """Loads episode performance data."""

        url = self._build_url("episodes", episode_id, "performance")
        return self._request(url)

    def episode_aggregate(
        self,
        episode_id: str,
        start: dt.date,
        end: Optional[dt.date] = None,
    ) -> dict:
        """
        Loads episode demographics data.

        If end is None, end == start
        """
        if end is None:
            end = start

        url = self._build_url(
            "episodes",
            episode_id,
            "aggregate",
            params=self._date_params(start, end),
        )
        return self._request(url)


experimental_spotify_podcast_api = ExperimentalSpotifyPodcastAPI()
