import sys

from django.apps import AppConfig
from django.conf import settings
from . import patch_django_extensions


class OkrConfig(AppConfig):
    name = "okr"
    verbose_name = "OKR - Objectives and Key Results"

    def ready(self):
        # Don't schedule stuff if we aren't running a server (during migrations etc.)
        if "manage.py" in sys.argv and "runserver" not in sys.argv:
            return super().ready()

        from .scrapers import scheduler

        scheduler.setup()

        if not settings.DEBUG:
            scheduler.add_jobs()

        patch_django_extensions.patch()

        return super().ready()
