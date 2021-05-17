""" Helper functions to generate a message for MS Teams. """

import os
import random

from pyadaptivecards.card import AdaptiveCard
from pyadaptivecards.container import ColumnSet, FactSet
from pyadaptivecards.components import Fact, TextBlock

from okr.models.pages import Page
from ..pyadaptivecards_tools import ActionSet, Container, Column, ToggleVisibility
from ..teams_tools import format_number, format_percent

GREETINGS = ["Hallo!", "Guten Tag!", "Hi!"]
MORE_URL = os.environ.get("SEO_BOT_TODO_MORE_URL")


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
                title="Mehr",
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
                verticalContentAlignment="center",
                width=77,
            ),
            Column(
                [button],
                verticalContentAlignment="center",
                width=23,
            ),
        ],
        id=f"summary_{page.id}",
        spacing="extralarge",
        separator=True,
    )

    story = Container(items=[summary, details], id=f"story_{page.id}", spacing="Large")

    return story


def _generate_adaptive_card(pages: Page) -> AdaptiveCard:
    # Generate intro
    greeting = random.choice(GREETINGS)
    intro = TextBlock(
        f"{greeting} Diese Beiträge von uns sind gestern mit Google gut gefunden worden und haben heute noch kein Update bekommen. **Lohnt sich eine Aktualisierung oder ein Weiterdreh?**",
        wrap=True,
    )

    # Generate outro
    outro = TextBlock(
        text=f"[Was bedeutet diese Nachricht?]({MORE_URL})",
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

    return card
