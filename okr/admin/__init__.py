"""Module for Django backend."""

from django.contrib import admin
from . import insta
from . import youtube
from . import podcasts
from . import pages
from . import tiktok

admin.site.site_header = "STAGING | Django WDR OKR"
admin.site.site_title = "STAGING | Django WDR OKR"
admin.site.index_title = "Home"
