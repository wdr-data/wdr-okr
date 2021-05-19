"""Module for Django backend."""
# flake8: noqa

from django.contrib import admin
from . import facebook
from . import twitter
from . import insta
from . import youtube
from . import podcasts
from . import pages
from . import tiktok
from . import custom

admin.site.site_header = "Django WDR OKR"
admin.site.site_title = "Django WDR OKR"
admin.site.index_title = "Home"
