from collections import defaultdict
from datetime import date

from django import forms
from django.contrib import admin
from django.contrib import messages
import pandas as pd

from ..models import YouTube, YouTubeAnalytics, YouTubeTrafficSource
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

        for index, row in df.iterrows():
            time = date.fromisoformat(row["Date"])

            field = field_for_source[row["Traffic source"]]
            merged[time][field] = row["Impressions"]

        print(merged)

        for time, defaults in merged.items():
            obj, created = YouTubeTrafficSource.objects.update_or_create(
                youtube=youtube, time=time, defaults=defaults,
            )

        self.message_user(request, "Datei wurde erfolgreich eingelesen!")


admin.site.register(YouTube)
admin.site.register(YouTubeAnalytics)
admin.site.register(YouTubeTrafficSource, TrafficSourceAdmin)
