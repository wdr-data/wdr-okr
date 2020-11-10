import requests
import os
import datetime as dt
from typing import Dict, Optional
from contextlib import contextmanager


WEBTREKK_LOGIN = os.environ.get("WEBTREKK_LOGIN")
WEBTREKK_PASSWORD = os.environ.get("WEBTREKK_PASSWORD")


class WebtrekkError(Exception):
    pass


class Webtrekk:
    """
    Webtrekk API Object Class
    """

    def __init__(self):
        """
        Login to Webtrekk JSON/RCP Api
        """
        self.token = None
        self.account = os.environ.get("WEBTREKK_ACCOUNT_LIVE_ID")
        self.name = f'{WEBTREKK_LOGIN}-LIVE-account'

    def __str__(self):
        if self.token:
            return f"{WEBTREKK_LOGIN} is connected to {self.name}."
        return f"{WEBTREKK_LOGIN} ist not connected to {self.name}."

    def login(self):
        params = {"login": WEBTREKK_LOGIN,
                  "pass": WEBTREKK_PASSWORD,
                  "customerId": self.account,
                  "language": "de",
                  }
        self.token = self._get_response(method='login', params=params)
        print(f"{WEBTREKK_LOGIN} has been sucessfully connected to to {self.name}.")

    def logout(self):
        """
        Logout from JSON/RSP Api
        """
        self._get_response('logout', {'token': self.token})
        print(f"{WEBTREKK_LOGIN} has been logged out sucessfully from {self.name}.")

    @contextmanager
    def session(self):
        self.login()
        try:
            yield 
        finally:
            self.logout()

    def _get_response(self, method: str, params: Dict[str, str]  = {}):
        """
        Call Webtrekk JSON/RCP Api Method with Params
        """
        url = 'https://report2.webtrekk.de/cgi-bin/wt/JSONRPC.cgi'

        # Example echo method
        if self.token:
            params['token'] = self.token

        payload = {
            "params": params,
            "version": "1.1",
            "method": method,
        }
    
        response = requests.post(url, json=payload).json()

        if 'result' in response:
            return response['result']
        if 'error' in response:
            raise WebtrekkError(response['error'])
        return None

    def get_report_data(self, name: str, start_date: Optional[dt.date] = None, end_date: Optional[dt.date] = None):
        """
        Call getReportData
        """
        params = {'report_name': name}
        
        #Date format="YYYY-MM-DD"
        if start_date:
            params['time_start'] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params['time_stop'] = end_date.strftime("%Y-%m-%d")
        if start_date and not end_date:
            params['time_stop'] = params['time_start']
    
        return self._get_response('getReportData', params)


    def get_analysis_data(self, analysis_config):
        """
        Call JSON/RCP Api for Analytics Data
        """
        params = {'analysisConfig': analysis_config}
        data = self._get_response('getAnalysisData', params)
        return data

    def get_dimensions_metrics(self):
        """
        Call getAnalysisObjectsAndMetricsList
        """
        return self._get_response('getAnalysisObjectsAndMetricsList')

    def get_report_list(self):
        """
        Call getCustomReportsList
        """
        return self._get_response('getCustomReportsList')
