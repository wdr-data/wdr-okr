"""Retrieve and process reviews data from the iTunes podcast directory."""

import datetime as dt
from decimal import Decimal
import html
import json
import re
from typing import Optional, Tuple

import bs4
import requests

from okr.models.podcasts import Podcast
from ..common import types


BASE_URL = "https://itunes.apple.com/search"
COUNTRY_CODE = "DE"


class ItunesReviewsError(Exception):
    """Custom error for unexpected data for iTunes reviews."""

    def __init__(self, error_msg: str = None):
        self.message = (
            f"Unexpected reviews data from iTunes - check scraper ({error_msg})"
        )
        super().__init__(self.message)


def get_reviews(
    podcast: Podcast,
) -> Optional[Tuple[dict, dict]]:
    """Retrieve reviews data from iTunes Podcasts.

    * ``ratings_average``: Rating average
    * ``review_count``: Number of reviews
    * ``reviews``: List of reviews


    Args:
    """
    # Get podcast URL through iTunes Search API, if not provided:
    if not podcast.itunes_url:
        print(f'Querying iTunes Search API for "{podcast.name}" to retrieve itunes_url')
        podcast.itunes_url = _get_metadata_url(podcast)
        podcast.save()

    if not podcast.itunes_url:
        return None

    # Get podcast ratings and reviews from iTunes Podcasts with podcast URL
    print(f"Scraping iTunes Podcast reviews data from {podcast.itunes_url}")
    user_ratings_raw, ratings_percentages = _get_reviews_json(podcast)

    user_rating = {
        "ratings_average": float(user_ratings_raw["aggregateRating"]["ratingValue"]),
        "ratings_count": int(user_ratings_raw["aggregateRating"]["reviewCount"]),
        "ratings_1_stars": ratings_percentages[1],
        "ratings_2_stars": ratings_percentages[2],
        "ratings_3_stars": ratings_percentages[3],
        "ratings_4_stars": ratings_percentages[4],
        "ratings_5_stars": ratings_percentages[5],
    }

    user_reviews = {}

    for review in user_ratings_raw["review"]:
        user_reviews[html.unescape(review["author"])] = {
            "date": dt.datetime.strptime(review["datePublished"], "%d.%m.%Y").date(),
            "title": html.unescape(review["name"]),
            "text": html.unescape(review["reviewBody"]),
            "rating": review["reviewRating"]["ratingValue"],
        }

    return (user_rating, user_reviews)


def _get_apple_meta_data(**params) -> types.JSON:
    """Retrieve data from iTunes Search API.

    Args:
        baseurl (str): Base url to combine with **params.

    Returns:
        types.JSON: Raw JSON representation of search result.
    """

    result = requests.get(BASE_URL, params=params)
    result.raise_for_status()

    return result.json()


def _get_metadata_url(
    podcast: Podcast,
) -> Optional[str]:
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
    json_data = _get_apple_meta_data(
        country=COUNTRY_CODE,
        term=podcast.name,
        media="podcast",
        attribute="titleTerm",
    )

    # iterate over all results and check against search criteria
    url = None

    for result in json_data.get("results", []):
        if (
            result["collectionName"] == podcast.name
            and result["artistName"] == podcast.author
        ):
            url = result["collectionViewUrl"].split("?")[0]
            break

    return url


def _get_reviews_json(podcast: Podcast, retry: bool = True) -> types.JSON:
    """Read reviews data for url from library.

    Args:
        url (str): URL to get reviews data for.

    Raises:
        ItunesReviewsError: Custom error for unexpected data for iTunes reviews.

    Returns:
        types.JSON: JSON representation of reviews data.
    """
    result = requests.get(podcast.itunes_url)

    # Retry once if the itunes_url is 404 (renamed podcast?)
    if result.status_code == 404 and retry:
        podcast = _get_metadata_url(podcast)
        podcast.save()
        return _get_reviews_json(podcast, retry=False)

    result.raise_for_status()

    soup = bs4.BeautifulSoup(result.content, "lxml")

    user_ratings_raw = soup.find("script", attrs={"name": "schema:podcast-show"})
    if user_ratings_raw:
        user_ratings = json.loads(user_ratings_raw.contents[0])
    else:
        raise ItunesReviewsError("Failed to find review info JSON")

    # Count individual stars
    review_bars = soup.find_all(
        "div", attrs={"class": "we-star-bar-graph__bar__foreground-bar"}
    )

    percentage_regex = r"width:\s*(\d+)%"
    reviews_percentages = dict()

    for review_percent, stars in zip(review_bars, range(5, 0, -1)):
        percentage = re.search(percentage_regex, review_percent.attrs["style"]).group(1)
        reviews_percentages[stars] = Decimal(percentage) / 100

    return (user_ratings, reviews_percentages)
