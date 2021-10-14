from typing import Dict, Optional

import requests


def _request(path: str, params: Optional[Dict[str, str]] = None):
    url = f"https://api.ardaudiothek.de/{path}"
    return requests.get(url, params=params)


def get_programset(programset_id: str) -> Dict:
    """
    Returns programset information with the given ID from the API.

    Args:
        programset_id (str): The id of the programset.

    Returns:
        Dict: The programset information.
    """
    response = _request(f"programsets/{programset_id}", params={"limit": 1000})
    response.raise_for_status()
    return response.json()


def get_item(item_id: str) -> Dict:
    """
    Returns item information with the given ID from the API.

    Args:
        item_id (str): The id of the programset.

    Returns:
        Dict: The item information.
    """
    response = _request(f"items/{item_id}")
    response.raise_for_status()
    return response.json()
