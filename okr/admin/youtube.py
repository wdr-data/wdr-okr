"""Forms for managing YouTube data."""

from django.contrib import admin

from ..models import (
    YouTube,
    YouTubeAnalytics,
    YouTubeDemographics,
    YouTubeVideo,
    YouTubeVideoAnalytics,
    YouTubeVideoDemographics,
    YouTubeVideoTrafficSource,
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


class YouTubeVideoAdmin(admin.ModelAdmin):
    """List for choosing existing YouTube video base data to edit."""

    list_display = [
        "published_at",
        "title",
        "duration",
        "is_livestream",
        "quintly_last_updated",
        "last_updated",
    ]
    list_display_links = ["published_at"]
    list_filter = ["youtube", "is_livestream"]
    date_hierarchy = "published_at"


class YouTubeVideoAnalyticsAdmin(admin.ModelAdmin):
    """List for choosing existing YouTube video analytics data to edit."""

    list_display = [
        "date",
        "youtube_video_id",
        "views",
        "quintly_last_updated",
        "last_updated",
    ]
    list_display_links = ["date"]
    date_hierarchy = "date"


class YouTubeVideoDemographicsAdmin(admin.ModelAdmin):
    """List for choosing existing YouTube video demographics data to edit."""

    list_display = [
        "date",
        "youtube_video_id",
        "age_range",
        "gender",
        "last_updated",
    ]
    list_display_links = ["date"]
    list_filter = ["age_range", "gender"]
    date_hierarchy = "date"


class YouTubeVideoTrafficSourceAdmin(admin.ModelAdmin):
    """List for choosing existing YouTube video traffic source data to edit."""

    list_display = [
        "youtube_video_id",
        "source_type",
        "last_updated",
    ]
    list_display_links = ["youtube_video_id", "source_type"]
    list_filter = ["source_type"]


admin.site.register(YouTube, QuintlyAdmin)
admin.site.register(YouTubeAnalytics, YouTubeAnalyticsAdmin)
admin.site.register(YouTubeDemographics, YouTubeDemographicsAdmin)
admin.site.register(YouTubeVideo, YouTubeVideoAdmin)
admin.site.register(YouTubeVideoAnalytics, YouTubeVideoAnalyticsAdmin)
admin.site.register(YouTubeVideoDemographics, YouTubeVideoDemographicsAdmin)
admin.site.register(YouTubeVideoTrafficSource, YouTubeVideoTrafficSourceAdmin)
