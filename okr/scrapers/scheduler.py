from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from pytz import timezone
from sentry_sdk import capture_exception

from ..models import Podcast, Insta, YouTube
from . import insta, youtube, podcasts


berlin = timezone("Europe/Berlin")

scheduler = None


def sentry_listener(event):
    if event.exception:
        capture_exception(event.exception)


def start():
    global scheduler
    scheduler = BackgroundScheduler(timezone=berlin)
    scheduler.start()

    if settings.DEBUG:
        return

    scheduler.add_listener(sentry_listener, EVENT_JOB_ERROR)

    # Instagram
    scheduler.add_job(
        insta.scrape_insights,
        args=["daily"],
        trigger="cron",
        hour="5,11,17,23",
        minute="30",
    )
    scheduler.add_job(
        insta.scrape_insights,
        args=["weekly"],
        trigger="cron",
        hour="6",
        minute="0",
    )
    scheduler.add_job(
        insta.scrape_insights,
        args=["monthly"],
        trigger="cron",
        hour="6",
        minute="1",
    )
    scheduler.add_job(
        insta.scrape_stories,
        trigger="cron",
        hour="5",
        minute="31",
    )
    scheduler.add_job(
        insta.scrape_posts,
        trigger="cron",
        hour="5",
        minute="32",
    )

    # YouTube
    scheduler.add_job(
        youtube.scrape_analytics,
        args=["daily"],
        trigger="cron",
        hour="5",
        minute="35",
    )
    scheduler.add_job(
        youtube.scrape_analytics,
        args=["weekly"],
        trigger="cron",
        hour="6",
        minute="5",
    )
    scheduler.add_job(
        youtube.scrape_analytics,
        args=["monthly"],
        trigger="cron",
        hour="6",
        minute="6",
    )

    # Podcasts
    scheduler.add_job(podcasts.scrape_feed, trigger="cron", hour="1,11", minute="0")
    scheduler.add_job(
        podcasts.scrape_spotify_mediatrend, trigger="cron", hour="2", minute="30"
    )
    scheduler.add_job(
        podcasts.scrape_spotify_api, trigger="cron", hour="12", minute="0"
    )
    scheduler.add_job(podcasts.scrape_podstat, trigger="cron", hour="8", minute="30")
    scheduler.add_job(podcasts.scrape_episode_data_webtrekk_performance, trigger="cron", hour="4", minute="0")


@receiver(post_save, sender=Podcast)
def podcast_created(instance, created, **kwargs):
    print(instance, created)
    if created:
        scheduler.add_job(podcasts.scrape_full, args=[instance])


@receiver(post_save, sender=Insta)
def insta_created(instance, created, **kwargs):
    print(instance, created)
    if created:
        scheduler.add_job(insta.scrape_full, args=[instance])


@receiver(post_save, sender=YouTube)
def youtube_created(instance, created, **kwargs):
    print(instance, created)
    if created:
        scheduler.add_job(youtube.scrape_full, args=[instance])
