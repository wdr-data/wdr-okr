import re
import datetime as dt
from okr.scrapers.pages.gsc import fetch_day
from typing import Optional

from django.db.models import Q

from okr.models.pages import Page, Property
from okr.scrapers.common.utils import date_range, local_today, local_yesterday


def scrape_gsc(
    *, start_date: Optional[dt.date] = None, property_filter: Optional[Q] = None
):
    today = local_today()
    yesterday = local_yesterday()

    if start_date is None:
        start_date = yesterday - dt.timedelta(days=2)

    start_date = max(start_date, today - dt.timedelta(days=30))
    start_date = min(start_date, yesterday)

    properties = Property.objects.all()

    if property_filter:
        properties = properties.filter(property_filter)

    for property in properties:
        for date in reversed(date_range(start_date, yesterday)):
            data = fetch_day(property, date)
            for row in data:
                page, device = row["keys"]
                try:
                    sophora_id = re.match(r".*?/(.*?)\.(?:html|amp)$", page).group(1)
                except AttributeError:
                    # TODO: Failed to parse, report to sentry
                    continue  # ?

                Page.objects.get_or_create(
                    property=property, date=date, defaults=dict()
                )
