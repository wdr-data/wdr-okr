"""Forms for managing YouTube data."""

from collections import defaultdict
from datetime import date

from django import forms
from django.contrib import admin
from django.contrib import messages
from django.core.files.uploadedfile import UploadedFile
from django.http.request import HttpRequest
import pandas as pd
from loguru import logger

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
from .uploads import UploadFileMixin, UploadFileForm


class UploadFileFormYouTube(UploadFileForm):
    """Upload form for YouTube data."""

    def get_initial_for_field(self, field, field_name):
        if field_name == "youtube":
            youtubes = YouTube.objects.all()[:1]
            youtubes = list(youtubes)
            if youtubes:
                return youtubes[0]

    youtube = forms.ModelChoiceField(YouTube.objects.all(), label="YouTube-Account")


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


class YouTubeVideoAnalyticsAdmin(UploadFileMixin, admin.ModelAdmin):
    """List for choosing existing YouTube video analytics data to edit."""

    upload_form_class = UploadFileFormYouTube

    list_display = [
        "date",
        "youtube_video",
        "views",
        "watch_time",
        "last_updated",
        "impressions",
        "clicks",
    ]
    list_display_links = ["date", "youtube_video"]
    list_filter = ["youtube_video__youtube", "live_or_on_demand"]
    search_fields = ["youtube_video__title", "youtube_video__external_id"]
    date_hierarchy = "date"

    def process_uploaded_file(self, request: HttpRequest, file: UploadedFile):
        """Implementation to handle uploaded files, required by the ``UploadFileMixin``.
        Parses files exported from the YouTube Analytics backend and creates the
        corresponding entries in the database.
        Some checks were added to provide hints to the user if the file has an unexpected
        structure.
        Results are saved in
        :class:`~okr.models.youtube.YouTubeVideoAnalytics`.
        Args:
            request (HttpRequest): The request generated by the upload form
            file (UploadedFile): The uploaded file
        """
        logger.info("Uploaded file: {}", file.name)
        df = pd.read_csv(self.open_zip(file)["Table data.csv"])
        logger.debug(df)

        if not request.POST["youtube"]:
            self.message_user(
                request,
                "Bitte einen YouTube-Account auswählen",
                level=messages.ERROR,
            )
            return

        youtube = YouTube.objects.get(id=request.POST["youtube"])

        field_for_source = {
            "SUBSCRIBER./my_subscriptions": "impressions_subscriptions",
            "SUBSCRIBER.what-to-watch": "impressions_home",
            "SUBSCRIBER.trend": "impressions_trending",
        }

        merged = defaultdict(dict)

        if "Traffic source" not in df.columns:
            self.message_user(
                request,
                "Die hochgeladene Datei enthält keine Traffic sources! "
                'Wähle den Tab "Traffic source" in den YouTube Studio Analytics.',
                level=messages.ERROR,
            )
            return

        if "Impressions" not in df.columns:
            self.message_user(
                request,
                "Die hochgeladene Datei enthält keine Impressions! "
                'Wähle die Metrik "Impressions by Traffic source" in den YouTube Studio Analytics.',
                level=messages.ERROR,
            )
            return

        if "Source title" not in df.columns:
            self.message_user(
                request,
                "Die hochgeladene Datei enthält keine detaillierten Traffic Sources! "
                'Wähle als Traffic Source "Browse features" in den YouTube Studio Analytics.',
                level=messages.ERROR,
            )
            return

        for index, row in df.iterrows():
            time = date.fromisoformat(row["Date"])

            field = field_for_source[row["Traffic source"]]
            merged[time][field] = row["Impressions"]

        logger.debug(merged)

        for time, defaults in merged.items():
            obj, created = YouTubeTrafficSource.objects.update_or_create(
                youtube=youtube,
                date=time,
                defaults=defaults,
            )

        self.message_user(request, "Datei wurde erfolgreich eingelesen!")


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
