from django.apps import AppConfig
from django.conf import settings
from . import patch_django_extensions


class OkrConfig(AppConfig):
    name = "okr"
    verbose_name = "OKR - Objectives and Key Results"

    def ready(self):
        from .scrapers import scheduler

        scheduler.setup()

        if not settings.DEBUG:
            scheduler.add_jobs()

        patch_django_extensions.patch()

        return super().ready()
