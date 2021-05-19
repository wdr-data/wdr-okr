import pytrends.request

from okr.scrapers.common.types import JSON


class TrendReq(pytrends.request.TrendReq):
    REALTIME_TRENDING_SEARCHES_URL = (
        "https://trends.google.com/trends/api/realtimetrends"
    )

    def realtime_trending_searches(
        self,
        cat: str = "all",
        count: int = 25,
    ) -> JSON:
        """
        Request data from Google Realtime Search Trends section and returns a dataframe
        Source: https://github.com/GeneralMills/pytrends/pull/332
        """
        # Don't know what some of the params mean here, followed the nodejs library
        # https://github.com/pat310/google-trends-api/ 's implemenration

        # sort: api accepts only 0 as the value, optional parameter

        # ri: number of trending stories IDs returned,
        # max value of ri supported is 300, based on emperical evidence

        ri_value = 300
        if count < ri_value:
            ri_value = count

        # rs : don't know what is does but it's max value is never more than the ri_value based on emperical evidence
        # max value of ri supported is 200, based on emperical evidence
        rs_value = 200
        if count < rs_value:
            rs_value = count - 1

        forms = {
            "ns": 15,
            "geo": self.geo,
            "tz": self.tz,
            "hl": self.hl,
            "cat": cat,
            "fi": "0",
            "fs": "0",
            "ri": ri_value,
            "rs": rs_value,
            "sort": 0,
        }
        req_json = self._get_data(
            url=TrendReq.REALTIME_TRENDING_SEARCHES_URL,
            method=TrendReq.GET_METHOD,
            trim_chars=5,
            params=forms,
        )["storySummaries"]["trendingStories"]

        return req_json
