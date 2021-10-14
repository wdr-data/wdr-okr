from typing import Dict, Optional

import requests


def _request(path: str, params: Optional[Dict[str, str]] = None):
    url = f"https://api.ardaudiothek.de/{path}"
    return requests.get(url, params=params)


def get_programset(programset_id: str) -> Dict:
    response = _request(f"programsets/{programset_id}", params={"limit": 1000})
    return response.json()


def get_item(item_id: str) -> Dict:
    response = _request(f"items/{item_id}")
    return response.json()
