import datetime as dt
import json
import os

from django.db.models import F, Sum
import requests

from okr.models.pages import *
from okr.scrapers.common.utils import (
    local_yesterday,
    local_today,
    BERLIN,
)


def _get_pages(impressions_limit: int = 10000, date: dt.date = None) -> Page:
    gsc_yesterday = (
        Page.objects.filter(data_gsc__date=date)
        .annotate(impressions_all=Sum(F("data_gsc__impressions")))
        .filter(
            impressions_all__gt=impressions_limit,
        )
        .order_by(F("impressions_all").desc(nulls_last=True))
    )

    return gsc_yesterday


def get_seo_articles_to_update(impressions_limit: int = 10000, date: dt.date = None):
    pages = _get_pages(impressions_limit, date)

    articles_to_do = []

    for page in pages:
        document = page.sophora_id.sophora_document

        if not document:
            print(f"No document found for {page.url}")
            continue

        latest_meta = document.metas.all().order_by("-editorial_update").first()

        print(
            f'Potential update to-do found for "{latest_meta.headline}"" ({page.url}, Standdatum {latest_meta.editorial_update}'
        )

        if latest_meta.editorial_update.date() == local_today():
            continue

        articles_to_do.append(page)

        if len(articles_to_do) == 5:
            break

    return articles_to_do
