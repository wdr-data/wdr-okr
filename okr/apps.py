from django.apps import AppConfig
from . import patch_django_extensions


class OkrConfig(AppConfig):
    name = "okr"
    verbose_name = "OKR - Objectives and Key Results"

    def ready(self):
        from .scrapers import scheduler

        scheduler.start()
        patch_django_extensions.patch()

        return super().ready()
