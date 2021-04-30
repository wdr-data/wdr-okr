"""Forms for managing Facebook data."""

from django.contrib import admin
from ..models import (
    Facebook,
    FacebookInsight,
    FacebookPost,
)
from .base import QuintlyAdmin


class InsightAdmin(admin.ModelAdmin):
    """List for choosing existing insight data to edit."""

    list_display = [
        "date",
        "facebook",
        "interval",
        "fans",
        "follows",
        "impressions_unique",
        "fans_online_per_day",
    ]
    list_display_links = ["date"]
    list_filter = ["facebook", "interval"]
    date_hierarchy = "date"


class PostAdmin(admin.ModelAdmin):
    """List for choosing existing post data to edit."""

    list_display = [
        "external_id",
        "facebook",
        "created_at",
        "post_type",
        "likes",
        "comments",
        "shares",
        "impressions_unique",
    ]
    list_display_links = ["external_id"]
    list_filter = ["facebook", "post_type"]
    date_hierarchy = "created_at"


admin.site.register(Facebook, QuintlyAdmin)
admin.site.register(FacebookInsight, InsightAdmin)
admin.site.register(FacebookPost, PostAdmin)
