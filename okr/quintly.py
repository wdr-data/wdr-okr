import os
import datetime

from analytics import quintly


# Instantiate the class with your client id and secret
quintly = quintly.QuintlyAPI(
    os.environ.get("QUINTLY_CLIENT_ID"), os.environ.get("QUINTLY_CLIENT_SECRET")
)

# You can run the query with the run_query method. It returns a pandas DataFrame
def get_insta_insights(profile_id, *, interval="daily"):
    profile_ids = [profile_id]
    start_date = datetime.date.today() - datetime.timedelta(days=1)
    end_date = start_date

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

    print(df)
    return df


# get_insta_insights(278343)


def get_insta_stories(profile_id):
    profile_ids = [profile_id]
    table = "instagramInsightsStories"
    fields = [
        "time",
        "reach",
        "impressions",
        "caption",
        "replies",
        "type",
        "link",
        "externalId",
    ]
    start_date = datetime.date.today() - datetime.timedelta(days=1)
    end_date = start_date
    df = quintly.run_query(profile_ids, table, fields, start_date, end_date)
    print(df)
    return df


# get_insta_stories(278343)
