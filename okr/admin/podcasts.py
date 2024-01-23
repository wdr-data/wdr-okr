"""Forms for managing podcast data."""

import functools
from typing import Any, Dict
from time import sleep

from django import forms
from django.contrib import admin
from django.db import models
from django.forms import ValidationError
from loguru import logger
from sentry_sdk import capture_exception

from ..models import (
    Podcast,
    PodcastITunesRating,
    PodcastITunesReview,
    PodcastEpisode,
    PodcastDataWebtrekkPicker,
    PodcastDataSpotify,
    PodcastDataSpotifyHourly,
    PodcastDataSpotifyDemographics,
    PodcastEpisodeDataSpotifyUser,
    PodcastEpisodeDataSpotifyPerformance,
    PodcastEpisodeDataSpotify,
    PodcastEpisodeDataPodstat,
    PodcastEpisodeDataWebtrekkPerformance,
    PodcastEpisodeDataSpotifyDemographics,
    PodcastCategory,
    PodcastEpisodeDataArdAudiothekPerformance,
)
from .base import ProductAdmin
from .mixins import UnrequiredFieldsMixin, large_table
from ..scrapers.podcasts import feed
from ..scrapers.podcasts.spotify_api import spotify_api


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
    spotify_id = forms.CharField(
        label="Spotify ID",
        help_text="Nicht erforderlich. Die Spotify ID kann hier manuell angegeben werden, falls die automatische Erkennung nicht funktioniert.",
        required=False,
    )

    def clean(self) -> Dict[str, Any]:
        try:
            feed_dict = feed.parse(self.cleaned_data["feed_url"])
        except Exception as e:
            capture_exception(e)
            raise ValidationError(
                {"feed_url": "Die URL scheint keinen gültigen Feed zu enthalten."}
            ) from e

        existing_podcast = Podcast.objects_all.filter(name=feed_dict.feed.title).first()
        if existing_podcast:
            raise ValidationError(
                {
                    "feed_url": f"Ein Podcast mit dem Namen „{feed_dict.feed.title}“ existiert bereits!"
                }
            )

        self.feed_dict = feed_dict

        # Load licensed podcasts and their names so we can get the spotify_id for this podcast later
        # We do it here so we can raise a validation error if the Spotify API is not available
        try:
            licensed_podcasts = spotify_api.licensed_podcasts()
        except Exception as e:
            logger.exception(e)
            capture_exception(e)
            raise ValidationError(
                "Spotify API nicht erreichbar. Bitte versuchen Sie es später erneut."
            ) from e

        licensed_ids = list(
            uri.replace("spotify:show:", "")
            for uri in licensed_podcasts["shows"].keys()
        )

        spotify_id = None

        if self.cleaned_data["spotify_id"] in licensed_ids:
            spotify_id = self.cleaned_data["spotify_id"]
        elif (
            self.cleaned_data["spotify_id"]
            and self.cleaned_data["spotify_id"] not in licensed_ids
        ):
            raise ValidationError(
                "Die angegebene Spotify ID ist nicht nicht bekannt. Bitte geben Sie eine andere ID an oder lassen Sie das Feld frei, um eine automatische Zuordnung zu versuchen."
            )
        # Try searching for the podcast name in the Spotify API
        else:
            results = spotify_api.search(feed_dict.feed.title, type="show", market="DE")
            for item in results["shows"]["items"]:
                logger.info("Found Spotify podcast: {}", item)
                if item is None:
                    continue

                if item["name"] == feed_dict.feed.title and item["id"] in licensed_ids:
                    spotify_id = item["id"]
                    break

        self._spotify_id = spotify_id

        return super().clean()

    def save(self, commit: bool) -> Any:
        d = self.feed_dict

        self.instance.name = d.feed.title
        self.instance.author = d.feed.author
        self.instance.image = d.feed.image.href
        self.instance.description = d.feed.description
        self.instance.itunes_category = d.feed.itunes_category
        self.instance.itunes_subcategory = d.feed.itunes_subcategory
        self.instance.spotify_id = self._spotify_id
        return super().save(commit=commit)


class PodcastAdmin(UnrequiredFieldsMixin, ProductAdmin):
    """List for choosing an existing podcast to edit."""

    list_display = ProductAdmin.list_display + [
        "author",
        "spotify_id",
        "ard_audiothek_id",
        "main_category",
    ]
    list_filter = ProductAdmin.list_filter + [
        "author",
        "categories",
        "main_category",
        "itunes_category",
    ]
    search_fields = ProductAdmin.search_fields + [
        "spotify_id",
        "ard_audiothek_id",
    ]

    unrequired_fields = [
        "itunes_category",
        "itunes_subcategory",
        "categories",
        "main_category",
        "spotify_id",
        "ard_audiothek_id",
        "itunes_url",
    ]

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return FeedForm

        return super().get_form(request, obj=obj, **kwargs)

    def save_related(
        self,
        request: Any,
        form: forms.ModelForm,
        formsets: Any,
        change: bool,
    ) -> None:
        super().save_related(request, form, formsets, change)

        # Ensure that the main category is always added to the regular categories
        obj = form.instance
        if change and obj.main_category:
            logger.info(
                "Adding main category {} to regular categories",
                obj.main_category,
            )
            obj.categories.add(obj.main_category)


