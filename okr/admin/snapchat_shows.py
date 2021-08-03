"""Forms for managing Snapchat Show data."""

from django.contrib import admin
from ..models import (
    SnapchatShow,
    SnapchatShowInsight,
    SnapchatShowStory,
    SnapchatShowSnap,
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
    list_filter = ["snapchat_show"]
    date_hierarchy = "start_date_time"
    search_fields = ["title"]


class SnapchatShowSnapAdmin(admin.ModelAdmin):
    """List for choosing existing Snapchat show story snap data to edit."""

    list_display = [
        "get_story_start_date_time",  # Custom lookup function
        "get_story_title",  # Custom lookup function
        "position",
        "name",
        "total_views",
        "drop_off_rate",
        "quintly_last_updated",
    ]
    list_display_links = ["name", "position"]
    date_hierarchy = "story__start_date_time"
    ordering = ("-story__start_date_time", "position")

    # Custom lookup function for story.title
    def get_story_title(self, obj):
        return obj.story.title

    get_story_title.admin_order_field = "story__title"
    get_story_title.short_description = "Story Titel"

    # Custom lookup function for story.start_date_time
    def get_story_start_date_time(self, obj):
        return obj.story.start_date_time

    get_story_start_date_time.admin_order_field = "story__start_date_time"
    get_story_start_date_time.short_description = "Veröffentlichungszeitpunkt der Story"


admin.site.register(SnapchatShow, QuintlyAdmin)
admin.site.register(SnapchatShowInsight, SnapchatShowInsightAdmin)
admin.site.register(SnapchatShowStory, SnapchatShowStoryAdmin)
admin.site.register(SnapchatShowSnap, SnapchatShowSnapAdmin)
