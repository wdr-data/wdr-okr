""" Init module"""

import re
import datetime as dt
from typing import Optional
from time import sleep
from json.decoder import JSONDecodeError

from django.db.models import Q
from sentry_sdk import capture_exception

from ...models import Property
from okr.models.pages import Page, PageMeta, Property, PageDataGSC
from okr.scrapers.common.utils import date_range, local_today, local_yesterday, BERLIN
from okr.scrapers.pages import gsc, sophora


def scrape_full(property: Property):
    """Run full scrape of property from Google and Sophora APIs (most recent 30 days).

    Args:
        property (Property): Property to scrape data for.
    """
    print("Running full scrape of property", property)

    property_filter = Q(id=property.id)

    start_date = local_yesterday() - dt.timedelta(days=30)

    sleep(1)
    scrape_gsc(start_date=start_date, property_filter=property_filter)

    sleep(1)
    scrape_sophora(property_filter=property_filter)

    print("Finished full scrape of property", property)


def scrape_gsc(
    *,
    start_date: Optional[dt.date] = None,
    property_filter: Optional[Q] = None,
):
    """Scrape from Google Search Console API and update Page and PageDataGSC in the
    database.

    Args:
        start_date (Optional[dt.date], optional): Earliest date to request data for.
          Defaults to None. Will be set to two days before yesterday if None.
        property_filter (Optional[Q], optional): Filter to select a subset of
          properties. Defaults to None.
    """
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
            data = gsc.fetch_day(property, date)
            for row in data:
                url, device = row["keys"]

                # Match Google data to Sophora ID, if possible
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


def scrape_sophora(*, property_filter: Optional[Q] = None):
    """Scrape data from Sophora API and update PageMeta.

    Args:
        property_filter (Optional[Q], optional): Filter to select a subset of
          properties. Defaults to None.
    """
    properties = Property.objects.all()

    if property_filter:
        properties = properties.filter(property_filter)

    for property in properties:
        print(f"Scraping Sophora API for pages of {property}")

        for page in property.pages.all():
            if page.sophora_id == "index":
                continue

            if len(page.metas.all()) > 0:
                print("skipping")
                continue

            try:
                sophora_page = sophora.get_page(page)
            except JSONDecodeError:
                print(f"Failed to decode JSON response for page {page}")
                continue

            if "userMessage" in sophora_page:
                print(sophora_page["userMessage"], page.url)
                continue

            if "teaser" in sophora_page:
                editorial_update = dt.datetime.fromtimestamp(
                    sophora_page["teaser"]["redaktionellerStand"],
                    tz=BERLIN,
                )
                headline = sophora_page["teaser"]["schlagzeile"]
                teaser = "\n".join(sophora_page["teaser"]["teaserText"])

            elif sophora_page.get("mediaType") == "imageGallery":
                editorial_update = None
                headline = sophora_page["schlagzeile"]
                teaser = "\n".join(sophora_page["teaserText"])

            elif sophora_page.get("mediaType") in ["audio", "video"]:
                editorial_update = dt.datetime.fromtimestamp(
                    sophora_page["lastModified"] / 1000,
                    tz=BERLIN,
                )
                headline = sophora_page["title"]
                teaser = "\n".join(sophora_page.get("teaserText", []))

            else:
                try:
                    raise Exception("Unknown page type")
                except Exception as e:
                    capture_exception(e)

                print(page, sophora_page)
                continue

            PageMeta(
                page=page,
                editorial_update=editorial_update,
                headline=headline,
                teaser=teaser,
            ).save()
