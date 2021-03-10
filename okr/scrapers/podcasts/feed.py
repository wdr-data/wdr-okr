"""Parse podcast feed using the feedparser library."""

import html
import re

import feedparser


def parse(url: str) -> feedparser.util.FeedParserDict:
    """Parse feed from url into FeedParserDict.

    Also adds the property ``feed.itunes_categories`` which is usually not supported by
    feedparser.

    Args:
        url (str): Url to be parsed.

    Returns:
        feedparser.util.FeedParserDict: Parsed data.
    """

    # Hijacking a private function - might be better to use urllib2 directly.
    # However, that would be an additional dependency...
    result = feedparser.util.FeedParserDict(
        bozo=False,
        entries=[],
        feed=feedparser.util.FeedParserDict(),
        headers={},
    )
    raw_xml = feedparser.api._open_resource(
        url_file_stream_or_string=url,
        etag=None,
        modified=None,
        agent=feedparser.USER_AGENT,
        referrer=None,
        handlers=None,
        request_headers=None,
        result=result,
    )

    # this regex finds categories and sub-categories
    category_regex = r"<itunes:category text=\".*?[\"|\/]>"

    categories_raw = re.findall(category_regex, str(raw_xml))

    categories = []
    for category in categories_raw:
        category = category.split('"')[1]
        category = html.unescape(category)  # e.g. for 'Society & Culture'
        categories.append(category)

    parsed_xml = feedparser.parse(raw_xml)

    parsed_xml.feed.itunes_categories = categories

    return parsed_xml
