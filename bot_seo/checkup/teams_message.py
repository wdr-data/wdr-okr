""" Helper functions to generate a message for MS Teams. """

import os
from typing import List

from pyadaptivecards.card import AdaptiveCard
from pyadaptivecards.container import ColumnSet
from pyadaptivecards.components import Image, TextBlock
from pyadaptivecards.actions import OpenUrl

from okr.scrapers.common.types import JSON
from ..pyadaptivecards_tools import Container, Column
from ..teams_tools import format_number

GREETINGS = ["Hallo!", "Guten Tag!", "Hi!"]
MORE_URL = os.environ.get("SEO_BOT_TODO_MORE_URL")


def _generate_adaptive_card(
    google_trends_data: List[JSON] = None,
    twitter_trends_data: List[JSON] = None,
) -> AdaptiveCard:
    title = TextBlock("SEO-Checkup", size="large", weight="bolder")
    card_body = [title]

    if google_trends_data:
        title_trends = TextBlock(
            "Google Echtzeit-Trends", size="medium", weight="bolder"
        )
        card_body.append(title_trends)

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

        card_body.append(Container(trends_items))

    if twitter_trends_data:
        title_trends = Container(
            [TextBlock("Twitter-Trends Deutschland", size="medium", weight="bolder")],
            separator=True,
        )
        card_body.append(title_trends)

        twitter_trends_items = []
        i = 0
        while i < 10:
            # for item in twitter_trends_data:
            item = twitter_trends_data[i]
            i += 1
            trend_item = f"{i}. [{item['name']}]({item['url']})"
            if item["tweet_volume"]:  # can be None
                trend_item += f" ({format_number(item['tweet_volume'])} Tweets)"
            twitter_trends_items.append(TextBlock(trend_item))

        card_body.append(Container(twitter_trends_items))

    card = AdaptiveCard(body=card_body)

    return card
