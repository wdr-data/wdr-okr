"""Base module for page data scrapers."""

import re
import datetime as dt
from typing import Dict, Optional, Tuple
from time import sleep

from django.db.models import Q
from sentry_sdk import capture_exception
from rfc3986 import urlparse

from ...models import Property
from okr.models.pages import (
    Page,
    PageDataWebtrekk,
    PageWebtrekkMeta,
    Property,
    PropertyDataGSC,
    PageDataGSC,
    PageDataQueryGSC,
    SophoraNode,
    SophoraDocument,
    SophoraDocumentMeta,
    SophoraID,
)
from okr.scrapers.common.utils import (
    date_param,
    date_range,
    local_now,
    local_today,
    local_yesterday,
    BERLIN,
)
from okr.scrapers.pages import gsc, sophora, webtrekk


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


def _parse_sophora_url(url: str) -> Tuple[str, str, Optional[int]]:
    parsed = urlparse(url)
    match = re.match(r"(.*)/(.*?)(?:~_page-(\d+))?\.(?:html|amp)$", parsed.path)
    node = match.group(1)
    sophora_id = match.group(2)
    # Cut off any other weird Sophora parameters
    sophora_id = re.sub(f"~.*", "", sophora_id)
    if sophora_id == "index":
        sophora_id = f"{node}/{sophora_id}"

    sophora_page = match.group(3)
    if sophora_page is not None:
        sophora_page = int(sophora_page)
    return sophora_id, node, sophora_page


def _page_from_url(
    url: str,
    page_cache: Dict[str, Page],
    *,
    property: Optional[Property] = None,
) -> Optional[Page]:
    try:
        sophora_id_str, node, sophora_page = _parse_sophora_url(url)
    except AttributeError as error:
        capture_exception(error)
        return None

    if url in page_cache:
        return page_cache[url]
    else:
        sophora_id, created = SophoraID.objects.get_or_create(
            sophora_id=sophora_id_str,
            defaults=dict(
                sophora_document=None,
            ),
        )
        sophora_document = sophora_id.sophora_document

        page, created = Page.objects.get_or_create(
            url=url,
            defaults=dict(
                property=property,
                sophora_document=sophora_document,
                sophora_page=sophora_page,
                sophora_id=sophora_id,
                node=node,
            ),
        )
        page_cache[url] = page
        return page


def _property_data_gsc(property: Property, start_date: dt.date, end_date: dt.date):
    """Scrape from Google Search Console API and update
    :class:`~okr.models.pages.PropertyDataGSC` of the database models.

    Args:
        property (Property): Selected property.
        start_date (dt.date): Start date to request data for.
        end_date (dt.date): End date to request data for.
    """

    data = gsc.fetch_data(
        property, start_date, end_date=end_date, dimensions=["date", "device"]
    )

    for row in data:
        date, device = row["keys"]

        PropertyDataGSC.objects.update_or_create(
            property=property,
            date=dt.date.fromisoformat(date),
            device=device,
            defaults=dict(
                clicks=row["clicks"],
                impressions=row["impressions"],
                ctr=row["ctr"],
                position=row["position"],
            ),
        )


def _page_data_gsc(property: Property, date: dt.date, page_cache: Dict[str, Page]):
    """Scrape from Google Search Console API and update
    :class:`~okr.models.pages.Page` and :class:`~okr.models.pages.PageDataGSC`
    of the database models.

    Args:
        property (Property): Selected property.r.
        page_cache (Dict[str, Page]): Cache for url to page mapping.
    """

    data = gsc.fetch_data(property, date)
    for row in data:
        url, device = row["keys"]

        page = _page_from_url(url, page_cache, property=property)

        if page is None:
            continue

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


def _page_data_query_gsc(
    property: Property, date: dt.date, page_cache: Dict[str, Page]
):
    """Scrape from Google Search Console API and update
    :class:`~okr.models.pages.Page` and
    :class:`~okr.models.pages.PageDataQueryGSC` of the database models.

    Args:
        property (Property): Selected property.
        date (dt.date): Date to request data for.
        page_cache (Dict[str, Page]): Cache for url to page mapping.
    """

    data = gsc.fetch_data(property, date, dimensions=["page", "query"])
    for row in data:
        url, query = row["keys"]

        page = _page_from_url(url, page_cache, property=property)

        if page is None:
            continue

        PageDataQueryGSC.objects.update_or_create(
            page=page,
            date=date,
            query=query,
            defaults=dict(
                clicks=row["clicks"],
                impressions=row["impressions"],
                ctr=row["ctr"],
                position=row["position"],
            ),
        )


