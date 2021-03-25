from django.apps import AppConfig
from django.conf import settings


class BotSeoConfig(AppConfig):
    name = "bot_seo"
    verbose_name = "Teams-Bot für SEO"

    def ready(self):
        # from .scrapers import scheduler

        # scheduler.setup()

        # if not settings.DEBUG:
        #     scheduler.add_jobs()

        return super().ready()
