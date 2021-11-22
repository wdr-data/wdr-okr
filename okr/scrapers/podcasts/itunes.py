"""Retrieve and process reviews data from the iTunes podcast directory."""

from decimal import Decimal
import html
import json
import re
from typing import Optional, Tuple

import bs4
import dateparser
from loguru import logger
import requests
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_exponential

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
    """Retrieve reviews and ratings data from iTunes Podcasts.

    Args:
        podcast (Podcast): Podcast to retrieve data for.

    Returns:
        Optional[Tuple[dict, dict]]: User ratings and user reviews for podcast. Returns
            None if podcast is not in the iTunes database or has no ratings.
    """
    # try getting podcast URL through iTunes Search API, if not provided:
    if not podcast.itunes_url:
        logger.info(
            'Querying iTunes Search API for "{}" to retrieve itunes_url',
            podcast.name,
        )
        podcast.itunes_url = _get_metadata_url(podcast)
        podcast.save()

    if not podcast.itunes_url:
        return None

    # get podcast ratings and reviews from iTunes Podcasts with podcast URL
    logger.info("Scraping iTunes Podcast reviews data from {}", podcast.itunes_url)
    user_ratings_raw, ratings_percentages = _get_reviews_json(podcast)

    if "aggregateRating" not in user_ratings_raw.keys():
        logger.warning(
            'Podcast "{}" is in iTunes database but has no reviews.',
            podcast.name,
        )
        return None

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
            "date": dateparser.parse(
                review["datePublished"], locales=["de", "en"]
            ).date(),
            "title": html.unescape(review["name"]),
            "text": html.unescape(review.get("reviewBody", "")),
            "rating": review["reviewRating"]["ratingValue"],
        }

    return (user_rating, user_reviews)


@retry(wait=wait_exponential(), stop=stop_after_attempt(4))
def _get_apple_meta_data(**params) -> types.JSON:
    """Retrieve data from iTunes Search API.

    Returns:
        types.JSON: Raw JSON representation of search result.
    """

    result = requests.get(BASE_URL, params=params)
    result.raise_for_status()

    return result.json()


def _get_metadata_url(
    podcast: Podcast,
) -> Optional[str]:
    """Retrieve meta data URL from API based on podcast.

    Args:
        podcast (Podcast): Podcast to retrieve URL for.

    Returns:
        Optional[str]: Meta data URL for podcast. Is None if no URL found.
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


@retry(wait=wait_exponential(), stop=stop_after_attempt(3))
def _get_reviews_json_raw(url: str) -> requests.Response:
    return requests.get(url)


def _get_reviews_json(podcast: Podcast, retry: bool = True) -> Tuple[types.JSON, dict]:
    """Read reviews data for URL from iTunes library.

    Args:
        url (str): URL to get reviews data for.
        retry (bool, optional): Retry finding URL when request returns 404 if True. No
            retry if False.

    Returns:
        Tuple[types.JSON, dict]: JSON representation of ratings and review data as well
            as dict of star ratings.
    """
    result = _get_reviews_json_raw(podcast.itunes_url)

    # retry once if the itunes_url is 404 (renamed podcast?)
    if result.status_code == 404 and retry:
        url = _get_metadata_url(podcast)

        if url:
            podcast.itunes_url = url
            podcast.save()

        return _get_reviews_json(podcast, retry=False)

    result.raise_for_status()

    # read schema JSON data
    soup = bs4.BeautifulSoup(result.content, "lxml")

    user_ratings_raw = soup.find("script", attrs={"name": "schema:podcast-show"})
    if user_ratings_raw:
        user_ratings = json.loads(user_ratings_raw.contents[0])
    else:
        raise ItunesReviewsError("Failed to find info JSON")

    # count individual stars
    review_bars = soup.find_all(
        "div", attrs={"class": "we-star-bar-graph__bar__foreground-bar"}
    )

    percentage_regex = r"width:\s*(\d+)%"
    reviews_percentages = dict()

    for review_percent, stars in zip(review_bars, range(5, 0, -1)):
        percentage = re.search(percentage_regex, review_percent.attrs["style"]).group(1)
        reviews_percentages[stars] = Decimal(percentage) / 100

    return (user_ratings, reviews_percentages)