def scrape_gsc(
    *,
    start_date: Optional[dt.date] = None,
    property_filter: Optional[Q] = None,
):
    """Scrape from Google Search Console API.

    Args:
        start_date (Optional[dt.date], optional): Earliest date to request data for.
          Defaults to None. Will be set to two days before yesterday if None.
        property_filter (Optional[Q], optional): Filter to select a subset of
          properties. Defaults to None.
    """
    today = local_today()
    yesterday = local_yesterday()

    start_date = date_param(
        start_date,
        default=yesterday - dt.timedelta(days=2),
        earliest=today - dt.timedelta(days=30),
        latest=yesterday,
    )

    properties = Property.objects.all()

    if property_filter:
        properties = properties.filter(property_filter)

    for property in properties:
        page_cache = {}

        _property_data_gsc(property, start_date, yesterday)

        for date in reversed(date_range(start_date, yesterday)):
            print(
                f"Start scrape Google Search Console data for property {property} from {date}."
            )
            _page_data_gsc(property, date, page_cache)
            _page_data_query_gsc(property, date, page_cache)

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
        # Sometimes this is not set to sane value
        if sophora_document_info["lastModified"] < 1:
            editorial_update = None
        else:
            editorial_update = dt.datetime.fromtimestamp(
                sophora_document_info["lastModified"] / 1000,
                tz=BERLIN,
            )

        headline = sophora_document_info["title"]
        teaser = "\n".join(sophora_document_info.get("teaserText", []))

    elif sophora_document_info.get("mediaType") == "imageGallery":
        editorial_update = None
        headline = sophora_document_info["schlagzeile"]
        teaser = "\n".join(sophora_document_info["teaserText"])

    elif sophora_document_info.get("mediaType") == "link":
        return True

    else:
        try:
            raise Exception("Unknown page type")
        except Exception as e:
            capture_exception(e)

        print(sophora_document_info)
        return True

    # Cancel when editorial update is too old
    if editorial_update is not None and editorial_update < max_age:
        print(
            f"Done scraping this feed. editorial_update: {editorial_update}, max_age={max_age}"
        )
        print(sophora_document_info)
        return False

    # Parse Sophora ID, uuid and documentType
    if "teaser" in sophora_document_info:
        contains_info = sophora_document_info["teaser"]
    else:
        contains_info = sophora_document_info

    try:
        sophora_id_str, node, _ = _parse_sophora_url(contains_info["shareLink"])
    except KeyError as error:
        # Don't send error to Sentry for image galleries
        if contains_info.get("mediaType") == "imageGallery":
            return True

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

    sophora_id, created = SophoraID.objects.get_or_create(
        sophora_id=sophora_id_str,
        defaults=dict(
            sophora_document=sophora_document,
        ),
    )

    if sophora_id.sophora_document is None:
        sophora_id.sophora_document = sophora_document
        sophora_id.save()

    SophoraDocumentMeta.objects.get_or_create(
        sophora_document=sophora_document,
        headline=headline,
        teaser=teaser,
        document_type=document_type,
        sophora_id=sophora_id,
        node=node,
        defaults=dict(
            editorial_update=editorial_update,
        ),
    )
    return True


def scrape_sophora_nodes(*, sophora_node_filter: Optional[Q] = None):
    """Scrape data from Sophora API to discover new documents to store as
    :class:`~okr.models.pages.SophoraDocument`.

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
                SophoraDocumentMeta.objects.all()
                .filter(sophora_document__sophora_node=sophora_node)
                .exclude(editorial_update=None)
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


def scrape_webtrekk(
    *,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
):
    """Load webtrekk report and transfer it into database
    (:class:`~okr.models.pages.PageWebtrekkMeta` and
    :class:`~okr.models.pages.PageDataWebtrekk`).
    """
    today = local_today()
    yesterday = local_yesterday()

    start_date = date_param(
        start_date,
        default=yesterday - dt.timedelta(days=1),
        earliest=today - dt.timedelta(days=30),
        latest=yesterday,
    )

    end_date = date_param(
        end_date,
        default=yesterday,
        earliest=start_date,
        latest=today,
    )

    page_cache = {}

    try:
        property = Property.objects.get(url="https://www1.wdr.de/nachrichten/")
    except Property.DoesNotExist:
        property = None

    for date in reversed(date_range(start_date, end_date)):
        print(f"Start Webtrekk SEO scrape for {date}.")
        data = webtrekk.cleaned_webtrekk_page_data(date)

        for key, item in data.items():
            url, headline, query = key

            page = _page_from_url(url, page_cache, property=property)

            if page is None:
                continue

            webtrekk_meta, created = PageWebtrekkMeta.objects.get_or_create(
                page=page,
                headline=headline,
                query=query or "",
            )

            PageDataWebtrekk.objects.update_or_create(
                date=date,
                webtrekk_meta=webtrekk_meta,
                defaults=dict(
                    visits=item.get("visits", 0),
                    entries=item.get("entries", 0),
                    visits_campaign=item.get("visits_campaign", 0),
                    bounces=item.get("bounces", 0),
                    length_of_stay=dt.timedelta(seconds=item.get("length_of_stay", 0)),
                    impressions=item.get("impressions", 0),
                    exits=item.get("exits", 0),
                    visits_search=item.get("visits_search", 0),
                    entries_search=item.get("entries_search", 0),
                    visits_campaign_search=item.get("visits_campaign_search", 0),
                    bounces_search=item.get("bounces_search", 0),
                    length_of_stay_search=dt.timedelta(
                        seconds=item.get("length_of_stay_search", 0)
                    ),
                    impressions_search=item.get("impressions_search", 0),
                    exits_search=item.get("exits_search", 0),
                ),
            )

    print(f"Finished Webtrekk SEO scrape")
