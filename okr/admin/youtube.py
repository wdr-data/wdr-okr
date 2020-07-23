from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
import re

from django import forms
from django.contrib import admin
from django.contrib import messages
import pandas as pd

from ..models import (
    YouTube,
    YouTubeAnalytics,
    YouTubeTrafficSource,
    YouTubeViewerAge,
    YouTubeAgeRangeDuration,
    YouTubeAgeRangePercentage,
)
from .base import QuintlyAdmin
from .uploads import UploadFileMixin, UploadFileForm


class UploadFileFormYouTube(UploadFileForm):
    def get_initial_for_field(self, field, field_name):
        if field_name == "youtube":
            youtubes = YouTube.objects.all()[:1]
            youtubes = list(youtubes)
            if youtubes:
                return youtubes[0]

    youtube = forms.ModelChoiceField(YouTube.objects.all(), label="YouTube-Account")


class TrafficSourceAdmin(UploadFileMixin, admin.ModelAdmin):
    upload_form_class = UploadFileFormYouTube

    list_display = ["date", "youtube"]
    list_display_links = ["date"]
    date_hierarchy = "date"

    readonly_fields = ["last_updated"]

    def process_uploaded_file(self, request, file):
        print(file.name)
        df = pd.read_csv(self.open_zip(file)["Chart data.csv"])
        print(df)

        if not request.POST["youtube"]:
            self.message_user(
                request, "Bitte einen YouTube-Account auswählen", level=messages.ERROR,
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

        print(merged)

        for time, defaults in merged.items():
            obj, created = YouTubeTrafficSource.objects.update_or_create(
                youtube=youtube, date=time, defaults=defaults,
            )

        self.message_user(request, "Datei wurde erfolgreich eingelesen!")


def parse_duration(duration):
    hours, minutes, seconds = re.match(r"(\d+):(\d+):(\d+)", duration).groups()
    return timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds))


class ViewerAgeAdmin(UploadFileMixin, admin.ModelAdmin):
    upload_form_class = UploadFileFormYouTube

    list_display = ["date", "youtube", "interval"]
    list_display_links = ["date"]
    list_filter = ["youtube", "interval"]
    date_hierarchy = "date"

    readonly_fields = ["last_updated"]

    def process_uploaded_file(self, request, file):
        filename = file.name
        name_pattern = r"Viewer age (\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2}).*"
        parsed_name = re.match(name_pattern, filename)

        if not parsed_name:
            self.message_user(
                request,
                "Die Datei scheint keine Viewer-Age Daten zu enthalten! "
                'Wähle den Tab "Viewer Age" in den YouTube Studio Analytics.',
                level=messages.ERROR,
            )
            return

        start_date, end_date = parsed_name.groups()
        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)

        # Get interval from dates
        if (
            start_date.day == 1
            and end_date.day == 1
            and end_date.month - start_date.month == 1
            and start_date.year == end_date.year
        ):
            interval = "monthly"
        elif end_date - start_date == timedelta(weeks=1) and start_date.weekday() == 0:
            interval = "weekly"
        elif end_date - start_date == timedelta(days=1):
            interval = "daily"
        else:
            self.message_user(
                request,
                "Der Export-Zeitraum kann nicht als Monat, Woche (Mo - So) oder einzelner Tag erkannt werden.",
                level=messages.ERROR,
            )
            return

        df = pd.read_csv(self.open_zip(file)["Table data.csv"])
        print(df)

        if not request.POST["youtube"]:
            self.message_user(
                request, "Bitte einen YouTube-Account auswählen", level=messages.ERROR,
            )
            return

        youtube = YouTube.objects.get(id=request.POST["youtube"])

        # Transpose so the age range is the column
        df = df.rename(columns={"Viewer age": "type"}).set_index("type").transpose()
        print(df)

        field_for_type = {
            "Average view duration": "average_view_duration",
            "Views (%)": "views",
            "Average percentage viewed (%)": "average_percentage_viewed",
            "Watch time (hours) (%)": "watch_time",
        }

        ranges = {}

        for index, row in df.iterrows():
            if index == "Average view duration":
                obj = YouTubeAgeRangeDuration(
                    age_13_17=parse_duration(row["AGE_13_17"]),
                    age_18_24=parse_duration(row["AGE_18_24"]),
                    age_25_34=parse_duration(row["AGE_25_34"]),
                    age_35_44=parse_duration(row["AGE_35_44"]),
                    age_45_54=parse_duration(row["AGE_45_54"]),
                    age_55_64=parse_duration(row["AGE_55_64"]),
                    age_65_plus=parse_duration(row["AGE_65_"]),
                )
            else:
                obj = YouTubeAgeRangePercentage(
                    age_13_17=Decimal(row["AGE_13_17"]),
                    age_18_24=Decimal(row["AGE_18_24"]),
                    age_25_34=Decimal(row["AGE_25_34"]),
                    age_35_44=Decimal(row["AGE_35_44"]),
                    age_45_54=Decimal(row["AGE_45_54"]),
                    age_55_64=Decimal(row["AGE_55_64"]),
                    age_65_plus=Decimal(row["AGE_65_"]),
                )

            obj.save()
            ranges[field_for_type[index]] = obj

        obj, created = YouTubeViewerAge.objects.update_or_create(
            youtube=youtube, date=start_date, interval=interval, defaults=ranges,
        )

        self.message_user(request, "Datei wurde erfolgreich eingelesen!")


class AnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        "date",
        "youtube",
        "interval",
        "views",
        "likes",
        "dislikes",
        "estimated_minutes_watched",
        "average_view_duration",
    ]
    list_display_links = ["date"]
    list_filter = ["youtube", "interval"]
    date_hierarchy = "date"


class AgeRangeDurationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "age_13_17",
        "age_18_24",
        "age_25_34",
        "age_35_44",
        "age_45_54",
        "age_55_64",
        "age_65_plus",
    ]
    list_display_links = ["id"]
    list_filter = []


class AgeRangePercentageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "age_13_17",
        "age_18_24",
        "age_25_34",
        "age_35_44",
        "age_45_54",
        "age_55_64",
        "age_65_plus",
    ]
    list_display_links = ["id"]
    list_filter = []
    date_hierarchy = None


admin.site.register(YouTube, QuintlyAdmin)
admin.site.register(YouTubeAnalytics, AnalyticsAdmin)
admin.site.register(YouTubeTrafficSource, TrafficSourceAdmin)
admin.site.register(YouTubeViewerAge, ViewerAgeAdmin)
admin.site.register(YouTubeAgeRangeDuration, AgeRangeDurationAdmin)
admin.site.register(YouTubeAgeRangePercentage, AgeRangePercentageAdmin)