from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings

from . import podcasts


def start():
    if settings.DEBUG:
        return

    scheduler = BackgroundScheduler()
    scheduler.add_job(podcasts.scrape_feed, trigger="interval", minutes=1)
    scheduler.start()
