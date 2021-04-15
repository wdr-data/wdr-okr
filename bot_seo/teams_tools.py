from typing import Optional, Union

from loguru import logger
from pyadaptivecards.card import AdaptiveCard
import requests
from django.utils.numberformat import format


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


def send_to_teams(payload: dict, webhook_url: str) -> requests.models.Response:
    """Send payload to MS Teams with webhook_url.

    Args:
        payload (dict): Payload to send.
        webhook_url (str): Webhook to use.

    Returns:
        requests.models.Response: Response from request.post()
    """
    result = requests.post(webhook_url, json=payload)
    result.raise_for_status()
    logger.info("Message sent to MS Teams")
    return result


def generate_teams_payload(adaptive_card: AdaptiveCard) -> dict:
    """Generate payload for MS Teams.

    Args:
        adaptive_card (AdaptiveCard): AdaptiveCard to generate payload with.

    Returns:
        dict: Payload dict for MS Teams.
    """

    # Add adaptive card to payload
    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": "null",
                "content": adaptive_card.to_dict(),
            }
        ],
    }

    return payload
