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
import random
import string
import base64
import hashlib
import re

import requests
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_exponential
import yaml

BASE_URL = os.environ.get("EXPERIMENTAL_SPOTIFY_BASE_URL")
CLIENT_ID = os.environ.get("EXPERIMENTAL_SPOTIFY_CLIENT_ID")
SP_AC = os.environ.get("EXPERIMENTAL_SPOTIFY_SP_AC")
SP_DC = os.environ.get("EXPERIMENTAL_SPOTIFY_SP_DC")
SP_KEY = os.environ.get("EXPERIMENTAL_SPOTIFY_SP_KEY")

DELAY_BASE = 2.0


def random_string(
    length: int,
    chars: str = string.ascii_lowercase + string.ascii_uppercase + string.digits,
) -> str:
    """Simple helper function to generate random strings suitable for use with Spotify"""
    return "".join(random.choices(chars, k=length))


class ExperimentalSpotifyPodcastAPI:
    """Representation of the experimental Spotify podcast API."""

    def __init__(self):
        self._bearer: Optional[str] = None
        self._bearer_expires: Optional[dt.datetime] = None
        self._auth_lock = RLock()

    @retry(wait=wait_exponential(), stop=stop_after_attempt(7))
    def _authenticate(self):
        """
        Retrieves a Bearer token for the experimental Spotify API, valid 1 hour.

        Generally follows the steps outlined here:
        https://developer.spotify.com/documentation/general/guides/authorization/code-flow/
        (with a few exceptions)
        """

        with self._auth_lock:
            logger.info("Retrieving Bearer for experimental Spotify API...")

            logger.debug("Generating secrets")

            state = random_string(32)

            code_verifier = random_string(64)
            code_challenge = base64.b64encode(
                hashlib.sha256(code_verifier.encode("utf-8")).digest()
            ).decode("utf-8")

            # Fix up format of code_challenge for spotify
            code_challenge = re.sub(r"=+$", "", code_challenge)
            code_challenge = code_challenge.replace("/", "_")
            code_challenge = code_challenge.replace("+", "-")

            logger.trace("state = {}", state)
            logger.trace("code_verifier = {}", code_verifier)
            logger.trace("code_challenge = {}", code_challenge)

            logger.debug("Requesting User Authorization")
            response = requests.get(
                "https://accounts.spotify.com/oauth2/v2/auth",
                params={
                    "response_type": "code",
                    "client_id": CLIENT_ID,
                    "scope": "streaming ugc-image-upload user-read-email user-read-private",
                    "redirect_uri": "https://podcasters.spotify.com",
                    "code_challenge": code_challenge,
                    "code_challenge_method": "S256",
                    "state": state,
                    "response_mode": "web_message",  # TODO: Figure out if there is a way to get pure JSON
                    "prompt": "none",
                },
                cookies={
                    "sp_ac": SP_AC,
                    "sp_dc": SP_DC,
                    "sp_key": SP_KEY,
                },
            )
            response.raise_for_status()

            # We get some weird HTML here that contains some JS
            html = response.text

            match = re.search(r"const authorizationResponse = (.*?);", html, re.DOTALL)
            json_str = match.group(1)

            # The extracted string isn't strictly valid JSON due to some missing quotes,
            # but PyYAML loads it fine
            auth_response = yaml.safe_load(json_str)

            # Confirm that auth was successful
            assert auth_response["type"] == "authorization_response"
            assert auth_response["response"]["state"] == state

            auth_code = auth_response["response"]["code"]

            logger.trace("auth_code = {}", auth_code)

            logger.debug("Requesting Bearer Token")
            response = requests.post(
                "https://accounts.spotify.com/api/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": CLIENT_ID,
                    "code": auth_code,
                    "redirect_uri": "https://podcasters.spotify.com",
                    "code_verifier": code_verifier,
                },
            )
            response.raise_for_status()

            response_json = response.json()

            self._bearer = response_json["access_token"]
            expires_in = response_json["expires_in"]
            self._bearer_expires = dt.datetime.now() + dt.timedelta(seconds=expires_in)

            logger.trace("bearer = {}", self._bearer)

            logger.success("Bearer token retrieved!")

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
