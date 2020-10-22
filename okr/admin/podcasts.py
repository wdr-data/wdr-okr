from datetime import date, timedelta
from decimal import Decimal
import re

from django import forms
from django.contrib import admin
from django.contrib import messages

from ..models import (
    Podcast,
    PodcastEpisode,
    PodcastDataSpotifyFollowers,
    PodcastEpisodeDataSpotifyUser,
    PodcastEpisodeDataSpotifyPerformance,
    PodcastEpisodeDataSpotify,
    PodcastEpisodeDataPodstat,
)
from .base import ProductAdmin


class PodcastAdmin(ProductAdmin):
    list_display = ProductAdmin.list_display + [
        "author",
    ]
    list_filter = ["author"]


class DataSpotifyFollowersAdmin(admin.ModelAdmin):
    list_display = [
        "podcast",
        "date",
        "followers",
    ]
    list_display_links = ["podcast", "date"]
    list_filter = ["podcast"]
    date_hierarchy = "date"


class EpisodeAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "podcast",
        "publication_date_time",
        "zmdb_id",
        "duration",
    ]
    list_display_links = ["title"]
    list_filter = ["podcast"]
    date_hierarchy = "publication_date_time"


class EpisodeDataSpotifyAdmin(admin.ModelAdmin):
    list_display = [
        "episode",
        "date",
        "starts",
        "streams",
        "listeners",
    ]
    list_display_links = ["episode", "date"]
    list_filter = []
    date_hierarchy = "date"


class EpisodeDataSpotifyUserAdmin(admin.ModelAdmin):
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


class EpisodeDataPodstatAdmin(admin.ModelAdmin):
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
admin.site.register(PodcastDataSpotifyFollowers, DataSpotifyFollowersAdmin)
admin.site.register(PodcastEpisodeDataSpotify, EpisodeDataSpotifyAdmin)
admin.site.register(PodcastEpisodeDataSpotifyUser, EpisodeDataSpotifyUserAdmin)
admin.site.register(
    PodcastEpisodeDataSpotifyPerformance, EpisodeDataSpotifyPerformanceAdmin
)
admin.site.register(PodcastEpisodeDataPodstat, EpisodeDataPodstatAdmin)
