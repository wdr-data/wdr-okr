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
    PodcastEpisodeDataPodstatOndemand,
    PodcastEpisodeDataPodstatDownload,
)
from .base import ProductAdmin

admin.site.register(Podcast, ProductAdmin)
admin.site.register(PodcastEpisode)
admin.site.register(PodcastDataSpotifyFollowers)
admin.site.register(PodcastEpisodeDataSpotifyUser)
admin.site.register(PodcastEpisodeDataSpotifyPerformance)
admin.site.register(PodcastEpisodeDataSpotify)
admin.site.register(PodcastEpisodeDataPodstatOndemand)
admin.site.register(PodcastEpisodeDataPodstatDownload)
