"""Forms for managing YouTube data."""

from django.contrib import admin

from ..models import (
    YouTube,
    YouTubeAnalytics,
    YouTubeDemographics,
    YouTubeTrafficSource,
    YouTubeVideo,
    YouTubeVideoAnalytics,
    YouTubeVideoDemographics,
    YouTubeVideoTrafficSource,
    YouTubeVideoSearchTerm,
    YouTubeVideoExternalTraffic,
)
from .base import QuintlyAdmin


class YouTubeAnalyticsAdmin(admin.ModelAdmin):
    """List for choosing existing YouTube analytics data to edit."""

    list_display = [
        "date",
        "youtube",
        "subscribers",
        "quintly_last_updated",
        "last_updated",
    ]
    list_display_links = ["date"]
    list_filter = ["youtube"]
    date_hierarchy = "date"


class YouTubeDemographicsAdmin(admin.ModelAdmin):
    """List for choosing existing YouTube demographics data to edit."""

    list_display = [
        "date",
        "youtube",
        "age_range",
        "gender",
        "quintly_last_updated",
        "last_updated",
    ]
    list_display_links = ["date"]
    list_filter = ["youtube", "age_range", "gender"]
    date_hierarchy = "date"


class YouTubeTrafficSourceAdmin(admin.ModelAdmin):
    """List for choosing existing YouTube traffic source data to edit."""

    list_display = [
        "date",
        "youtube",
        "source_type",
        "views",
        "watch_time",
        "quintly_last_updated",
        "last_updated",
    ]
    list_display_links = ["date"]
    list_filter = ["youtube", "source_type"]
    date_hierarchy = "date"


class YouTubeVideoAdmin(admin.ModelAdmin):
    """List for choosing existing YouTube video base data to edit."""

    list_display = [
        "published_at",
        "title",
        "duration",
        "is_livestream",
        "external_id",
        "quintly_last_updated",
        "last_updated",
    ]
    list_display_links = ["published_at", "title"]
    list_filter = ["youtube", "is_livestream"]
    search_fields = ["title", "external_id"]
    date_hierarchy = "published_at"


class YouTubeVideoAnalyticsAdmin(admin.ModelAdmin):
    """List for choosing existing YouTube video analytics data to edit."""

    list_display = [
        "youtube_video",
        "views",
        "watch_time",
        "last_updated",
    ]
    list_display_links = ["youtube_video"]
    list_filter = ["youtube_video__youtube"]
    search_fields = ["youtube_video__title", "youtube_video__external_id"]
    date_hierarchy = "date"


class YouTubeVideoDemographicsAdmin(admin.ModelAdmin):
    """List for choosing existing YouTube video demographics data to edit."""

    list_display = [
        "youtube_video",
        "age_range",
        "gender",
        "views_percentage",
        "last_updated",
    ]
    list_display_links = ["youtube_video"]
    list_filter = ["youtube_video__youtube", "age_range", "gender"]
    search_fields = ["youtube_video__title", "youtube_video__external_id"]
    date_hierarchy = "date"


class YouTubeVideoTrafficSourceAdmin(admin.ModelAdmin):
    """List for choosing existing YouTube video traffic source data to edit."""

    list_display = [
        "youtube_video",
        "source_type",
        "views",
        "watch_time",
        "last_updated",
    ]
    list_display_links = ["youtube_video", "source_type"]
    search_fields = ["youtube_video__title", "youtube_video__external_id"]
    list_filter = ["source_type", "youtube_video__youtube"]


class YouTubeVideoSearchTermAdmin(admin.ModelAdmin):
    """List for choosing existing YouTube video search term data to edit."""

    list_display = [
        "youtube_video",
        "search_term",
        "views",
        "watch_time",
        "last_updated",
    ]
    list_display_links = ["youtube_video"]
    search_fields = ["youtube_video__title", "youtube_video__external_id"]
    list_filter = ["youtube_video__youtube"]


class YouTubeVideoExternalTrafficAdmin(admin.ModelAdmin):
    """List for choosing existing YouTube video search term data to edit."""

    list_display = [
        "youtube_video",
        "name",
        "views",
        "watch_time",
        "last_updated",
    ]
    list_display_links = ["youtube_video"]
    search_fields = ["youtube_video__title", "youtube_video__external_id"]
    list_filter = ["youtube_video__youtube"]


admin.site.register(YouTube, QuintlyAdmin)
admin.site.register(YouTubeAnalytics, YouTubeAnalyticsAdmin)
admin.site.register(YouTubeDemographics, YouTubeDemographicsAdmin)
admin.site.register(YouTubeTrafficSource, YouTubeTrafficSourceAdmin)
admin.site.register(YouTubeVideo, YouTubeVideoAdmin)
admin.site.register(YouTubeVideoAnalytics, YouTubeVideoAnalyticsAdmin)
admin.site.register(YouTubeVideoDemographics, YouTubeVideoDemographicsAdmin)
admin.site.register(YouTubeVideoTrafficSource, YouTubeVideoTrafficSourceAdmin)
admin.site.register(YouTubeVideoSearchTerm, YouTubeVideoSearchTermAdmin)
admin.site.register(YouTubeVideoExternalTraffic, YouTubeVideoExternalTrafficAdmin)
