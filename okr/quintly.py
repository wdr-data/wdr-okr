import os
import datetime

from analytics import quintly


# Instantiate the class with your client id and secret
quintly = quintly.QuintlyAPI(
    os.environ.get("QUINTLY_CLIENT_ID"), os.environ.get("QUINTLY_CLIENT_SECRET")
)

# You can run the query with the run_query method. It returns a pandas DataFrame
def get_insta_insights(profile_id):
    profile_ids = [profile_id]
    table = "instagram"
    fields = ["time", "followers", "followersChange", "postsChange"]
    interval = "daily"
    start_date = datetime.date.today() - datetime.timedelta(days=1)
    end_date = start_date
    df = quintly.run_query(
        profile_ids, table, fields, start_date, end_date, interval=interval
    )
    print(df)
    return df
