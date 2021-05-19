""" Helper functions to generate a message for MS Teams. """

import os
from typing import List

from pyadaptivecards.card import AdaptiveCard
from pyadaptivecards.container import ColumnSet
from pyadaptivecards.components import Image, TextBlock
from pyadaptivecards.actions import OpenUrl

from okr.scrapers.common.types import JSON
from ..pyadaptivecards_tools import Container, Column

GREETINGS = ["Hallo!", "Guten Tag!", "Hi!"]
MORE_URL = os.environ.get("SEO_BOT_TODO_MORE_URL")


def _generate_adaptive_card(google_trends_data: List[JSON]) -> AdaptiveCard:
    title = TextBlock("SEO-Checkup", size="large", weight="bolder")

    title_trends = TextBlock("Google Echtzeit-Trends", size="medium", weight="bolder")

    trends_items = []
    for trend_data in google_trends_data:
        topic = TextBlock(" • ".join(trend_data["entityNames"]), weight="bolder")

        top_article = trend_data["articles"][0]
        article_url = f"[{top_article['source']}]({top_article['url']})"
        time = top_article["time"]
        share_url = f"[Mehr]({trend_data['shareUrl']})"
        subtext = TextBlock(f"{article_url} {time} {share_url}")

        image = Image(
            f"https:{trend_data['image']['imgUrl']}",
            selectAction=OpenUrl(
                url=trend_data["image"]["newsUrl"],
                title=trend_data["image"]["source"],
            ),
        )

        trends_items.append(
            ColumnSet(
                columns=[
                    Column(
                        items=[topic, subtext],
                        width=80,
                        verticalContentAlignment="center",
                    ),
                    Column(items=[image], width=20),
                ]
            )
        )

    card = AdaptiveCard(body=[title, title_trends, Container(trends_items)])

    return card
