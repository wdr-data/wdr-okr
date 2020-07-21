from django.apps import AppConfig


class OkrConfig(AppConfig):
    name = "okr"
    verbose_name = "OKR - Objectives and Key Results"

    def ready(self):
        from .scrapers import scheduler

        scheduler.start()
        return super().ready()
