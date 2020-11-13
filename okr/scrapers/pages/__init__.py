import re
import datetime as dt
from okr.scrapers.pages.gsc import fetch_day
from typing import Optional

from django.db.models import Q
from sentry_sdk import capture_exception

from okr.models.pages import Page, Property, PageDataGSC
from okr.scrapers.common.utils import date_range, local_today, local_yesterday


def scrape_full(property):
    print("Running full scrape of property", property)

    property_filter = Q(id=property.id)

    start_date = local_yesterday() - dt.timedelta(days=30)

    scrape_gsc(start_date=start_date, property_filter=property_filter)

    print("Finished full scrape of property", property)


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
        page_cache = {}

        for date in reversed(date_range(start_date, yesterday)):
            print(
                f"Start scrape Google Search Console data for property {property} from {date}."
            )
            data = fetch_day(property, date)
            for row in data:
                url, device = row["keys"]

                try:
                    match = re.match(r".*/(.*?)(?:~_page-(\d+))?\.(?:html|amp)$", url)

                    sophora_id = match.group(1)
                    # Cut off any other weird Sophora parameters
                    sophora_id = re.sub(f"~.*", "", sophora_id)

                    sophora_page = match.group(2)

                    if sophora_page is not None:
                        sophora_page = int(sophora_page)

                except AttributeError as error:
                    capture_exception(error)
                    continue

                if url in page_cache:
                    page = page_cache[url]
                else:
                    page, created = Page.objects.get_or_create(
                        url=url,
                        defaults=dict(
                            property=property,
                            sophora_id=sophora_id,
                            sophora_page=sophora_page,
                        ),
                    )
                    page_cache[url] = page

                PageDataGSC.objects.update_or_create(
                    page=page,
                    date=date,
                    device=device,
                    defaults=dict(
                        clicks=row["clicks"],
                        impressions=row["impressions"],
                        ctr=row["ctr"],
                        position=row["position"],
                    ),
                )

        print(f"Finished Google Search Console scrape for property {property}.")
