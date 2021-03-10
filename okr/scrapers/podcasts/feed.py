"""Parse podcast feed using the feedparser library."""

import html
import re

import feedparser
import requests
import bs4


def parse(url: str) -> feedparser.util.FeedParserDict:
    """Parse feed from ``url`` into ``FeedParserDict``.

    Also adds the properties ``feed.itunes_category`` and ``feed.itunes_subcategory``
    which are usually not supported by ``feedparser``.

    Args:
        url (str): Url to be parsed.

    Returns:
        feedparser.util.FeedParserDict: Parsed data.
    """

    raw_xml = requests.get(url).content
    parsed_xml = feedparser.parse(raw_xml)

    # Extract itunes:category manually cause feedparser mixes them with keywords
    soup = bs4.BeautifulSoup(markup=raw_xml, features="lxml-xml")

    # Parse categories like Apple does
    # https://help.apple.com/itc/podcasts_connect/#/itcb54353390
    category = soup.channel.find("itunes:category", recursive=False)
    parsed_xml.feed.itunes_category = category and category.attrs["text"]
    parsed_xml.feed.itunes_subcategory = None

    if category:
        subcategory = category.find("itunes:category")
        parsed_xml.feed.itunes_subcategory = subcategory and subcategory.attrs["text"]

    return parsed_xml
