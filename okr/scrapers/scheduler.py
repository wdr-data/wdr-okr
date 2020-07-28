from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from pytz import timezone

from ..models import Podcast, Insta, YouTube
from . import insta, youtube, podcasts


berlin = timezone("Europe/Berlin")

scheduler = None


def start():
    global scheduler
    scheduler = BackgroundScheduler(timezone=berlin)
    scheduler.start()

    if settings.DEBUG:
        return

    # Instagram
    scheduler.add_job(
        insta.scrape_insights,
        args=["daily"],
        trigger="cron",
        hour="5,11,17,23",
        minute="30",
    )
    scheduler.add_job(
        insta.scrape_insights, args=["weekly"], trigger="cron", hour="6", minute="0",
    )
    scheduler.add_job(
        insta.scrape_insights, args=["monthly"], trigger="cron", hour="6", minute="1",
    )
    scheduler.add_job(
        insta.scrape_stories, trigger="cron", hour="5,11,17,23", minute="31",
    )
    scheduler.add_job(
        insta.scrape_posts, trigger="cron", hour="5,11,17,23", minute="32",
    )

    # YouTube
    scheduler.add_job(
        youtube.scrape_analytics,
        args=["daily"],
        trigger="cron",
        hour="5,11,17,23",
        minute="35",
    )
    scheduler.add_job(
        youtube.scrape_analytics, args=["weekly"], trigger="cron", hour="6", minute="5",
    )
    scheduler.add_job(
        youtube.scrape_analytics,
        args=["monthly"],
        trigger="cron",
        hour="6",
        minute="6",
    )

    # Podcasts
    scheduler.add_job(
        podcasts.scrape_feed, trigger="cron", hour="4,10,16,22", minute="0"
    )
    scheduler.add_job(podcasts.scrape_spotify, trigger="cron", hour="4", minute="15")
    scheduler.add_job(podcasts.scrape_podstat, trigger="cron", hour="4", minute="30")


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
