"""Forms for managing podcast data."""

import functools

from django import forms
from django.contrib import admin

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
    PodcastEpisodeDataSpotifyDemographics,
    PodcastCategory,
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
        self.instance.itunes_category = d.feed.itunes_category
        self.instance.itunes_subcategory = d.feed.itunes_subcategory

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
    """List for choosing an existing podcast to edit."""

    list_display = ProductAdmin.list_display + [
        "author",
        "spotify_id",
        "itunes_category",
        "itunes_subcategory",
    ]
    list_filter = [
        "author",
        "categories",
        "itunes_category",
        "itunes_subcategory",
    ]

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return FeedForm

        form = super().get_form(request, obj=obj, **kwargs)

        # Allow saving with these fields not filled because
        # Django admin is weird with NULLable string fields
        unrequired_fields = [
            "itunes_category",
            "itunes_subcategory",
            "spotify_id",
        ]

        for field in unrequired_fields:
            form.base_fields[field].required = False

        return form


class PodcastCategoryAdmin(admin.ModelAdmin):
    """List for choosing existing podcast categories to edit."""

    list_display = ["name", "created"]
    list_display_links = ["name"]
    date_hierarchy = "created"
    search_fields = ["name"]


class DataSpotifyAdmin(admin.ModelAdmin):
    """List for choosing existing Spotify podcast user data to edit."""

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
    """List for choosing existing Spotify hourly podcast data to edit."""

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
    """List for choosing existing podcast episode data to edit."""

    list_display = [
        "title",
        "podcast",
        "publication_date_time",
        "zmdb_id",
        "spotify_id",
        "duration",
        "available",
    ]
    list_display_links = ["title"]
    list_filter = ["podcast", "available"]
    date_hierarchy = "publication_date_time"
    search_fields = ["title"]


class EpisodeDataSpotifyAdmin(admin.ModelAdmin):
    """List for choosing existing Spotify podcast episode data to edit."""

    list_display = [
        "episode",
        "date",
        "starts",
        "streams",
        "listeners",
        "listeners_all_time",
    ]
    list_display_links = ["episode", "date"]
    list_filter = ["episode__podcast"]
    date_hierarchy = "date"
    search_fields = ["episode__title"]


class EpisodeDataSpotifyUserAdmin(admin.ModelAdmin):
    """List for choosing existing Spotify episode user data to edit."""

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
    list_filter = ["episode__podcast"]
    date_hierarchy = "date"
    search_fields = ["episode__title"]


class EpisodeDataSpotifyDemographicsAdmin(admin.ModelAdmin):
    """List for choosing existing Spotify episode demographics data to edit."""

    list_display = [
        "episode",
        "date",
        "age_range",
        "gender",
        "count",
    ]
    list_display_links = ["episode", "date"]
    list_filter = ["age_range", "gender", "episode__podcast"]
    date_hierarchy = "date"
    search_fields = ["episode__title"]


class EpisodeDataSpotifyPerformanceAdmin(admin.ModelAdmin):
    """List for choosing existing Spotify episode performance data to edit."""

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
    list_filter = ["episode__podcast"]
    date_hierarchy = "date"
    search_fields = ["episode__title"]


class EpisodeDataWebtrekkPerformanceAdmin(admin.ModelAdmin):
    """List for choosing existing Webtrekk episode performance data to edit."""

    list_display = [
        "episode",
        "date",
        "media_views",
        "media_views_complete",
        "playing_time",
    ]
    list_display_links = ["episode", "date"]
    list_filter = ["episode__podcast"]
    date_hierarchy = "date"
    search_fields = ["episode__title"]


class EpisodeDataPodstatAdmin(admin.ModelAdmin):
    """List for choosing existing Podstat episode data to edit."""

    list_display = [
        "episode",
        "date",
        "downloads",
        "ondemand",
    ]
    list_display_links = ["episode", "date"]
    list_filter = ["episode__podcast"]
    date_hierarchy = "date"
    search_fields = ["episode__title"]


admin.site.register(Podcast, PodcastAdmin)
admin.site.register(PodcastEpisode, EpisodeAdmin)
admin.site.register(PodcastCategory, PodcastCategoryAdmin)
admin.site.register(PodcastDataSpotify, DataSpotifyAdmin)
admin.site.register(PodcastDataSpotifyHourly, DataSpotifyHourlyAdmin)
admin.site.register(PodcastEpisodeDataSpotify, EpisodeDataSpotifyAdmin)
admin.site.register(PodcastEpisodeDataSpotifyUser, EpisodeDataSpotifyUserAdmin)
admin.site.register(
    PodcastEpisodeDataSpotifyDemographics, EpisodeDataSpotifyDemographicsAdmin
)
admin.site.register(
    PodcastEpisodeDataSpotifyPerformance, EpisodeDataSpotifyPerformanceAdmin
)
admin.site.register(
    PodcastEpisodeDataWebtrekkPerformance, EpisodeDataWebtrekkPerformanceAdmin
)
admin.site.register(PodcastEpisodeDataPodstat, EpisodeDataPodstatAdmin)
