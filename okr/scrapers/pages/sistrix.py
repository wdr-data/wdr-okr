""" Collect data from Sistrix API """

# https://api.sistrix.com/credits?api_key=API_KEY&format=json
# ?country=[COUNTRY_CODE]    de
# ?extended=true monatlich und nicht wöchentlich aktualisiert, sind dafür aber deutlich umfangreicher.
# ?mobile=true  Ergebnisse für Suchen mit dem Smartphone.
# 300 Zugriffe je Minute begrenzt. Zwischen zwei Aufrufen sollten mindestens 300ms liegen. Werden diese Grenzen dauerhaft überschritten, antwortet die API mit dem Status-Code 429 (Too many requests),

# 1. domain https://www.sistrix.de/api/domain

import os
import json
import requests
from urllib.parse import urlunparse, urlencode


class SistrixError(Exception):
    def __init__(self, error_msg: str = None):
        self.message = f"Sistrix API error: {error_msg}"
        super().__init__(self.message)


class Sistrix:
    """Wrapper for the Sistrix API (https://www.sistrix.de/api/)

    First, create an instance, using an API key:

    >>> sistrix_api_object = Sistrix(api_key)

    Next, request data using the get_data() method: The first argument to pass to this
    method is the "Methode" as defined by Systrix (e.g. "domain.overview" or
    "domain.competitors.seo"). The "Parameter" are passed as kwargs.

    """

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.data_format = "json"
        self.base_url = "api.sistrix.com"

    def _check_response_data(self, json_data: json, method: str):
        """Check Sistrix API json_data for common errors.

        Args:
            json_data (json): API reply data to check
            method (str): Method of original request

        Raises:
            SistrixError: Raise error with error message

        Returns:
            json: Return the checked json data
        """
        # check if json_data contains an error message
        if "error" in json_data:
            raise SistrixError(json_data["error"])
        # check if API replied with the correct method
        elif json_data["method"][0][0] != method:
            error_msg = f"Reply does not match supplied method. Supplied: {method} Received: {json_data['method'][0][0]})."
            raise SistrixError(error_msg)

    def get_data(self, method: str, **kwargs) -> json:
        """Request data from Sistrix API. Return JSON dict if request was successful.

        Args:
            method (str): Method to request data for

        Raises:
            SistrixError: Error occurred when requesting data from API

        Returns:
            json: JSON representation of API reply
        """
        # create dict of basic queries (i.e. api_key and format)
        base_queries = {
            "api_key": self.api_key,
            "format": self.data_format,
        }
        # build basic url for request
        url = urlunparse(
            ("https", self.base_url, method, "", urlencode(base_queries), "")
        )

        # request data from url with kwargs as params
        try:
            request = requests.get(url=url, params=kwargs)
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.TooManyRedirects,
            requests.exceptions.Timeout,
        ) as error:
            raise SistrixError(error)

        # check request status code
        if request.status_code != 200:
            raise SistrixError(request)

        json_data = json.loads(request.text)

        self._check_response_data(json_data, method)  # check reply for common errors

        return json_data


if __name__ == "__main__":

    sistrix_api_key = os.environ.get("SISTRIX_KEY")

    sistrix_api = Sistrix(sistrix_api_key)

    # Example 1: "Die Methode domain" https://www.sistrix.de/api/domain#domain
    data = sistrix_api.get_data("domain", path="https://www1.wdr.de/nachrichten/")

    # # Example 2: "Kontostand" der Credits abfragen https://www.sistrix.de/api/#Credit-System
    # data = sistrix_api.get_data("credits")

    # # Example 3: Überblick über aktuelle Kennzahlen zu der Domain (domain.overview) https://www.sistrix.de/api/domain#domainoverview
    # data = sistrix_api.get_data("domain.overview", path="https://www1.wdr.de/nachrichten/")

    # # Example 4: domain.sichtbarkeitsindex für einzelne Seite https://www.sistrix.de/api/domain#domainsichtbarkeitsindexoverview
    # data = sistrix_api.get_data(
    #     "domain.sichtbarkeitsindex",
    #     url="https://www1.wdr.de/nachrichten/themen/coronavirus/foerderschulen-lockdown-100.html",
    # )

    # # Example 5: domain.ideas https://www.sistrix.de/api/domain#domainideas
    # data = sistrix_api.get_data(
    #     "domain.ideas",
    #     path="https://www1.wdr.de/nachrichten/",
    #     limit = 5,
    # )

    # # Example 6: keyword.seo https://www.sistrix.de/api/keyword#keywordseo
    # data = sistrix_api.get_data(
    #     "keyword.seo",
    #     kw = "Bonn",
    #     num = 10,
    # )

    # # Example 7: links.linktexts https://www.sistrix.de/api/link#linkslinktexts
    # data = sistrix_api.get_data(
    #     "links.linktexts",
    #     domain="https://www1.wdr.de/",
    #     num=5,
    # )
    # # hier kommt 403 Permission Denied - sogar mit manueller Abfrage im Browser:
    # # https://api.sistrix.com/links.linktexts?api_key=API_KEY&domain=wdr.de&num=3&format=json
    # # Haben wir vielleicht gar keinen Zugriff auf diesen Teilbereich der API??!

    print(json.dumps(data, indent=3))
