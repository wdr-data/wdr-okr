""" Helper functions to generate a message for MS Teams. """

import os
import random

from typing import List
from pyadaptivecards.card import AdaptiveCard
from pyadaptivecards.container import ColumnSet, FactSet
from pyadaptivecards.components import Fact, TextBlock

from okr.models.pages import Page
from ..pyadaptivecards_tools import ActionSet, Container, Column, ToggleVisibility
from ..teams_tools import format_number, format_percent


GREETINGS = ["Hallo!", "Guten Tag!", "Hi!"]
MORE_URL = os.environ.get("SEO_BOT_TODO_MORE_URL")
ARTICLE_THRESHOLD = int(os.environ.get("SEO_BOT_TOP_ARTICLES_THRESHOLD", 10000))


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

    # Add webtrekk data, if webtrekk data is available
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


def _generate_article_section(page: Page, i: int) -> Container:

    details = _generate_details(page)

    # some pages (such as https://www1.wdr.de/nachrichten/index.html)
    # don't have latest_meta
    if page.latest_meta:
        article = f"[{page.latest_meta.headline}]({page.url})"
    elif page.webtrekk_data:
        article = f"[{page.webtrekk_data.webtrekk_meta.headline}]({page.url})"
    else:
        article = f"[{page.url}]({page.url})"

    place = TextBlock(
        f"{i + 1}.",
        weight="bolder",
        size="large",
        horizontalAlignment="right",
        spacing="None",
    )
    headline = TextBlock(
        f"{article} (**{format_number(page.clicks_all)}** Klicks)",
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
                [place],
                verticalContentAlignment="center",
                width=10,
                spacing="none",
            ),
            Column(
                [headline],
                verticalContentAlignment="center",
                width=67,
                spacing="small",
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

    article_section_container = Container(
        items=[summary, details], id=f"story_{page.id}", spacing="Large"
    )

    return article_section_container


def _generate_adaptive_card(
    top_articles: List[Page],
    articles_above_threshold: int,
    threshold: int = 10000,
) -> AdaptiveCard:

    # Generate intro
    greeting = random.choice(GREETINGS)
    intro = TextBlock(
        f"{greeting} Das sind die drei Beiträge, mit denen wir gestern die meisten Besucher:innen von Google in unser Angebot locken konnten. **Können wir daraus was lernen?**",
        wrap=True,
    )

    # Generate sections for each page
    article_sections = []

    for i, page in enumerate(top_articles):
        article_section = _generate_article_section(page, i)

        # Add separators between stories
        if i > 0:
            article_section.separator = True

        article_sections.append(article_section)

    # Generate above_threshold message (only if the threshold was passed)
    threshold = format_number(ARTICLE_THRESHOLD)
    above_threshold = TextBlock(
        text=f"Gestern hatten wir {articles_above_threshold} Beiträge mit mehr als {threshold} Klicks!",
        spacing="extralarge",
        size="medium",
        weight="bolder",
        wrap=True,
    )

    if articles_above_threshold > 3:
        above_threshold.text += " 🎉"
        above_threshold.size = "large"
    elif articles_above_threshold == 1:
        above_threshold.text = (
            f"Gestern hatten wir einen Beitrag mit mehr als {threshold} Klicks."
        )
        above_threshold.size = None
        above_threshold.weight = None
    elif articles_above_threshold < 1:
        above_threshold = None

    if above_threshold:
        article_sections.append(above_threshold)

    # Add note about GSC data
    note_gsc = TextBlock(
        text=(
            "Letzter Datenabgleich mit der GSC: 15:30 Uhr\n"
            "Es dauert bis zu 48 Stunden, bis die Daten in der GSC final sind!"
        ),
        horizontalAlignment="left",
        spacing="extralarge",
        wrap=True,
    )

    # Generate outro
    outro = TextBlock(
        text=f"[Infos zur Datenerhebung]({MORE_URL})",
        horizontalAlignment="right",
        spacing="large",
    )

    # Put everything together
    adaptive_card_body = [intro, *article_sections, note_gsc, outro]
    card = AdaptiveCard(body=adaptive_card_body)

    return card
