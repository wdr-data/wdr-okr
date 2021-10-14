from os import environ
from typing import Dict, Optional
import datetime as dt
from io import BytesIO

import requests
import pandas as pd

from ..common.utils import local_today, local_yesterday


API_KEY = environ["ATI_API_KEY_SWR"]


def _get_data(**params: Optional[Dict[str, str]]):
    url = "https://apirest.atinternet-solutions.com/data/v2/csv/getData"

    params = {
        "apikey": API_KEY,
        **params,
    }

    return requests.get(url, params=params)


def _all_pages_as_df(**params: Optional[Dict[str, str]]) -> pd.DataFrame:
    params = params.copy()
    params["max-results"] = "10000"

    dfs = []
    page = 1

    while True:
        params["page-num"] = page

        response = _get_data(**params)
        response.raise_for_status()

        df = pd.read_csv(BytesIO(response.content), encoding="utf-8", sep=";")

        if df.empty:
            break

        dfs.append(df)

        page += 1

    return pd.concat(dfs)


def get_all_episode_data(date: Optional[dt.date] = None) -> pd.DataFrame:
    """
    Loads data for all podcast episodes for a single day from AT Internet API.

    Args:
        date (Optional[dt.date], optional): Date for which to load data.
          If None, yesterday's data is loaded.

    Returns:
        pd.DataFrame: Data for all podcast episodes for a single day.
    """

    today = local_today()
    if date is None:
        date = local_yesterday()

    return _all_pages_as_df(
        columns="{d_time_date,d_rm_type,d_rm_broadcast,d_rm_l2,d_rm_theme1,d_rm_theme2,d_rm_theme3,d_rm_content,d_rm_duration,m_rm_playcounts,m_rm_time_spent}",
        sort="{-m_rm_playcounts}",
        filter="{d_rm_type:{$eq:'Audiodateien'},d_rm_theme1:{$eq:'WDR'}}",
        space="{s:511893}",
        period="{R:{D:'%d'}}" % (date - today).days,
    )
