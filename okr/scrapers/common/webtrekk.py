"""
Creatin of Webtrekk JSON/RPC Module
"""
import requests
import os

WEBTREKK_LOGIN = os.environ.get("WEBTREKK_LOGIN")
WEBTREKK_PASSWORD = os.environ.get("WEBTREKK_PASSWORD")


class Webtrekkjson:
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
        self.token = self.get_response(method='login', params=params)
        print(f"{WEBTREKK_LOGIN} has been sucessfully connected to to {self.name}.")

    def logout(self):
        """
        Logout from JSON/RSP Api
        """
        self.get_response('logout', {'token': self.token})
        print(f"{WEBTREKK_LOGIN} has been loged out sucessfully from {self.name}.")

    def get_response(self, method=str, params={}):
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
            print(response['error'])
            return f'Error in method {method}'
        return print(f'Something unexpected happend: {response}')

    def get_analysis_data(self, analysis_config):
        """
        Call JSON/RCP Api for Analytics Data
        """
        params = {'analysisConfig': analysis_config}
        data = self.get_response('getAnalysisData', params)
        return data

    def get_dimensions_metrics(self):
        """
        Call getAnalysisObjectsAndMetricsList
        """
        return self.get_response('getAnalysisObjectsAndMetricsList')

    def get_report_list(self):
        """
        Call getCustomReportsList
        """
        return self.get_response('getCustomReportsList')

    def get_report_data(self, name):
        """
        Call getReportData
        """
        return self.get_response('getReportData', {'report_name': name})
