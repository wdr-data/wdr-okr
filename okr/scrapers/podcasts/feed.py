"""Parse feed using feedparser
"""

import feedparser


def parse(url: str) -> feedparser.util.FeedParserDict:
    """Parse feed from url into FeedParserDict.

    Args:
        url (str): Url to be parsed.

    Returns:
        feedparser.util.FeedParserDict: Parsed data.
    """
    return feedparser.parse(url)
