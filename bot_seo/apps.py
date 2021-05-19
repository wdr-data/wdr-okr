import sys

from django.apps import AppConfig
from django.conf import settings


class BotSeoConfig(AppConfig):
    name = "bot_seo"
    verbose_name = "Teams-Bot für SEO"

    def ready(self):
        # Don't schedule stuff if we aren't running a server (during migrations etc.)
        if "manage.py" in sys.argv and "runserver" not in sys.argv:
            return super().ready()

        from . import scheduler

        scheduler.setup()

        if not settings.DEBUG:
            scheduler.add_jobs()

        return super().ready()