class PodcastCategoryAdmin(admin.ModelAdmin):
    """List for choosing existing podcast categories to edit."""

    formfield_overrides = {
        models.TextField: {"widget": forms.TextInput()},
    }

    list_display = ["name", "created"]
    list_display_links = ["name"]
    date_hierarchy = "created"
    search_fields = ["name"]


class PodcastITunesRatingAdmin(admin.ModelAdmin):
    """List for choosing existing iTunes podcast ratings data to edit."""

    list_display = [
        "podcast",
        "date",
        "ratings_average",
        "ratings_count",
    ]
    list_display_links = ["podcast", "date"]
    list_filter = ["podcast"]
    date_hierarchy = "date"


class PodcastITunesReviewAdmin(admin.ModelAdmin):
    """List for choosing existing iTunes podcast reviews data to edit."""

    list_display = [
        "podcast",
        "date",
        "rating",
        "title",
    ]
    list_display_links = ["podcast", "date"]
    list_filter = ["podcast"]
    date_hierarchy = "date"


class PodcastDataSpotifyDemographicsAdmin(admin.ModelAdmin):
    """List for choosing existing Spotify episode demographics data to edit."""

    list_display = [
        "podcast",
        "date",
        "age_range",
        "gender",
        "count",
    ]
    list_display_links = ["podcast", "date"]
    list_filter = ["age_range", "gender", "podcast"]
    date_hierarchy = "date"
    search_fields = ["podcast__name"]


class DataWebtrekkPickerAdmin(admin.ModelAdmin):
    """List for choosing existing Spotify podcast Webtrekk Podcast Picker data to edit."""

    list_display = [
        "podcast",
        "date",
        "visits",
        "visits_campaign",
        "exits",
    ]
    list_display_links = ["podcast", "date"]
    list_filter = ["podcast"]
    date_hierarchy = "date"


class DataSpotifyAdmin(admin.ModelAdmin):
    """List for choosing existing Spotify podcast user data to edit."""

    list_display = [
        "podcast",
        "date",
        "followers",
        "listeners",
        "listeners_7_days",
        "listeners_28_days",
        "listeners_all_time",
    ]
    list_display_links = ["podcast", "date"]
    list_filter = ["podcast"]
    date_hierarchy = "date"


@large_table
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
        "ard_audiothek_id",
        "duration",
        "available",
    ]
    list_display_links = ["title"]
    list_filter = ["podcast", "available"]
    date_hierarchy = "publication_date_time"
    search_fields = ["title", "spotify_id", "ard_audiothek_id", "zmdb_id"]


@large_table
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
    autocomplete_fields = ["episode"]


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
    autocomplete_fields = ["episode"]


@large_table
class EpisodeDataSpotifyDemographicsAdmin(admin.ModelAdmin):
    """List for choosing existing Spotify episode demographics data to edit."""

    list_display = [
        "episode",
        "age_range",
        "gender",
        "count",
    ]
    list_display_links = ["episode"]
    list_filter = ["age_range", "gender", "episode__podcast"]
    search_fields = ["episode__title"]
    autocomplete_fields = ["episode"]


@large_table
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
    autocomplete_fields = ["episode"]


@large_table
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
    autocomplete_fields = ["episode"]


@large_table
class EpisodeDataArdAudiothekPerformanceAdmin(admin.ModelAdmin):
    """List for choosing existing ARD Audiothek episode performance data to edit."""

    list_display = [
        "episode",
        "date",
        "starts",
        "playback_time",
    ]
    list_display_links = ["episode", "date"]
    list_filter = ["episode__podcast"]
    date_hierarchy = "date"
    search_fields = ["episode__title"]
    autocomplete_fields = ["episode"]


@large_table
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
    autocomplete_fields = ["episode"]


admin.site.register(Podcast, PodcastAdmin)
admin.site.register(PodcastEpisode, EpisodeAdmin)
admin.site.register(PodcastCategory, PodcastCategoryAdmin)
admin.site.register(PodcastITunesRating, PodcastITunesRatingAdmin)
admin.site.register(PodcastITunesReview, PodcastITunesReviewAdmin)
admin.site.register(PodcastDataSpotifyDemographics, PodcastDataSpotifyDemographicsAdmin)
admin.site.register(PodcastDataWebtrekkPicker, DataWebtrekkPickerAdmin)
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
admin.site.register(
    PodcastEpisodeDataArdAudiothekPerformance, EpisodeDataArdAudiothekPerformanceAdmin
)
admin.site.register(PodcastEpisodeDataPodstat, EpisodeDataPodstatAdmin)
