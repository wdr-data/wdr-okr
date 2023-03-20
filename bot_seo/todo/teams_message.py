""" Helper functions to generate a message for MS Teams. """

import os
import random
import datetime as dt

from pyadaptivecards.card import AdaptiveCard
from pyadaptivecards.container import ColumnSet, FactSet
from pyadaptivecards.components import Fact, TextBlock

from okr.models.pages import Page
from okr.scrapers.common.utils import BERLIN, local_yesterday
from ..pyadaptivecards_tools import ActionSet, Container, Column, ToggleVisibility
from ..teams_tools import format_number, format_percent

GREETINGS = ["Hallo!", "Guten Tag!", "Hi!"]
MORE_URL = os.environ.get("SEO_BOT_TODO_MORE_URL")


def _generate_details(page: Page) -> Container:
    facts = []

    facts.append(
        Fact(
            "Top 5 Google Suchanfragen",
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


def _generate_adaptive_card(pages: Page, last_update_gsc: str = None) -> AdaptiveCard:
    # Convert PDT timezone to Berlin time, because GSC-times are all PDT-based
    PDT = dt.timezone(-dt.timedelta(hours=7))
    yesterday = local_yesterday()
    start_time = dt.datetime(yesterday.year, yesterday.month, yesterday.day, tzinfo=PDT)
    start_time_local = start_time.astimezone(BERLIN)

    # Generate intro
    greeting = random.choice(GREETINGS)
    intro = TextBlock(
        (
            f"{greeting} Diese Beiträge von uns sind seit gestern, {start_time_local.hour}:00 Uhr, "
            "mit Google gut gefunden worden und haben heute noch kein Update bekommen. "
            "**Lohnt sich eine Aktualisierung oder ein Weiterdreh?**"
        ),
        wrap=True,
    )

    # Add note about GSC data
    note_gsc = Container(
        [
            TextBlock(
                text=(f"Letzter Datenabgleich mit der GSC: {last_update_gsc} Uhr"),
                spacing="None",
                wrap=True,
            ),
            TextBlock(
                text=(
                    "Es dauert bis zu 48 Stunden, bis die Daten in der GSC final sind!"
                ),
                spacing="Small",
                wrap=True,
            ),
        ],
        spacing="extralarge",
    )

    # Generate outro
    outro = TextBlock(
        text=f"[Infos zur Datenerhebung]({MORE_URL})",
        horizontalAlignment="right",
        spacing="large",
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
    adaptive_card_body = [intro, *stories, note_gsc, outro]
    card = AdaptiveCard(body=adaptive_card_body)

    return card
