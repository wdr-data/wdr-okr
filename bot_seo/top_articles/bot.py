""" SEO Bot for top articles """

import datetime as dt
import os
from typing import List

from django.db.models import F, Sum
from loguru import logger

from okr.models.pages import (
    Page,
    PageDataQueryGSC,
    PageDataWebtrekk,
    SophoraDocumentMeta,
)
from okr.scrapers.common.utils import (
    local_yesterday,
)
from .teams_message import _generate_adaptive_card
from ..teams_tools import generate_teams_payload, send_to_teams

WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK_SEO_BOT")
ARTICLE_THRESHOLD = int(os.environ.get("SEO_BOT_TOP_ARTICLES_THRESHOLD", 10000))


def _get_top_articles(number_of_articles: int = 3, date: dt.date = None) -> List[Page]:
    # Get a number of pages that had the highest number of clicks on a certain date.
    logger.debug("Requesting top articles from DB")
    gsc_top_articles = (
        Page.objects.filter(data_gsc__date=date)
        .annotate(impressions_all=Sum("data_gsc__impressions"))
        .annotate(clicks_all=Sum("data_gsc__clicks"))
        .order_by(F("clicks_all").desc(nulls_last=True))
    )

    top_articles = gsc_top_articles[0:number_of_articles]

    for page in top_articles:
        # Retrieve and append latest_meta
        latest_meta = (
            SophoraDocumentMeta.objects.filter(sophora_document__sophora_id__page=page)
            .order_by("-editorial_update")
            .first()
        )

        if latest_meta:
            page.latest_meta = latest_meta
            logger.debug("Metas found and added for {}", page.url)
        else:
            page.latest_meta = None
            logger.warning("No metas found for {}, skipping", page.url)

        # Add webtrekk data to page object
        webtrekk_data = PageDataWebtrekk.objects.filter(
            webtrekk_meta__page=page,
            date=date,
        ).first()

        # Special case for Nachrichten index.html and other very old pages
        if not webtrekk_data:
            webtrekk_data = (
                PageDataWebtrekk.objects.filter(
                    webtrekk_meta__page__url=page.url.replace("https://", "http://"),
                    date=date,
                )
                .exclude(
                    webtrekk_meta__headline="html",
                )
                .first()
            )

        if webtrekk_data:
            page.webtrekk_data = webtrekk_data
            logger.debug("Webtrekk data found and added for {}", page.url)
        else:
            page.webtrekk_data = None
            logger.warning("No webtrekk data found for {}, skipping", page.url)

        # Add top Google queries
        top_queries = PageDataQueryGSC.objects.filter(page=page, date=date).order_by(
            "-impressions"
        )[:3]
        page.top_queries = list(top_queries)

    return top_articles


def _get_articles_above_threshold(clicks_min: int = 10000, date: dt.date = None) -> int:
    # Get the amount of pages that were above clicks_min on date.
    gsc_clicks_above_min = (
        Page.objects.filter(data_gsc__date=date)
        .annotate(clicks_all=Sum("data_gsc__clicks"))
        .filter(
            clicks_all__gte=clicks_min,
        )
        .order_by(F("clicks_all").desc(nulls_last=True))
    )

    return gsc_clicks_above_min.count()


def run():

    date = local_yesterday()
    # For local testing in different time zone:
    # date = local_yesterday() - dt.timedelta(days=1)

    top_articles = _get_top_articles(3, date)

    if top_articles:
        logger.debug("Found top articles")
        articles_above_threshold = _get_articles_above_threshold(
            ARTICLE_THRESHOLD,
            date,
        )
        logger.debug(
            "Found {} articles above threshold".format(articles_above_threshold)
        )

        adaptive_card = _generate_adaptive_card(top_articles, articles_above_threshold)
        logger.debug(adaptive_card.to_json())
        payload = generate_teams_payload(adaptive_card)

        # Send payload to MS Teams
        result = send_to_teams(payload, WEBHOOK_URL)
        logger.debug(result)
    else:
        logger.info("No articles found, sending no message to Teams")
