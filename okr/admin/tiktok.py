"""Forms for managing TikTok data."""

from django.contrib import admin
from ..models import (
    TikTok,
    TikTokData,
    TikTokPost,
    TikTokChallenge,
    TikTokHashtag,
    TikTokTag,
)
from .base import QuintlyAdmin


class DataAdmin(admin.ModelAdmin):
    """List for choosing existing TikTok account data to edit."""

    list_display = [
        "tiktok",
        "date",
        "followers",
        "likes",
        "videos",
    ]
    list_display_links = ["date"]
    list_filter = ["tiktok"]
    date_hierarchy = "date"


class PostAdmin(admin.ModelAdmin):
    """List for choosing existing TikTok post data to edit."""

    list_display = [
        "tiktok",
        "external_id",
        "created_at",
        "views",
        "likes",
        "shares",
        "comments",
    ]
    search_fields = ["description", "hashtags__hashtag", "challenges__title"]
    list_display_links = ["external_id"]
    list_filter = ["tiktok"]
    date_hierarchy = "created_at"


class HashtagAdmin(admin.ModelAdmin):
    """List for choosing existing TikTok hashtag data to edit."""

    list_display = [
        "hashtag",
        "first_seen",
    ]
    search_fields = ["hashtag"]
    list_display_links = ["hashtag"]
    date_hierarchy = "first_seen"


class ChallengeAdmin(admin.ModelAdmin):
    """List for choosing existing TikTok challenge data to edit."""

    list_display = [
        "title",
        "description",
        "first_seen",
    ]
    search_fields = ["title"]
    list_display_links = ["title"]
    date_hierarchy = "first_seen"


class TagAdmin(admin.ModelAdmin):
    """List for choosing existing TikTok tag data to edit."""

    list_display = [
        "name",
        "first_seen",
    ]
    search_fields = ["name"]
    list_display_links = ["name"]
    date_hierarchy = "first_seen"


admin.site.register(TikTok, QuintlyAdmin)
admin.site.register(TikTokData, DataAdmin)
admin.site.register(TikTokPost, PostAdmin)
admin.site.register(TikTokHashtag, HashtagAdmin)
admin.site.register(TikTokChallenge, ChallengeAdmin)
admin.site.register(TikTokTag, TagAdmin)
