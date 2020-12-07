"""Configure scheduler to call scraper modules.
"""

from okr.models.pages import SophoraNode
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from sentry_sdk import capture_exception

from ..models import Podcast, Insta, YouTube, Property
from . import insta, youtube, podcasts, pages
from .common.utils import BERLIN


scheduler = None


def sentry_listener(event):
    if event.exception:
        capture_exception(event.exception)


def start():
    """Add and define scheduler for each scraper module."""
    global scheduler
    scheduler = BackgroundScheduler(timezone=BERLIN)
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
    scheduler.add_job(
        podcasts.scrape_feed,
        trigger="cron",
        hour="1,11",
        minute="0",
    )
    scheduler.add_job(
        podcasts.scrape_spotify_mediatrend,
        trigger="cron",
        hour="2",
        minute="30",
    )
    scheduler.add_job(
        podcasts.scrape_spotify_api,
        trigger="cron",
        hour="12",
        minute="0",
    )
    scheduler.add_job(
        podcasts.scrape_podstat,
        trigger="cron",
        hour="8",
        minute="30",
    )
    scheduler.add_job(
        podcasts.scrape_episode_data_webtrekk_performance,
        trigger="cron",
        hour="4",
        minute="0",
    )

    # Pages
    scheduler.add_job(
        pages.scrape_sophora_nodes,
        trigger="cron",
        hour="*",
        minute="45",
    )
    scheduler.add_job(
        pages.scrape_gsc,
        trigger="cron",
        hour="17",
        minute="0",
    )


@receiver(post_save, sender=Podcast)
def podcast_created(instance: Podcast, created: bool, **kwargs):
    """Start scraper run for newly added podcast.

    Args:
        instance (Podcast): A Podcast instance
        created (bool): Start scraper if set to True
    """
    print(instance, created)
    if created:
        scheduler.add_job(podcasts.scrape_full, args=[instance], max_instances=1)


@receiver(post_save, sender=Insta)
def insta_created(instance: Insta, created: bool, **kwargs):
    """Start scraper run for newly added Instagram account.

    Args:
        instance (Insta): An Insta instance
        created (bool): Don't start scraper if set to False
    """
    print(instance, created)
    if created:
        scheduler.add_job(insta.scrape_full, args=[instance], max_instances=1)


@receiver(post_save, sender=YouTube)
def youtube_created(instance: YouTube, created: bool, **kwargs):
    """Start scraper run for newly added Youtube channel.

    Args:
        instance (YouTube): A YouTube instance
        created (bool): Don't start scraper if set to False
    """
    print(instance, created)
    if created:
        scheduler.add_job(youtube.scrape_full, args=[instance], max_instances=1)


@receiver(post_save, sender=Property)
def property_created(instance: Property, created: bool, **kwargs):
    """Start scraper run for newly added property.

    Args:
        instance (Property): A Property instance
        created (bool): Start scraper if set to True
    """
    print(instance, created)
    if created:
        scheduler.add_job(pages.scrape_full_gsc, args=[instance], max_instances=1)


@receiver(post_save, sender=SophoraNode)
def property_created(instance: SophoraNode, created: bool, **kwargs):
    """Start scraper run for newly added Sophora node.

    Args:
        instance (SophoraNode): A SophoraNode instance
        created (bool): Start scraper if set to True
    """
    print(instance, created)
    if created:
        scheduler.add_job(pages.scrape_full_sophora, args=[instance], max_instances=1)
