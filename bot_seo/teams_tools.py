from loguru import logger
from pyadaptivecards.card import AdaptiveCard
import requests

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