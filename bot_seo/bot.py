import datetime as dt
import os

from django.db.models import F, Sum
import requests
from loguru import logger

from okr.models.pages import Page, SophoraDocumentMeta
from okr.scrapers.common.utils import (
    local_yesterday,
    local_today,
)

URL = os.environ.get("TEAMS_WEBHOOK")


def _get_pages(impressions_min: int = 10000, date: dt.date = None) -> Page:
    # get all pages that had a certain number of impressions on a certain date.
    gsc_date = (
        Page.objects.filter(data_gsc__date=date)
        .annotate(impressions_all=Sum("data_gsc__impressions"))
        .filter(
            impressions_all__gt=impressions_min,
        )
        .order_by(F("impressions_all").desc(nulls_last=True))
    )

    return gsc_date


def _get_seo_articles_to_update(impressions_min: int = 10000, date: dt.date = None):
    # generate a list of pages that had at least a certain number of impressions
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

        # add data from latest_meta to page object
        page.latest_meta = latest_meta
        articles_to_do.append(page)

        if len(articles_to_do) == 5:
            break

    return articles_to_do


def _generate_to_do_strings(articles: list) -> list:
    to_dos = []

    for article in articles:
        impressions = article.impressions_all
        headline = article.latest_meta.headline
        url = article.url
        to_dos.append(
            f'* Der Beitrag **"[{headline}]({url})"** hatte gestern **{"{:,}".format(impressions).replace(",",".")}** Suchmaschinen-Impressions und wurde heute noch nicht aktualisiert.'
        )

    return to_dos


def _generate_json_payload(messages: str) -> dict:
    # generate json payload to send to Teams
    payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": "Markup test",
        "sections": [
            {
                "title": "Hallo! Ich habe mir mal die Beiträge von gestern in der Search Console angesehen und habe folgende Vorschläge:"
            }
        ],
    }

    for message in messages:
        payload["sections"].append({"text": message})

    return payload


def _send_to_teams(payload: dict) -> requests.models.Response:
    return requests.post(URL, json=payload).raise_for_status()


def bot_seo():
    # Generate list of Page objects that are potential to-do items
    articles_to_do = _get_seo_articles_to_update(10000, local_yesterday())

    # Generate a list of sentences about the to-do items
    to_dos = _generate_to_do_strings(articles_to_do)

    # Generate payload for to-dos
    payload = _generate_json_payload(to_dos)

    # Send payload to MS Teams
    result = _send_to_teams(payload)
    logger.debug(result)
