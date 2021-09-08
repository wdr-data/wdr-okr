"""Forms for managing Twitter data."""

from django.contrib import admin
from ..models import (
    Twitter,
    TwitterInsight,
    Tweet,
)
from .base import QuintlyAdmin


class InsightAdmin(admin.ModelAdmin):
    """List for choosing existing insight data to edit."""

    list_display = [
        "date",
        "twitter",
        "followers",
    ]
    list_display_links = ["date"]
    list_filter = ["twitter"]
    date_hierarchy = "date"


class TweetAdmin(admin.ModelAdmin):
    """List for choosing existing post data to edit."""

    list_display = [
        "external_id",
        "twitter",
        "created_at",
        "tweet_type",
        "favs",
        "retweets",
        "replies",
    ]
    list_display_links = ["external_id"]
    list_filter = ["twitter", "tweet_type"]
    date_hierarchy = "created_at"


admin.site.register(Twitter, QuintlyAdmin)
admin.site.register(TwitterInsight, InsightAdmin)
admin.site.register(Tweet, TweetAdmin)
