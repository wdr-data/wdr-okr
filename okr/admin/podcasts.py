"""Forms for adding and editing podcasts
"""

from datetime import date, timedelta
from decimal import Decimal
import re
import functools

from django import forms
from django.contrib import admin
from django.contrib import messages

from ..models import (
    Podcast,
    PodcastEpisode,
    PodcastDataSpotify,
    PodcastDataSpotifyHourly,
    PodcastEpisodeDataSpotifyUser,
    PodcastEpisodeDataSpotifyPerformance,
    PodcastEpisodeDataSpotify,
    PodcastEpisodeDataPodstat,
    PodcastEpisodeDataWebtrekkPerformance,
)
from .base import ProductAdmin
from ..scrapers.podcasts import feed
from ..scrapers.podcasts.spotify_api import spotify_api, fetch_all


class FeedForm(forms.ModelForm):
    """Form for adding a new podcast

    This form processes a feed url inputted by the user. It adds a new podcast to
    the database and initiates a scraper run to collect basic data about the
    podcast.
    """

    class Meta:
        model = Podcast
        fields = ["feed_url"]

    feed_url = forms.URLField(label="Feed URL")

    def save(self, commit=True):
        d = feed.parse(self.instance.feed_url)

        self.instance.name = d.feed.title
        self.instance.author = d.feed.author
        self.instance.image = d.feed.image.href
        self.instance.description = d.feed.description

        licensed_podcasts = spotify_api.licensed_podcasts()
        spotify_podcasts = fetch_all(
            functools.partial(spotify_api.shows, market="DE"),
            list(
                uri.replace("spotify:show:", "")
                for uri in licensed_podcasts["shows"].keys()
            ),
            "shows",
        )

        spotify_podcast_id = next(
            (p["id"] for p in spotify_podcasts if p and p["name"] == d.feed.title), None
        )
        self.instance.spotify_id = spotify_podcast_id

        return super().save(commit=commit)


class PodcastAdmin(ProductAdmin):
    """List for choosing an existing podcast to edit"""

    list_display = ProductAdmin.list_display + ["author", "spotify_id"]
    list_filter = ["author"]

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return FeedForm
        return super().get_form(request, obj=obj, **kwargs)


class DataSpotifyAdmin(admin.ModelAdmin):
    """List for choosing existing Spotify podcast user data to edit"""

    list_display = [
        "podcast",
        "date",
        "followers",
        "listeners",
        "listeners_weekly",
        "listeners_monthly",
        "listeners_all_time",
    ]
    list_display_links = ["podcast", "date"]
    list_filter = ["podcast"]
    date_hierarchy = "date"


class DataSpotifyHourlyAdmin(admin.ModelAdmin):
    """List for choosing existing Spotify hourly podcast data to edit"""

    list_display = [
        "podcast",
        "date_time",
        "starts",
        "streams",
    ]
    list_display_links = ["podcast", "date_time"]
    list_filter = ["podcast"]
    date_hierarchy = "date_time"


class EpisodeAdmin(admin.ModelAdmin):
    """List for choosing existing podcast episode data to edit"""

    list_display = [
        "title",
        "podcast",
        "publication_date_time",
        "zmdb_id",
        "spotify_id",
        "duration",
    ]
    list_display_links = ["title"]
    list_filter = ["podcast"]
    date_hierarchy = "publication_date_time"


class EpisodeDataSpotifyAdmin(admin.ModelAdmin):
    """List for choosing existing Spotify podcast episode data to edit"""

    list_display = [
        "episode",
        "date",
        "starts",
        "streams",
        "listeners",
        "listeners_all_time",
    ]
    list_display_links = ["episode", "date"]
    list_filter = []
    date_hierarchy = "date"


class EpisodeDataSpotifyUserAdmin(admin.ModelAdmin):
    """List for choosing existing Spotify episode user data to edit"""

    list_display = [
        "episode",
        "date",
        "age_0_17",
        "age_18_22",
        "age_23_27",
        "age_28_34",
        "age_35_44",
        "age_45_59",
        "age_60_150",
        "age_unknown",
        "gender_female",
        "gender_male",
        "gender_non_binary",
        "gender_not_specified",
    ]
    list_display_links = ["episode", "date"]
    list_filter = []
    date_hierarchy = "date"


class EpisodeDataSpotifyPerformanceAdmin(admin.ModelAdmin):
    """List for choosing existing Spotify episode performance data to edit"""

    list_display = [
        "episode",
        "date",
        "average_listen",
        "quartile_1",
        "quartile_2",
        "quartile_3",
        "complete",
    ]
    list_display_links = ["episode", "date"]
    list_filter = []
    date_hierarchy = "date"


class EpisodeDataWebtrekkPerformanceAdmin(admin.ModelAdmin):
    """List for choosing existing Webtrekk episode performance data to edit"""

    list_display = [
        "episode",
        "date",
        "media_views",
        "media_views_complete",
        "playing_time",
    ]
    list_display_links = ["episode", "date"]
    list_filter = []
    date_hierarchy = "date"


class EpisodeDataPodstatAdmin(admin.ModelAdmin):
    """List for choosing existing Podstat episode data to edit"""

    list_display = [
        "episode",
        "date",
        "downloads",
        "ondemand",
    ]
    list_display_links = ["episode", "date"]
    list_filter = []
    date_hierarchy = "date"


admin.site.register(Podcast, PodcastAdmin)
admin.site.register(PodcastEpisode, EpisodeAdmin)
admin.site.register(PodcastDataSpotify, DataSpotifyAdmin)
admin.site.register(PodcastDataSpotifyHourly, DataSpotifyHourlyAdmin)
admin.site.register(PodcastEpisodeDataSpotify, EpisodeDataSpotifyAdmin)
admin.site.register(PodcastEpisodeDataSpotifyUser, EpisodeDataSpotifyUserAdmin)
admin.site.register(
    PodcastEpisodeDataSpotifyPerformance, EpisodeDataSpotifyPerformanceAdmin
)
admin.site.register(
    PodcastEpisodeDataWebtrekkPerformance, EpisodeDataWebtrekkPerformanceAdmin
)
admin.site.register(PodcastEpisodeDataPodstat, EpisodeDataPodstatAdmin)
