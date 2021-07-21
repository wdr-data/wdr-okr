"""Forms for managing Instagram data."""

from django.contrib import admin
from ..models import (
    Insta,
    InstaInsight,
    InstaPost,
    InstaStory,
    InstaIGTV,
)
from .base import QuintlyAdmin


class InsightAdmin(admin.ModelAdmin):
    """List for choosing existing insight data to edit."""

    list_display = [
        "date",
        "insta",
        "interval",
        "reach",
        "impressions",
        "followers_change",
        "posts_change",
    ]
    list_display_links = ["date"]
    list_filter = ["insta", "interval"]
    date_hierarchy = "date"


class PostAdmin(admin.ModelAdmin):
    """List for choosing existing post data to edit."""

    list_display = [
        "external_id",
        "insta",
        "created_at",
        "quintly_import_time",
        "post_type",
        "likes",
        "reach",
        "impressions",
        "saved",
        "video_views",
    ]
    list_display_links = ["external_id"]
    list_filter = ["insta", "post_type"]
    date_hierarchy = "created_at"


class StoryAdmin(admin.ModelAdmin):
    """List for choosing existing story data to edit."""

    list_display = [
        "external_id",
        "insta",
        "created_at",
        "quintly_import_time",
        "story_type",
        "reach",
        "impressions",
        "taps_forward",
        "taps_back",
        "exits",
    ]
    list_display_links = ["external_id"]
    list_filter = ["insta", "story_type"]
    date_hierarchy = "created_at"


class IGTVAdmin(admin.ModelAdmin):
    """List for choosing existing IGTV data to edit."""

    list_display = [
        "external_id",
        "insta",
        "created_at",
        "quintly_import_time",
        "video_title",
        "reach",
        "impressions",
        "video_views",
    ]
    list_display_links = ["external_id"]
    list_filter = ["insta"]
    date_hierarchy = "created_at"


admin.site.register(Insta, QuintlyAdmin)
admin.site.register(InstaInsight, InsightAdmin)
admin.site.register(InstaPost, PostAdmin)
admin.site.register(InstaStory, StoryAdmin)
admin.site.register(InstaIGTV, IGTVAdmin)
