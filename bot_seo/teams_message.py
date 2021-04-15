""" Helper functions to generate a message for MS Teams. """

import random

from pyadaptivecards.actions import OpenUrl
from pyadaptivecards.card import AdaptiveCard
from pyadaptivecards.container import ColumnSet
from pyadaptivecards.components import TextBlock, Column

from django.utils.numberformat import format

from okr.models.pages import Page
from .pyadaptivecards_tools import ActionSet, Container, ToggleVisibility

GREETINGS = ["Hallo!", "Guten Tag!", "Hi!"]


def _generate_story(page: Page) -> Container:

    # generate uuid to make details unique
    uuid = page.sophora_document.export_uuid

    # format and parse data for message
    impressions_gsc = format(
        page.impressions_all,
        decimal_sep=",",
        thousand_sep=".",
        force_grouping=True,
        grouping=3,
    )
    ctr = round(page.clicks_all / page.impressions_all * 100, 2)

    # webtrekk_data ist None für https://www1.wdr.de/nachrichten/themen/coronavirus/corona-virus-dortmund-hagen-hamm-recklinghausen-unna-104.html
    if page.webtrekk_data:
        webtrekk_search_share = round(
            page.webtrekk_data.visits_search / page.webtrekk_data.visits * 100, 2
        )

    facts = Container(
        items=[
            TextBlock(
                f"**Sophora ID:** {page.sophora_id.sophora_id}",
                wrap=True,
                size="Small",
                spacing=None,
            ),
            TextBlock(
                f"**Impressions (GSC):** {impressions_gsc}",
                wrap=True,
                size="Small",
                spacing=None,
            ),
            TextBlock(
                f"**CTR (GSC):** {ctr} %",
                wrap=True,
                size="Small",
                spacing=None,
            ),
            # TextBlock(
            #     f"**Anteil Suchmaschinen (Webtrekk):** {webtrekk_search_share} %",
            #     wrap=True,
            #     size="Small",
            #     spacing=None,
            # ),
        ]
    )

    # only include line about Webtrekk if Webtrekk data exists
    if page.webtrekk_data:
        facts.items.append(
            TextBlock(
                f"**Anteil Suchmaschinen (Webtrekk):** {webtrekk_search_share} %",
                wrap=True,
                size="Small",
                spacing=None,
            )
        )

    details = Container(
        items=[facts],
        id=uuid,
        isVisible=False,
    )

    headline = TextBlock(
        f"[{page.latest_meta.headline}]({page.url}) (Stand: {page.latest_meta.editorial_update.strftime('%d.%m, %H:%M')})",
        wrap=True,
    )
    button = ActionSet(
        actions=[
            ToggleVisibility(
                title="🔽",
                style="positive",
                targetElements=[details],
            )
        ],
        horizontalAlignment="Right",
    )

    summary = ColumnSet(
        columns=[
            Column(
                [headline],
                width="stretch",
                verticalContentAlignment="center",
            ),
            Column(
                [button],
                width="auto",
                verticalContentAlignment="center",
            ),
        ],
        id=uuid + "_summary",
        spacing="ExtraLarge",
        separator=True,
    )

    story_id = uuid + "_container"
    story = Container(items=[summary, details], id=story_id, spacing="Large")

    return story


def _generate_adaptive_card(pages: Page) -> dict:
    # generate intro
    greeting = random.choice(GREETINGS)
    intro = TextBlock(
        f"{greeting} Bei den folgenden Texten der vergangenen Tage könnte sich ein Update für SEO lohnen:",
        wrap=True,
    )

    # generate outro
    outro = ActionSet(
        actions=[
            OpenUrl(
                ## TODO: create sharepoint page and add link here
                url="https://en.wikipedia.org/wiki/SharePoint",
                title="Was bedeutet diese Nachricht?",
            )
        ],
        horizontalAlignment="Right",
    )

    adaptive_card_body = [intro]

    # generate sections for each page
    for page in pages:
        adaptive_card_body.append(_generate_story(page))

    # put everything together
    adaptive_card_body.append(outro)
    card = AdaptiveCard(body=adaptive_card_body)

    adaptive_card = card.to_dict()
    return adaptive_card


def generate_teams_payload(pages: Page) -> dict:
    """Generate payload for MS Teams.

    Args:
        pages (Page): Pages to generate text for.

    Returns:
        dict: Payload dict for MS Teams.
    """

    # generate adaptive card
    adaptive_card = _generate_adaptive_card(pages)

    # add adaptive card to payload
    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": "null",
                "content": adaptive_card,
            }
        ],
    }

    return payload
