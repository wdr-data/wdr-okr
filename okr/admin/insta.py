"""Forms for managing Instagram data."""

from django.contrib import admin
from ..models import (
    Insta,
    InstaInsight,
    InstaPost,
    InstaVideoData,
    InstaReelData,
    InstaStory,
    InstaIGTV,
    InstaIGTVData,
    InstaComment,
    InstaDemographics,
    InstaHourlyFollowers,
)
from .base import QuintlyAdmin


class InsightAdmin(admin.ModelAdmin):
    """List for choosing existing insight data to edit."""

    list_display = [
        "date",
        "insta",
        "reach",
        "reach_7_days",
        "reach_28_days",
        "impressions",
    ]
    list_display_links = ["date"]
    list_filter = ["insta"]
    date_hierarchy = "date"


class PostAdmin(admin.ModelAdmin):
    """List for choosing existing post data to edit."""

    list_display = [
        "external_id",
        "insta",
        "created_at",
        "quintly_last_updated",
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


class InstaVideoDataAdmin(admin.ModelAdmin):
    """List for choosing existing video data to edit."""

    list_display = [
        "date",
        "post",
        "video_views",
        "impressions",
        "quintly_last_updated",
    ]
    list_display_links = ["date", "post"]
    list_filter = ["post__insta"]
    date_hierarchy = "date"
    search_fields = ["post__external_id"]


class InstaReelDataAdmin(admin.ModelAdmin):
    """List for choosing existing reel data to edit."""

    list_display = [
        "date",
        "post",
        "video_views",
        "shares",
        "quintly_last_updated",
    ]
    list_display_links = ["date", "post"]
    list_filter = ["post__insta"]
    date_hierarchy = "date"
    search_fields = ["post__external_id"]


class StoryAdmin(admin.ModelAdmin):
    """List for choosing existing story data to edit."""

    list_display = [
        "external_id",
        "insta",
        "created_at",
        "quintly_last_updated",
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
        "quintly_last_updated",
        "video_title",
        "reach",
        "impressions",
        "video_views",
    ]
    list_display_links = ["external_id"]
    list_filter = ["insta"]
    date_hierarchy = "created_at"


class IGTVDataAdmin(admin.ModelAdmin):
    """List for choosing existing IGTV data to edit."""

    list_display = [
        "date",
        "igtv",
        "likes",
        "comments",
        "reach",
        "impressions",
        "saved",
        "video_views",
    ]
    list_display_links = ["date", "igtv"]
    list_filter = ["igtv__insta"]
    date_hierarchy = "date"
    search_fields = ["igtv__external_id", "igtv__video_title"]


class CommentAdmin(admin.ModelAdmin):
    """List for choosing existing Instagram comment data to edit."""

    list_display = [
        "post",
        "created_at",
        "username",
    ]
    list_display_links = ["created_at", "username"]
    list_filter = ["is_account_answer", "is_reply", "is_hidden", "post__insta"]
    date_hierarchy = "created_at"
    search_fields = ["post", "username", "external_post_id", "external_id"]


class DemographicsAdmin(admin.ModelAdmin):
    """List for choosing existing Instagram demographics data to edit."""

    list_display = [
        "insta",
        "date",
        "quintly_last_updated",
        "age_range",
        "gender",
        "followers",
    ]
    list_display_links = ["insta", "date"]
    list_filter = ["age_range", "gender", "insta"]
    date_hierarchy = "date"
    search_fields = ["insta"]


class HourlyFollowersAdmin(admin.ModelAdmin):
    """List for choosing existing Instagram hourly followers data to edit."""

    list_display = [
        "insta",
        "date_time",
        "followers",
    ]
    list_display_links = ["insta", "date_time"]
    list_filter = ["insta"]
    date_hierarchy = "date_time"
    search_fields = ["insta"]


admin.site.register(Insta, QuintlyAdmin)
admin.site.register(InstaInsight, InsightAdmin)
admin.site.register(InstaPost, PostAdmin)
admin.site.register(InstaVideoData, InstaVideoDataAdmin)
admin.site.register(InstaReelData, InstaReelDataAdmin)
admin.site.register(InstaStory, StoryAdmin)
admin.site.register(InstaIGTV, IGTVAdmin)
admin.site.register(InstaIGTVData, IGTVDataAdmin)
admin.site.register(InstaComment, CommentAdmin)
admin.site.register(InstaDemographics, DemographicsAdmin)
admin.site.register(InstaHourlyFollowers, HourlyFollowersAdmin)
