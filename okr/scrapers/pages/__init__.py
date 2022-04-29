"""Base module for page data scrapers."""

import re
import datetime as dt
from typing import Dict, Optional, Tuple
from time import sleep

from django.db.models import Q
from loguru import logger
from sentry_sdk import capture_exception, capture_message, push_scope
from rfc3986 import urlparse
from urllib.parse import unquote

import sentry_sdk

from okr.models.pages import (
    Page,
    PageDataWebtrekk,
    PageWebtrekkMeta,
    Property,
    PropertyDataGSC,
    PropertyDataQueryGSC,
    PageDataGSC,
    PageDataQueryGSC,
    SophoraNode,
    SophoraDocument,
    SophoraDocumentMeta,
    SophoraID,
    SophoraKeyword,
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
    logger.info("Running full scrape of property {}", property)

    property_filter = Q(id=property.id)

    start_date = local_yesterday() - dt.timedelta(days=30)

    sleep(1)
    scrape_gsc(start_date=start_date, property_filter=property_filter)

    logger.success("Finished full scrape of property {}", property)


def scrape_full_sophora(sophora_node: SophoraNode):
    """Run full scrape of node from Sophora API.

    Args:
        sophora_node (SophoraNode): Sophora node to scrape data for.
    """
    logger.info("Running full scrape of Sophora node {}", sophora_node)

    sophora_node_filter = Q(id=sophora_node.id)

    sleep(1)
    scrape_sophora_nodes(sophora_node_filter=sophora_node_filter)

    logger.success("Finished full scrape of Sophora node {}", sophora_node)


class SkipPageException(Exception):
    pass


def _parse_sophora_url(url: str) -> Tuple[str, str, Optional[int]]:

    # Special cases
    if url == "https://www1.wdr.de/nachrichten/nrw":
        # TODO: Investigate if there are more like this
        url = "https://www1.wdr.de/nachrichten/index.html"

    # Ensure that overview pages with missing "index.html" suffix
    # get related to the same SophoraID
    if url.endswith("/"):
        logger.debug("Adding index.html suffix")
        url = url + "index.html"

    parsed = urlparse(url)
    match = re.match(
        r"(.*)/(.*?)(?:~_page-(\d+))?\.(?:html|amp)$",
        unquote(parsed.path),
    )

    if match is None:
        # Parsing errors that are known and we want to ignore
        match_expected = re.match(
            r".*\.(?:jsp|pdf|news)$",
            unquote(parsed.path),
        ) or re.match(
            r".*/:~:text=.*$",
            unquote(parsed.path),
        )

        if match_expected is None:
            logger.error("Unexpected parsing error: {}", url)
            sentry_sdk.capture_message(
                f"Failed parsing URL with unexpected format: {url}",
                level="error",
            )
        else:
            logger.debug("Ignored parsing error: {}", url)

        raise SkipPageException(url)

    node = match.group(1)
    sophora_id = match.group(2)
    # Cut off any other weird Sophora parameters
    sophora_id = re.sub(r"~.*", "", sophora_id)
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
    except SkipPageException:
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

        if created:
            # Best-effort attempt at connecting this SophoraID to an existing SophoraDocument
            # Will fail most of the time, probably
            try:
                sophora_data = sophora.get_document_by_sophora_id(sophora_id_str)
                uuid = sophora_data["teaser"]["uuid"]
                sophora_document = SophoraDocument.objects.filter(
                    export_uuid=uuid
                ).first()

                if sophora_document:
                    sophora_id.sophora_document = sophora_document
                    sophora_id.save()

                    with push_scope() as scope:
                        scope.set_context(
                            "info",
                            {
                                "url": url,
                                "sophora_id": sophora_id_str,
                            },
                        )
                        capture_message(
                            "Added new URL that has not been seen by Sophora API scraper"
                        )
            except Exception as e:
                capture_exception(e)

        page, created = Page.objects.get_or_create(
            url=url,
            defaults=dict(
                property=property,
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

    logger.info("Getting Property Data...")

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


def _property_data_query_gsc(property: Property, date: dt.date):
    """Scrape data from Google Search Console API and update
    :class:`~okr.models.pages.PropertyDataQueryGSC` of the database models.

        Args:
            property (Property): Property to request data for.
            date (dt.date): The date to request data for.
    """

    logger.info("Getting Property Query Data...")

    data = gsc.fetch_data(property, date, dimensions=["query"])

    for row in data:
        (query,) = row["keys"]

        PropertyDataQueryGSC.objects.update_or_create(
            property=property,
            date=date,
            query=query,
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

    logger.info("Getting Page Data...")

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

    logger.info("Getting Page Query Data...")

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
        logger.info(
            "Start scrape Google Search Console data for property {}.",
            property,
        )

        page_cache = {}

        try:
            _property_data_gsc(property, start_date, yesterday)
        except Exception as e:
            capture_exception(e)

        for date in reversed(date_range(start_date, yesterday)):
            logger.info("Scraping data for {}.", date)

            # Get page data first to ensure scrape is done before SEO bot runs
            try:
                _page_data_gsc(property, date, page_cache)
            except Exception as e:
                capture_exception(e)

            try:
                _page_data_query_gsc(property, date, page_cache)
            except Exception as e:
                capture_exception(e)

            try:
                _property_data_query_gsc(property, date)
            except Exception as e:
                capture_exception(e)

        logger.success(
            "Finished Google Search Console scrape for property {}.",
            property,
        )


def _count_words(string: str) -> int:
    """Counts words. Hyphenated words are counted as separate words."""
    return len(re.findall(r"\w+", string))


def _handle_sophora_document(  # noqa: C901
    sophora_node: SophoraNode,
    sophora_document_info: Dict,
    *,
    is_first_run: bool = False,
) -> None:
    # Extract attributes depending on media type
    tags = []

    if "teaser" in sophora_document_info:
        editorial_update = dt.datetime.fromtimestamp(
            sophora_document_info["teaser"]["redaktionellerStand"],
            tz=BERLIN,
        )
        headline = sophora_document_info["teaser"]["schlagzeile"]
        teaser = "\n".join(sophora_document_info["teaser"]["teaserText"])

        tags = sophora_document_info["teaser"].get("tags", [])

        # Detect if API export parsing is still broken
        if "," in " ".join(tags):
            # Fix broken tags and normalize
            tags = " ".join(tags).lower().split(", ")
            tags = [tag.strip() for tag in tags]
        else:
            # Normalize only
            tags = [tag.lower().strip() for tag in tags]

    elif sophora_document_info.get("mediaType") == "uebersicht":
        editorial_update = None
        headline = sophora_document_info.get("seitenTitel", sophora_document_info.get("title"))
        teaser = sophora_document_info["beschreibung"]

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
        return

    else:
        try:
            raise Exception("Unknown page type")
        except Exception as e:
            capture_exception(e)

        logger.warning("Unknown page type:")
        logger.info(sophora_document_info)
        return

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
            return

        logger.exception("No shareLink found:")
        logger.info(sophora_document_info)
        capture_exception(error)
        return
    except SkipPageException:
        return

    export_uuid = contains_info["uuid"]

    try:
        document_type = contains_info["mediaType"]
    except KeyError as error:
        logger.exception(
            "Couldn't find mediaType in document {}",
            sophora_document_info,
        )
        capture_exception(error)
        return

    # Count the number of words in the body text (copytext and subheadlines)
    found_paragraphs = False
    word_count = 0
    paragraph_filter = ["copytext", "headline"]

    if "detail" in sophora_document_info:
        for paragraph in sophora_document_info["detail"]["messageBody"]:
            if paragraph["paragraphType"] in paragraph_filter:
                found_paragraphs = True
                word_count += _count_words(paragraph["paragraphValue"])

    elif "galleryBody" in sophora_document_info:
        for paragraph in sophora_document_info["galleryBody"]:
            if paragraph["paragraphType"] in paragraph_filter:
                found_paragraphs = True
                word_count += _count_words(paragraph["paragraphValue"])

    if word_count == 0 and not found_paragraphs:
        word_count = None

    # Create objects in DB
    sophora_document, created = SophoraDocument.objects.get_or_create(
        export_uuid=export_uuid,
        defaults=dict(
            sophora_node=sophora_node,
        ),
    )

    # Send message to Sentry about new documents with old editorial update timestamp
    if (
        not is_first_run
        and document_type == "beitrag"
        and created
        and editorial_update < local_now() - dt.timedelta(minutes=30)
    ):
        with push_scope() as scope:
            discrepancy = local_now() - editorial_update
            scope.set_context(
                "extracted_info",
                {
                    "url": contains_info.get("shareLink"),
                    "sophora_id": sophora_id_str,
                    "node": node,
                    "headline": headline,
                    "teaser": teaser,
                    "editorial_update": editorial_update.astimezone(BERLIN).isoformat(),
                    "discrepancy": discrepancy,
                    "discrepancy_hours": round(
                        discrepancy.total_seconds() / 60 / 60,
                        1,
                    ),
                },
            )
            logger.debug("New document with old editorial_update")
            capture_message("New document with old editorial_update")

    sophora_id, created = SophoraID.objects.get_or_create(
        sophora_id=sophora_id_str,
        defaults=dict(
            sophora_document=sophora_document,
        ),
    )

    if sophora_id.sophora_document is None:
        sophora_id.sophora_document = sophora_document
        sophora_id.save()

    sophora_document_meta, created = SophoraDocumentMeta.objects.get_or_create(
        sophora_document=sophora_document,
        headline=headline,
        teaser=teaser,
        word_count=word_count,
        keywords_list=", ".join(tags),
        document_type=document_type,
        sophora_id=sophora_id,
        node=node,
        defaults=dict(
            editorial_update=editorial_update,
        ),
    )

    for keyword in tags:
        sophora_keyword, created = SophoraKeyword.objects.get_or_create(
            keyword=keyword,
        )
        sophora_document_meta.keywords.add(sophora_keyword)


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
        logger.info("Scraping Sophora API for pages of {}", sophora_node)

        is_first_run = False

        if sophora_node.documents.count() == 0:
            logger.info("No existing documents found, search history")
            max_age = now - dt.timedelta(days=365)
            is_first_run = True
        else:
            max_age = (
                SophoraDocumentMeta.objects.all()
                .filter(sophora_document__sophora_node=sophora_node)
                .order_by("-created")
                .first()
                .created
            ) - dt.timedelta(minutes=5)

        logger.info("Scraping exact node matches")
        logger.debug("max_age: {}", max_age)
        for sophora_document_info in sophora.get_documents_in_node(
            sophora_node,
            max_age=max_age,
            force_exact=True,
        ):
            _handle_sophora_document(
                sophora_node,
                sophora_document_info,
                is_first_run=is_first_run,
            )

        logger.success("Done scraping exact node matches")

        if sophora_node.use_exact_search:
            continue

        logger.info("Scraping sub-node matches")
        for sophora_document_info in sophora.get_documents_in_node(
            sophora_node,
            max_age=max_age,
        ):
            _handle_sophora_document(
                sophora_node,
                sophora_document_info,
                is_first_run=is_first_run,
            )

        logger.success("Done scraping sub-node matches")


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
        logger.info("Start Webtrekk SEO scrape for {}.", date)

        try:
            data = webtrekk.cleaned_webtrekk_page_data(date)
        except Exception as e:
            capture_exception(e)
            continue

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

    logger.success("Finished Webtrekk SEO scrape")
