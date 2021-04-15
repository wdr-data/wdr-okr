""" Helper functions to generate a message for MS Teams. """

import random
from typing import Optional, Union

from pyadaptivecards.actions import OpenUrl
from pyadaptivecards.card import AdaptiveCard
from pyadaptivecards.container import ColumnSet, FactSet
from pyadaptivecards.components import Fact, TextBlock, Column
from django.utils.numberformat import format

from okr.models.pages import Page
from .pyadaptivecards_tools import ActionSet, Container, ToggleVisibility

GREETINGS = ["Hallo!", "Guten Tag!", "Hi!"]


def format_number(number: Union[int, float], decimal_places: Optional[int] = None):
    if decimal_places is not None:
        number = round(number, decimal_places)

    return format(
        number,
        decimal_sep=",",
        thousand_sep=".",
        force_grouping=True,
        grouping=3,
    )


def format_percent(number: Union[int, float], decimal_places: Optional[int] = 1):
    formatted_number = format_number(number, decimal_places=decimal_places)
    return f"{formatted_number} %"


def _generate_details(page: Page) -> Container:

    facts = []

    facts.append(
        Fact(
            "Top 3 Google Suchanfragen",
            ", ".join(query_data.query for query_data in page.top_queries),
        )
    )

    fact_set = FactSet(facts)

    title_columns = [
        Column(
            items=[
                TextBlock(
                    "Impressions (GSC)",
                    weight="bolder",
                    size="small",
                    wrap=True,
                )
            ],
            width=100,
        ),
        Column(
            items=[
                TextBlock(
                    "CTR (GSC)",
                    weight="bolder",
                    size="small",
                    wrap=True,
                )
            ],
            width=100,
        ),
    ]

    # Calculate total CTR across all devices
    ctr = page.clicks_all / page.impressions_all * 100

    value_columns = [
        Column(
            items=[
                TextBlock(
                    format_number(page.impressions_all),
                    size="extralarge",
                    wrap=True,
                )
            ],
            width=100,
        ),
        Column(
            items=[
                TextBlock(
                    format_percent(ctr),
                    size="extralarge",
                    wrap=True,
                )
            ],
            width=100,
        ),
    ]

    # webtrekk_data can be None because Webtrekk is bad
    if page.webtrekk_data:
        title_columns.append(
            Column(
                items=[
                    TextBlock(
                        "Anteil Suchmaschinen (Webtrekk)",
                        weight="bolder",
                        size="small",
                        wrap=True,
                    )
                ],
                width=150,
            )
        )

        webtrekk_search_share = (
            page.webtrekk_data.visits_search / page.webtrekk_data.visits * 100
        )

        value_columns.append(
            Column(
                items=[
                    TextBlock(
                        format_percent(webtrekk_search_share),
                        size="extralarge",
                        wrap=True,
                    )
                ],
                width=150,
            ),
        )

    column_set_titles = ColumnSet(columns=title_columns, spacing="None")
    column_set_values = ColumnSet(columns=value_columns)

    details = Container(
        items=[
            fact_set,
            column_set_values,
            column_set_titles,
        ],
        id=f"details_{page.id}",
        isVisible=False,
    )

    return details


def _generate_story(page: Page) -> Container:

    details = _generate_details(page)

    headline = TextBlock(
        f"[{page.latest_meta.headline}]({page.url}) (Stand: {page.latest_meta.editorial_update.strftime('%d.%m., %H:%M')})",
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
        id=f"summary_{page.id}",
        spacing="extralarge",
        separator=True,
    )

    story = Container(items=[summary, details], id=f"story_{page.id}", spacing="Large")

    return story


def _generate_adaptive_card(pages: Page) -> dict:
    # Generate intro
    greeting = random.choice(GREETINGS)
    intro = TextBlock(
        f"{greeting} Bei den folgenden Texten der vergangenen Tage könnte sich ein Update für SEO lohnen:",
        wrap=True,
    )

    # Generate outro
    outro = ActionSet(
        actions=[
            OpenUrl(
                # TODO: create sharepoint page and add link here
                url="https://en.wikipedia.org/wiki/SharePoint",
                title="Was bedeutet diese Nachricht?",
            )
        ],
        horizontalAlignment="right",
        spacing="extralarge",
    )

    # Generate sections for each page
    stories = []

    for i, page in enumerate(pages):
        story = _generate_story(page)

        # Add separators between stories
        if i > 0:
            story.separator = True

        stories.append(story)

    # Put everything together
    adaptive_card_body = [intro, *stories, outro]
    card = AdaptiveCard(body=adaptive_card_body)

    return card.to_dict()


def generate_teams_payload(pages: Page) -> dict:
    """Generate payload for MS Teams.

    Args:
        pages (Page): Pages to generate text for.

    Returns:
        dict: Payload dict for MS Teams.
    """

    # Generate adaptive card
    adaptive_card = _generate_adaptive_card(pages)

    # Add adaptive card to payload
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
