""" Init module"""

import re
import datetime as dt
from typing import Dict, Optional, Tuple
from time import sleep
from urllib.parse import urlparse

from django.db.models import Q
from sentry_sdk import capture_exception

from ...models import Property
from okr.models.pages import (
    Page,
    Property,
    PageDataGSC,
    SophoraNode,
    SophoraDocument,
    SophoraDocumentMeta,
    SophoraID,
)
from okr.scrapers.common.utils import (
    date_range,
    local_now,
    local_today,
    local_yesterday,
    BERLIN,
)
from okr.scrapers.pages import gsc, sophora


def scrape_full_gsc(property: Property):
    """Run full scrape of property from GSC API (most recent 30 days).

    Args:
        property (Property): Property to scrape data for.
    """
    print("Running full scrape of property", property)

    property_filter = Q(id=property.id)

    start_date = local_yesterday() - dt.timedelta(days=30)

    sleep(1)
    scrape_gsc(start_date=start_date, property_filter=property_filter)

    # sleep(1)
    # scrape_sophora(property_filter=property_filter)

    print("Finished full scrape of property", property)


def scrape_full_sophora(sophora_node: SophoraNode):
    """Run full scrape of node from Sophora API.

    Args:
        sophora_node (SophoraNode): Sophora node to scrape data for.
    """
    print("Running full scrape of Sophora node", sophora_node)

    sophora_node_filter = Q(id=sophora_node.id)

    sleep(1)
    scrape_sophora_nodes(sophora_node_filter=sophora_node_filter)

    print("Finished full scrape of Sophora node", sophora_node)


def _parse_sophora_url(url: str) -> Tuple[str, Optional[int]]:
    parsed = urlparse(url)
    match = re.match(r"(.*)/(.*?)(?:~_page-(\d+))?\.(?:html|amp)$", parsed.path)
    node = match.group(1)
    sophora_id = match.group(2)
    # Cut off any other weird Sophora parameters
    sophora_id = re.sub(f"~.*", "", sophora_id)
    sophora_page = match.group(3)
    if sophora_page is not None:
        sophora_page = int(sophora_page)
    return sophora_id, node, sophora_page


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
                    sophora_id, node, sophora_page = _parse_sophora_url(url)
                except AttributeError as error:
                    capture_exception(error)
                    continue

                if url in page_cache:
                    page = page_cache[url]
                else:
                    try:
                        sophora_document = SophoraID.objects.get(
                            sophora_id=sophora_id,
                        ).sophora_document
                    except SophoraID.DoesNotExist:
                        sophora_document = None

                    page, created = Page.objects.get_or_create(
                        url=url,
                        defaults=dict(
                            property=property,
                            sophora_document=sophora_document,
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


def _handle_sophora_document(
    sophora_node: SophoraNode,
    sophora_document_info: Dict,
    max_age: dt.datetime,
) -> bool:
    # Extract attributes depending on media type
    if "teaser" in sophora_document_info:
        editorial_update = dt.datetime.fromtimestamp(
            sophora_document_info["teaser"]["redaktionellerStand"],
            tz=BERLIN,
        )
        headline = sophora_document_info["teaser"]["schlagzeile"]
        teaser = "\n".join(sophora_document_info["teaser"]["teaserText"])

    elif sophora_document_info.get("mediaType") in ["audio", "video"]:
        editorial_update = dt.datetime.fromtimestamp(
            sophora_document_info["lastModified"] / 1000,
            tz=BERLIN,
        )
        headline = sophora_document_info["title"]
        teaser = "\n".join(sophora_document_info.get("teaserText", []))

    elif sophora_document_info.get("mediaType") in ["link", "imageGallery"]:
        return True

    else:
        try:
            raise Exception("Unknown page type")
        except Exception as e:
            capture_exception(e)

        print(sophora_document_info)
        return True

    if editorial_update is not None and editorial_update < max_age:
        return False

    # Parse Sophora ID and uuid
    if "teaser" in sophora_document_info:
        contains_info = sophora_document_info["teaser"]
    else:
        contains_info = sophora_document_info

    try:
        sophora_id, node, _ = _parse_sophora_url(contains_info["shareLink"])
    except KeyError as error:
        print("No shareLink found:")
        print(sophora_document_info)
        capture_exception(error)
        return True
    except AttributeError as error:
        capture_exception(error)
        return True

    export_uuid = contains_info["uuid"]

    try:
        document_type = contains_info.get("mediaType")
    except Exception as error:
        print(sophora_document_info)
        capture_exception(error)
        return True

    sophora_document, created = SophoraDocument.objects.get_or_create(
        export_uuid=export_uuid,
        defaults=dict(
            sophora_node=sophora_node,
        ),
    )

    sophora_id_obj, created = SophoraID.objects.get_or_create(
        sophora_id=sophora_id,
        defaults=dict(
            sophora_document=sophora_document,
        ),
    )

    SophoraDocumentMeta.objects.get_or_create(
        sophora_document=sophora_document,
        editorial_update=editorial_update,
        defaults=dict(
            headline=headline,
            teaser=teaser,
            sophora_id=sophora_id,
            node=node,
            document_type=document_type,
        ),
    )
    return True


def scrape_sophora_nodes(*, sophora_node_filter: Optional[Q] = None):
    """Scrape data from Sophora API to discover new SophoraDocuments.

    Args:
        sophora_node_filter (Optional[Q], optional): Filter to select a subset of
          sophora_nodes. Defaults to None.
    """

    now = local_now()

    sophora_nodes = SophoraNode.objects.all()

    if sophora_node_filter:
        sophora_nodes = sophora_nodes.filter(sophora_node_filter)

    for sophora_node in sophora_nodes:
        print(f"Scraping Sophora API for pages of {sophora_node}")

        if sophora_node.documents.count() == 0:
            print("No existing documents found, search history")
            max_age = now - dt.timedelta(days=365)
        else:
            max_age = (
                sophora_node.documents.all()
                .order_by("-editorial_update")[0]
                .editorial_update
            ) - dt.timedelta(minutes=1)

        print("Scraping exact node matches")
        for sophora_document_info in sophora.get_documents_in_node(
            sophora_node,
            force_exact=True,
        ):
            should_continue = _handle_sophora_document(
                sophora_node,
                sophora_document_info,
                max_age,
            )
            if not should_continue:
                break

        if sophora_node.use_exact_search:
            continue

        print("Scraping sub-node matches")
        for sophora_document_info in sophora.get_documents_in_node(sophora_node):
            should_continue = _handle_sophora_document(
                sophora_node,
                sophora_document_info,
                max_age,
            )
            if not should_continue:
                break
