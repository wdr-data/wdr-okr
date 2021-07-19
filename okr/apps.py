from django.apps import AppConfig
from . import patch_django_extensions


class OkrConfig(AppConfig):
    name = "okr"
    verbose_name = "OKR - Objectives and Key Results"

    def ready(self):
        # Import the scheduler module as we need it to register the save signals
        from .scrapers import scheduler  # noqa: F401

        patch_django_extensions.patch()

        return super().ready()
