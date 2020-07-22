import feedparser


def parse(url):
    return feedparser.parse(url)
