""" SEO Bot for to dos """

import datetime as dt
import os

from django.db.models import F, Sum
from loguru import logger

from okr.models.pages import (
    Page,
    PageDataQueryGSC,
    SophoraDocumentMeta,
    PageDataWebtrekk,
)
from okr.scrapers.common.utils import (
    local_yesterday,
    local_today,
)
from .teams_message import _generate_adaptive_card
from ..teams_tools import generate_teams_payload, send_to_teams

WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK_SEO_BOT")


def _get_pages(impressions_min: int = 10000, date: dt.date = None) -> Page:
    # Get all pages that had a certain number of impressions on a certain date.
    gsc_date = (
        Page.objects.filter(data_gsc__date=date)
        .annotate(impressions_all=Sum("data_gsc__impressions"))
        .annotate(clicks_all=Sum("data_gsc__clicks"))
        .filter(
            impressions_all__gt=impressions_min,
        )
        .order_by(F("impressions_all").desc(nulls_last=True))
    )

    return gsc_date


def _get_seo_articles_to_update(
    impressions_min: int = 10000, date: dt.date = None
) -> list:
    # Generate a list of pages that had at least a certain number of impressions
    # on a certain date and have not been updated today.

    today = local_today()

    pages = _get_pages(impressions_min, date)

    articles_to_do = []

    for page in pages:
        latest_meta = (
            SophoraDocumentMeta.objects.filter(sophora_document__sophora_id__page=page)
            .order_by("-editorial_update")
            .first()
        )

        if not latest_meta:
            logger.warning("No metas found for {}, skipping.", page.url)
            continue

        logger.info(
            'Potential update to-do found for "{}"" ({}, Standdatum {})',
            latest_meta.headline,
            page.url,
            latest_meta.editorial_update,
        )

        if latest_meta.editorial_update.date() == today:
            logger.info("But it's been updated today, so we're skipping it.")
            continue

        # Add data from latest_meta to page object
        page.latest_meta = latest_meta

        # Add webtrekk data to page object
        webtrekk_data = PageDataWebtrekk.objects.filter(
            webtrekk_meta__page=page,
            date=date,
        ).first()
        page.webtrekk_data = webtrekk_data

        # Add top Google queries
        top_queries = PageDataQueryGSC.objects.filter(page=page, date=date).order_by(
            "-impressions"
        )[:3]
        page.top_queries = list(top_queries)

        articles_to_do.append(page)

        if len(articles_to_do) == 5:
            break

    return articles_to_do


def run():
    # Generate list of Page objects that are potential to-do items
    articles_to_do = _get_seo_articles_to_update(10000, local_yesterday())
    # For testing, in case not enough articles have been scraped:
    # articles_to_do = _get_seo_articles_to_update(
    #     10000, local_yesterday() - dt.timedelta(days=1)
    # )

    adaptive_card = _generate_adaptive_card(articles_to_do)
    payload = generate_teams_payload(adaptive_card)

    # Send payload to MS Teams
    result = send_to_teams(payload, WEBHOOK_URL)
    logger.debug(result)
