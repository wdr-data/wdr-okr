import os
import datetime

import numpy as np

from analytics import quintly


_quintly = None


def get_quintly():
    # Instantiate the class with your client id and secret
    global _quintly
    if not _quintly:
        _quintly = quintly.QuintlyAPI(
            os.environ.get("QUINTLY_CLIENT_ID"), os.environ.get("QUINTLY_CLIENT_SECRET")
        )
    return _quintly


# You can run the query with the run_query method. It returns a pandas DataFrame
def get_insta_insights(profile_id, *, interval="daily", start_date=None):
    quintly = get_quintly()
    profile_ids = [profile_id]

    if start_date is None:
        if interval == "daily":
            start_date = datetime.date.today() - datetime.timedelta(days=3)
        elif interval == "weekly":
            start_date = datetime.date.today() - datetime.timedelta(days=14)
        elif interval == "monthly":
            start_date = datetime.date.today() - datetime.timedelta(days=60)

    end_date = datetime.date.today()

    table = "instagram"
    fields = ["time", "followers", "followersChange", "postsChange"]

    df_insta = quintly.run_query(
        profile_ids, table, fields, start_date, end_date, interval=interval
    )

    table = "instagramInsights"

    fields = [
        "time",
        "reach",
        "impressions",
    ]
    if interval == "daily":
        fields += [
            "textMessageClicksDay",
            "emailContactsDay",
        ]

    df_insta_insights = quintly.run_query(
        profile_ids, table, fields, start_date, end_date, interval=interval
    )

    df_insta.time = df_insta.time.str[:10]
    df_insta.time = df_insta.time.astype("str")
    df_insta_insights.time = df_insta_insights.time.str[:10]
    df_insta_insights.time = df_insta_insights.time.astype("str")

    df = df_insta.merge(df_insta_insights, on="time", how="inner")

    df = df.replace({np.nan: None})

    print(df)
    return df


def get_insta_stories(profile_id, *, start_date=None):
    quintly = get_quintly()
    profile_ids = [profile_id]
    table = "instagramInsightsStories"
    fields = [
        "externalId",
        "time",
        "caption",
        "reach",
        "impressions",
        "replies",
        "type",
        "link",
        "exits",
    ]
    start_date = start_date or datetime.date.today() - datetime.timedelta(days=7)
    end_date = datetime.date.today()
    df = quintly.run_query(profile_ids, table, fields, start_date, end_date)

    df = df.replace({np.nan: None})

    print(df)
    return df


def get_insta_posts(profile_id, *, start_date=None):
    quintly = get_quintly()
    profile_ids = [profile_id]
    table = "instagramOwnPosts"
    fields = [
        "externalId",
        "time",
        "message",
        "comments",
        "type",
        "link",
    ]
    start_date = start_date or datetime.date.today() - datetime.timedelta(days=7)
    end_date = datetime.date.today()

    df_posts = quintly.run_query(profile_ids, table, fields, start_date, end_date)

    table = "instagramInsightsOwnPosts"

    fields = [
        "externalId",
        "time",
        "likes",
        "reach",
        "impressions",
    ]

    df_posts_insights = quintly.run_query(
        profile_ids, table, fields, start_date, end_date
    )

    df = df_posts.merge(df_posts_insights, on=["externalId", "time"], how="inner")

    df = df.replace({np.nan: None})

    print(df)
    return df


def get_youtube_analytics(profile_id, *, interval="daily", start_date=None):
    quintly = get_quintly()
    profile_ids = [profile_id]
    table = "youtubeAnalytics"

    if start_date is None:
        if interval == "daily":
            start_date = datetime.date.today() - datetime.timedelta(days=7)
        elif interval == "weekly":
            start_date = datetime.date.today() - datetime.timedelta(days=14)
        elif interval == "monthly":
            start_date = datetime.date.today() - datetime.timedelta(days=60)

    end_date = datetime.date.today()

    fields = [
        "time",
        "views",
        "likes",
        "dislikes",
        "estimatedMinutesWatched",
        "averageViewDuration",
    ]

    df = quintly.run_query(profile_ids, table, fields, start_date, end_date)

    df.time = df.time.str[:10]
    df.time = df.time.astype("str")
    df = df.replace({np.nan: None})

    print(df)
    return df
