"""Wrapper for Webtrekk API."""

from contextlib import contextmanager
from typing import Any, Dict, Optional
import datetime as dt
import json
import os

import requests
from loguru import logger

from ....models.cached_requests import CachedWebtrekkRequest


WEBTREKK_LOGIN = os.environ.get("WEBTREKK_LOGIN")
WEBTREKK_PASSWORD = os.environ.get("WEBTREKK_PASSWORD")


class WebtrekkError(Exception):
    """Error class for Webtrekk."""

    pass


class Webtrekk:
    """Webtrekk API Object Class.

    Requires the following environment variables: WEBTREKK_LOGIN, WEBTREKK_PASSWORD,
    WEBTREKK_ACCOUNT_LIVE_ID.
    """

    def __init__(self):
        """Set up login information for Webtrekk JSON/RPC API."""
        self.token = None
        self.account = os.environ.get("WEBTREKK_ACCOUNT_LIVE_ID")
        self.name = f"{WEBTREKK_LOGIN}-LIVE-account"

    def __str__(self):
        if self.token:
            return f"{WEBTREKK_LOGIN} is connected to {self.name}."
        return f"{WEBTREKK_LOGIN} ist not connected to {self.name}."

    def login(self):
        """Login to JSON/RPC API."""
        params = {
            "login": WEBTREKK_LOGIN,
            "pass": WEBTREKK_PASSWORD,
            "customerId": self.account,
            "language": "de",
        }
        self.token = self._get_response(method="login", params=params)
        logger.info(
            "{} has been successfully connected to to {}.",
            WEBTREKK_LOGIN,
            self.name,
        )

    def logout(self):
        """Logout from JSON/RPC API."""
        self._get_response("logout", {"token": self.token})
        logger.info(
            "{} has been logged out successfully from {}.",
            WEBTREKK_LOGIN,
            self.name,
        )

    @contextmanager
    def session(self):
        """Initiate session with :meth:`~okr.scrapers.common.webtrekk.Webtrekk.login`
        and use :meth:`~okr.scrapers.common.webtrekk.Webtrekk.logout` in case of errors.
        """
        self.login()
        try:
            yield
        finally:
            self.logout()

    def _get_response(
        self,
        method: str,
        params: Dict[str, str] = {},
        use_cache: bool = False,
        force_cache_refresh: bool = False,
    ) -> Any:
        """Call Webtrekk JSON/RPC API Method with params.

        Args:
            method (str): API request method as defined by the API. For example:
              "getAnalysisData", "getReportData", "getAnalysisObjectsAndMetricsList", or
              "getCustomReportsList".
            params (Dict[str, str], optional): Parameters for API request. Defaults to
              {}.
            use_cache (bool, optional): If set to ``True``, requests will be saved to and
              retrieved from a persistent cache to avoid repeat API requests.
              Defaults to ``False``.
            force_cache_refresh (bool, optional): If set to ``True``, makes a query to the
              API even on cache hit and caches the result. Requires ``use_cache`` to be ``True``.
              Defaults to ``False``.

        Raises:
            WebtrekkError: Custom error for Webtrekk errors.

        Returns:
            Any: Reply from API. Can be int, str, and dict, for example.

        :meta public:
        """

        if force_cache_refresh and not use_cache:
            raise ValueError(
                f"Can't have {force_cache_refresh = } while {use_cache = }"
            )

        url = "https://report2.webtrekk.de/cgi-bin/wt/JSONRPC.cgi"

        payload = {
            "params": params,
            "version": "1.1",
            "method": method,
        }

        # Create key for cache lookups
        payload_cache_key = json.dumps(payload)

        # Insert token after creating the payload cache key
        if self.token:
            params["token"] = self.token

        # Check if a request with this payload is already cached - query API if not
        logger.debug(f"{use_cache = }, {force_cache_refresh = }")
        if use_cache and not force_cache_refresh:
            cached = CachedWebtrekkRequest.objects.filter(
                payload=payload_cache_key
            ).first()

            if cached:
                logger.debug("Cached request for payload found")
                logger.debug(payload_cache_key)
                return json.loads(cached.response)["result"]

            logger.debug("No cached request for payload found")
            logger.debug(payload_cache_key)

        response = requests.post(url, json=payload)
        response_data = response.json()

        if "result" in response_data:
            if use_cache:
                CachedWebtrekkRequest.objects.create(
                    payload=payload_cache_key,
                    response=response.text,
                )
                logger.debug("New cached entry for payload created")
                logger.debug(payload_cache_key)

            return response_data["result"]

        if "error" in response_data:
            raise WebtrekkError(response_data["error"])

        return None

    def get_report_data(
        self,
        name: str,
        start_date: Optional[dt.date] = None,
        end_date: Optional[dt.date] = None,
    ) -> Dict:
        """Call getReportData method at Webtrekk's JSON/RPC API.

        Args:
            name (str): id of the report to retrieve
            start_date (Optional[dt.date], optional): Earliest date to retrieve data
              for. If only a start_date but no end_date is provided, the scraper will
              only collect data for the date provided in start_date. Defaults to None.
            end_date (Optional[dt.date], optional): Latest date to retrieve data
              for. Defaults to None.

        Returns:
            Dict: Reply from API.
        """

        params = {"report_name": name}

        # Date format="YYYY-MM-DD"
        if start_date:
            params["time_start"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["time_stop"] = end_date.strftime("%Y-%m-%d")
        if start_date and not end_date:
            params["time_stop"] = params["time_start"]

        return self._get_response("getReportData", params, use_cache=True)

    def get_analysis_data(self, analysis_config: str) -> Dict:
        """Call getAnalysisData method at Webtrekk's JSON/RPC API.

        Args:
            analysis_config (str): Config information for analysis (according to API
            documentation).

        Returns:
            Dict: Reply from API.
        """
        params = {"analysisConfig": analysis_config}
        data = self._get_response("getAnalysisData", params, use_cache=True)
        return data

    def get_dimensions_metrics(self) -> Dict:
        """Call getAnalysisObjectsAndMetricsList method at Webtrekk's JSON/RPC API.

        Returns:
            Dict:  Reply from API.
        """
        return self._get_response("getAnalysisObjectsAndMetricsList")

    def get_report_list(self) -> Dict:
        """Call getAnalysisObjectsAndMetricsList method at Webtrekk's JSON/RPC API.

        Returns:
            Dict:  Reply from API.
        """
        return self._get_response("getCustomReportsList")
