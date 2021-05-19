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

    def _get_response(self, method: str, params: Dict[str, str] = {}) -> Any:
        """Call Webtrekk JSON/RPC API Method with params.

        Args:
            method (str): API request method as defined by the API. For example:
              "getAnalysisData", "getReportData", "getAnalysisObjectsAndMetricsList", or
              "getCustomReportsList".
            params (Dict[str, str], optional): Parameters for API request. Defaults to
              {}.

        Raises:
            WebtrekkError: Custom error for Webtrekk errors.

        Returns:
            Any: Reply from API. Can be int, str, and dict, for example.

        :meta public:
        """
        url = "https://report2.webtrekk.de/cgi-bin/wt/JSONRPC.cgi"

        # Example echo method
        if self.token:
            params["token"] = self.token

        payload = {
            "params": params,
            "version": "1.1",
            "method": method,
        }
        payload_str = json.dumps(payload)

        # Check if getAnalysisData query is already cached - query API if not
        if method == "getAnalysisData":  # no caching if method is "login"/"logout"
            cached = CachedWebtrekkRequest.objects.filter(payload=payload_str).first()
        else:
            cached = None

        if cached:
            logger.debug("Cached request for payload found ({})", payload_str)
            return json.loads(cached.response)["result"]

        response = requests.post(url, json=payload).json()

        if "result" in response:
            if method == "getAnalysisData":  # no caching if method is "login"/"logout"
                CachedWebtrekkRequest.objects.create(
                    payload=payload_str,
                    response=json.dumps(response),
                )
                logger.debug("New cached entry for payload created ({})", payload_str)
            return response["result"]
        if "error" in response:
            raise WebtrekkError(response["error"])
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

        return self._get_response("getReportData", params)

    def get_analysis_data(self, analysis_config: str) -> Dict:
        """Call getAnalysisData method at Webtrekk's JSON/RPC API.

        Args:
            analysis_config (str): Config information for analysis (according to API
            documentation).

        Returns:
            Dict: Reply from API.
        """
        params = {"analysisConfig": analysis_config}
        data = self._get_response("getAnalysisData", params)
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
