"""Retrieve and process reviews data from the iTunes podcast directory."""

import json
from typing import Tuple, Union
from urllib import parse

import bs4
import requests

from ..common import types


class ItunesReviewsError(Exception):
    """Custom error for unexpected data for iTunes reviews."""

    def __init__(self, error_msg: str = None):
        self.message = (
            f"Unexpected reviews data from iTunes - check scraper ({error_msg})"
        )
        super().__init__(self.message)


class ITunesReviews:
    """Class representing various data related to iTunes reviews.

    The most important properties of an ``ITunesReviews`` object are:

    * ``itunes_url``: iTunes Podcast URL
    * ``ratings_average``: Rating average
    * ``review_count``: Number of reviews
    * ``reviews``: List of reviews


    Args:
        podcast_author (str): Exact author of podcast to search for.
        podcast_title (str): Exact title of podcast to search for.
        feed_url (str): Exact feed URL of podcast to search for.
        itunes_url (str, optional): iTunes URL for podcast, if known. Will be
            retrieved from iTunes Search API, if not provided.
        country_code (str, optional): Country code for iTunes Search API. Defaults
            to "DE".
        base_url (str, optional): Base URL for iTunes Search API. Defaults to
            "https://itunes.apple.com/search".
    """

    def __init__(
        self,
        podcast_author: str,
        podcast_title: str,
        feed_url: str,
        itunes_url: str = None,
        country_code: str = "DE",
        base_url: str = "https://itunes.apple.com/search",
    ) -> None:

        self.base_url = base_url
        self.country_code = country_code
        self.podcast_author = podcast_author
        self.podcast_title = podcast_title
        self.feed_url = feed_url

        # get podcast URL through iTunes Search API, if not provided:
        if not itunes_url:
            print(f'Querying iTunes Search API for "{self.podcast_title}"')
            self.itunes_url = self._get_metadata_url(
                podcast_author, podcast_title, feed_url
            )
        else:
            self.itunes_url = itunes_url

        # get podcast reviews from iTunes Podcasts with podcast URL
        if self.itunes_url:
            print(f"Scraping iTunes Podcast reviews data from {self.itunes_url}")
            self.user_ratings_raw = self._get_reviews_json(self.itunes_url)
            self.ratings_average = self.user_ratings_raw["aggregateRating"][
                "ratingValue"
            ]
            self.review_count = self.user_ratings_raw["aggregateRating"]["reviewCount"]
            self.reviews = self.user_ratings_raw["review"]
        else:
            self.user_ratings_raw = None
            self.ratings_averages = None
            self.review_count = None
            self.reviews = None

    def _get_apple_meta_data(self, baseurl: str, **params) -> types.JSON:
        """Retrieve data from iTunes Search API.

        Args:
            baseurl (str): Base url to combine with **params.

        Returns:
            types.JSON: Raw JSON representation of search result.
        """
        url = baseurl + "?" + parse.urlencode(params)

        result = requests.get(url)
        result.raise_for_status()

        json_data = json.loads(result.content)

        return json_data

    def _get_metadata_url(
        self, podcast_author: str, podcast_title: str, feed_url: str
    ) -> Union[str, None]:
        """Retrieve meta data URL from API based on podcast_author, podcast_title, and
        feed_url.

        Args:
            podcast_author (str): Exact author of podcast to search for.
            podcast_title (str): Exact title of podcast to search for.
            feed_url (str): Exact feed URL of podcast to search for.

        Returns:
            Union[str, None]: Meta data URL for podcast. Is None if no URL found.
        """

        # search parameters for https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/
        json_data = self._get_apple_meta_data(
            baseurl=self.base_url,
            country=self.country_code,
            term=podcast_title,
            media="podcast",
            attribute="titleTerm",
        )

        # iterate over all results and check against search criteria
        if json_data["resultCount"]:
            for result in json_data["results"]:
                if (
                    result["feedUrl"] == feed_url
                    and result["collectionName"] == podcast_title
                    and result["artistName"] == podcast_author
                ):
                    url = result["collectionViewUrl"].split("?")[0]
                else:
                    url = None
        else:
            url = None

        return url

    def _get_reviews_json(self, url: str) -> types.JSON:
        """Read reviews data for url from library.

        Args:
            url (str): URL to get reviews data for.

        Raises:
            ItunesReviewsError: Custom error for unexpected data for iTunes reviews.

        Returns:
            types.JSON: JSON representation of reviews data.
        """
        result = requests.get(url)
        soup = bs4.BeautifulSoup(result.content, "lxml")

        user_ratings_raw = soup.find("script", type="application/ld+json")
        if user_ratings_raw:
            user_ratings = json.loads(user_ratings_raw.contents[0])
        else:
            raise ItunesReviewsError

        return user_ratings
