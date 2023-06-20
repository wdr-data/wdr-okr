"""Forms for managing YouTube data."""

from datetime import date, timedelta
import re
import zipfile

from bulk_sync import bulk_sync
from django.db.models import Q
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
    YouTubeVideoAnalyticsExtra,
    YouTubeVideoDemographics,
    YouTubeVideoTrafficSource,
    YouTubeVideoSearchTerm,
    YouTubeVideoExternalTraffic,
)
from .base import QuintlyAdmin
from .uploads import UploadFileMixin, UploadMultipleFilesForm


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
        "date",
        "youtube_video",
        "views",
        "watch_time",
        "last_updated",
    ]
    list_display_links = ["date", "youtube_video"]
    list_filter = ["youtube_video__youtube", "live_or_on_demand"]
    search_fields = ["youtube_video__title", "youtube_video__external_id"]
    date_hierarchy = "date"


class YouTubeVideoAnalyticsExtraAdmin(UploadFileMixin, admin.ModelAdmin):
    """List for uploading and choosing existing additional YouTube video
    analytics data to edit."""

    upload_form_class = UploadMultipleFilesForm

    list_display = [
        "date",
        "youtube_video",
        "impressions",
        "clicks",
    ]
    list_display_links = ["date", "youtube_video"]
    list_filter = ["youtube_video__youtube"]
    search_fields = ["youtube_video__title", "youtube_video__external_id"]
    date_hierarchy = "date"

    names = {
        "de": {
            "zip_name": "Videos",
            "csv_name_table_data": "Tabellendaten.csv",
            "column_content": "Videos",
            "column_title": "Videotitel",
            "column_published_at": "Veröffentlichungszeitpunkt des Videos",
            "column_views": "Aufrufe",
            "column_watchtime": "Wiedergabezeit (Stunden)",
            "column_subscribers": "Abonnenten",
            "column_estimated_revenue": "Geschätzter Umsatz (USD)",
            "column_impressions": "Impressionen",
            "column_ctr": "Klickrate der Impressionen (%)",
            "content_total": "Gesamt",
        },
        "en": {
            "zip_name": "Content",
            "csv_name_table_data": "Table data.csv",
            "column_content": "Content",
            "column_title": "Video title",
            "column_published_at": "Video publish time",
            "column_views": "Views",
            "column_watchtime": "Watch time (hours)",
            "column_subscribers": "Subscribers",
            "column_estimated_revenue": "Estimated revenue (USD)",
            "column_impressions": "Impressions",
            "column_ctr": "Impressions click-through rate (%)",
            "content_total": "Total",
        },
    }

    @staticmethod
    def clean_soft_hyphen_and_strip(name: str):
        return name.replace("\xad", "").strip()

    def process_uploaded_file(self, request: HttpRequest, file: UploadedFile):
        """Implementation to handle uploaded files, required by the ``UploadFileMixin``.
        Parses files exported from the YouTube Analytics backend and creates the
        corresponding entries in the database.
        Some checks were added to provide hints to the user if the file has an unexpected
        structure.
        Results are saved in
        :class:`~okr.models.youtube.YouTubeVideoAnalyticsExtra`.
        Args:
            request (HttpRequest): The request generated by the upload form
            file (UploadedFile): The uploaded file
        """
        logger.info("Uploaded file: {}", file.name)

        try:
            zip_file = self.open_zip(file)
        except zipfile.BadZipFile:
            self.message_user(
                request,
                f'Datei "{file.name}" ist keine ZIP-Datei. Bitte lade die Datei so hoch, wie sie aus YouTube Studio raus kommt.',
                level=messages.ERROR,
            )
            return

        table_data_csv = None
        for name, csv_file in zip_file.items():
            for lang, names in self.names.items():
                if names["csv_name_table_data"] == name:
                    table_data_csv = csv_file
                    break
            if table_data_csv:
                break

        else:
            self.message_user(
                request,
                f'Datei "{file.name}" ist vermutlich nicht der richtige Export (CSV-Datei mit Tabellendaten nicht gefunden). Wähle zum Export den Tab "Videos" bzw. "Content" in den YouTube Studio Analytics. Lasse den Dateinamen unverändert.',
                level=messages.ERROR,
            )
            return

        logger.debug(lang)

        filename = file.name
        name_pattern = r"(.*?) (\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2}).*"
        parsed_name = re.match(name_pattern, filename)

        if not parsed_name:
            self.message_user(
                request,
                f'Datei "{filename}" ist vermutlich nicht der richtige Export (Dateiname unbekannt). Wähle zum Export den Tab "Videos" bzw. "Content" in den YouTube Studio Analytics. Lasse den Dateinamen unverändert.',
                level=messages.ERROR,
            )
            return

        file_name_prefix, start_date, end_date = parsed_name.groups()

        # Replace weird characters in file name
        file_name_prefix = file_name_prefix.replace("_", "").replace("\xad", "")

        if file_name_prefix != names["zip_name"]:
            self.message_user(
                request,
                f'Datei "{filename}" ist nicht der richtige Export (Dateiname beginnt nicht mit "Videos" oder "Content"). Wähle zum Export den Tab "Video" bzw. "Content" in den YouTube Studio Analytics. Lasse den Dateinamen unverändert.',
                level=messages.ERROR,
            )
            return

        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)

        if end_date - start_date > timedelta(days=1, hours=2):
            self.message_user(
                request,
                f'Datei "{filename}" scheint mehr als einen Tag zu umfassen',
                level=messages.ERROR,
            )
            return

        # Load and clean CSV
        dtype = {
            names["column_content"]: str,
            names["column_title"]: str,
            names["column_published_at"]: str,
            names["column_views"]: int,
            names["column_watchtime"]: float,
            names["column_subscribers"]: int,
            names["column_impressions"]: int,
            names["column_ctr"]: float,
        }

        df = pd.read_csv(
            table_data_csv,
            dtype=str,
        )
        df.rename(columns=self.clean_soft_hyphen_and_strip, inplace=True)

        df.fillna(
            {
                names["column_content"]: "",
                names["column_title"]: "",
                names["column_published_at"]: "",
                names["column_views"]: 0,
                names["column_watchtime"]: 0,
                names["column_subscribers"]: 0,
                names["column_impressions"]: 0,
                names["column_ctr"]: 0,
            },
            inplace=True,
        )

        df = df.astype(dtype)

        df[names["column_content"]] = df[names["column_content"]].apply(
            self.clean_soft_hyphen_and_strip
        )

        df.info()

        if names["column_content"] not in df.columns:
            self.message_user(
                request,
                f'Datei "{filename}" enthält keine Video-Zahlen! '
                'Wähle den Tab "Videos" bzw. "Content" in den YouTube Studio Analytics.',
                level=messages.ERROR,
            )
            return

        if names["column_impressions"] not in df.columns:
            self.message_user(
                request,
                f'Datei "{filename}" enthält keine Impressions! '
                'Wähle den Tab "Videos" bzw. "Content" in den YouTube Studio Analytics.',
                level=messages.ERROR,
            )
            return

        if names["column_ctr"] not in df.columns:
            self.message_user(
                request,
                f'Datei "{filename}" enthält keine Click-Through-Rate! '
                'Wähle den Tab "Videos" bzw. "Content" in den YouTube Studio Analytics.',
                level=messages.ERROR,
            )
            return

        df = df[df[names["column_content"]] != names["content_total"]]

        df["Clicks"] = (
            df[names["column_ctr"]] * df[names["column_impressions"]] / 100
        ).astype("int")

        youtube_videos = YouTubeVideo.objects.filter(
            external_id__in=df[names["column_content"]].unique().tolist()
        )

        new_models = []
        youtube_videos = {video.external_id: video for video in youtube_videos}

        for index, row in df.iterrows():
            if row[names["column_content"]] not in youtube_videos:
                logger.warning(
                    "Could not find YouTube video with external_id {}",
                    row[names["column_content"]],
                )
                continue

            new_models.append(
                YouTubeVideoAnalyticsExtra(
                    youtube_video=youtube_videos[row[names["column_content"]]],
                    date=start_date,
                    impressions=row[names["column_impressions"]],
                    clicks=row["Clicks"],
                )
            )

        result = bulk_sync(
            new_models=new_models,
            filters=Q(date=start_date),
            key_fields=["youtube_video_id", "date"],
            skip_deletes=True,
        )

        logger.info(result)

        self.message_user(request, f'Datei "{filename}" erfolgreich eingelesen!')


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
admin.site.register(YouTubeVideoAnalyticsExtra, YouTubeVideoAnalyticsExtraAdmin)
admin.site.register(YouTubeVideoDemographics, YouTubeVideoDemographicsAdmin)
admin.site.register(YouTubeVideoTrafficSource, YouTubeVideoTrafficSourceAdmin)
admin.site.register(YouTubeVideoSearchTerm, YouTubeVideoSearchTermAdmin)
admin.site.register(YouTubeVideoExternalTraffic, YouTubeVideoExternalTrafficAdmin)
