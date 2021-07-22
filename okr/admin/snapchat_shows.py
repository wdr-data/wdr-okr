"""Forms for managing Snapchat Show data."""

from django.contrib import admin
from ..models import (
    SnapchatShow,
    SnapchatShowInsight,
    SnapchatShowStory,
)
from .base import QuintlyAdmin


class SnapchatShowInsightAdmin(admin.ModelAdmin):
    """List for choosing existing Snapchat show data to edit."""

    list_display = [
        "date",
        "snapchat_show",
        "subscribers",
        "quintly_last_updated",
        "last_updated",
    ]
    list_display_links = ["date"]
    list_filter = ["snapchat_show"]
    date_hierarchy = "date"


class SnapchatShowStoryAdmin(admin.ModelAdmin):
    """List for choosing existing Snapchat show story data to edit."""

    list_display = [
        "snapchat_show",
        "title",
        "start_date_time",
        "total_views",
        "shares",
        "quintly_last_updated",
    ]
    list_display_links = ["title"]
    list_filter = ["snapchat_show", "state"]
    date_hierarchy = "start_date_time"
    search_fields = ["title"]


admin.site.register(SnapchatShow, QuintlyAdmin)
admin.site.register(SnapchatShowInsight, SnapchatShowInsightAdmin)
admin.site.register(SnapchatShowStory, SnapchatShowStoryAdmin)
