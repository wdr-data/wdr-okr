"""Configure scheduler to call scraper modules."""

from okr.models.pages import SophoraNode
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR
from django.db.models.signals import post_save
from django.dispatch import receiver
from sentry_sdk import capture_exception
from loguru import logger

from ..models import Podcast, Insta, YouTube, TikTok, Property
from . import insta, youtube, podcasts, pages, tiktok
from .common.utils import BERLIN
from .db_cleanup import run_db_cleanup


scheduler = None


def sentry_listener(event):
    """Forward exception of event to Sentry."""
    if event.exception:
        capture_exception(event.exception)


def setup():
    """Create and start scheduler instance."""
    global scheduler

    # Prevent setting up multiple schedulers
    if scheduler:
        return

    scheduler = BackgroundScheduler(timezone=BERLIN)
    scheduler.start()


def add_jobs():
    """Add and define scheduler for each scraper module.

    Controls schedules for:

    * :meth:`~okr.scrapers.insta.scrape_insights`
    * :meth:`~okr.scrapers.insta.scrape_stories`
    * :meth:`~okr.scrapers.insta.scrape_posts`
    * :meth:`~okr.scrapers.youtube.scrape_analytics`
    * :meth:`~okr.scrapers.podcasts.scrape_feed`
    * :meth:`~okr.scrapers.podcasts.scrape_itunes_reviews`
    * :meth:`~okr.scrapers.podcasts.scrape_spotify_api`
    * :meth:`~okr.scrapers.podcasts.scrape_podstat`
    * :meth:`~okr.scrapers.podcasts.scrape_podcast_data_webtrekk_picker`
    * :meth:`~okr.scrapers.podcasts.scrape_episode_data_webtrekk_performance`
    * :meth:`~okr.scrapers.podcasts.scrape_spotify_experimental_performance`
    * :meth:`~okr.scrapers.pages.scrape_sophora_nodes`
    * :meth:`~okr.scrapers.pages.scrape_gsc`
    * :meth:`~okr.scrapers.pages.scrape_webtrekk`
    """

    scheduler.add_listener(sentry_listener, EVENT_JOB_ERROR)

    # Meta
    scheduler.add_job(
        run_db_cleanup,
        trigger="cron",
        hour="19",
        minute="0",
    )

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

    # TikTok
    scheduler.add_job(
        tiktok.scrape_data,
        args=["daily"],
        trigger="cron",
        hour="2",
        minute="00",
    )
    scheduler.add_job(
        tiktok.scrape_data,
        args=["weekly"],
        trigger="cron",
        hour="2",
        minute="10",
    )
    scheduler.add_job(
        tiktok.scrape_data,
        args=["monthly"],
        trigger="cron",
        hour="2",
        minute="20",
    )
    scheduler.add_job(
        tiktok.scrape_posts,
        trigger="cron",
        hour="2",
        minute="30",
    )

    # Podcasts
    scheduler.add_job(
        podcasts.scrape_feed,
        trigger="cron",
        hour="*",
        minute="30",
    )
    scheduler.add_job(
        podcasts.scrape_itunes_reviews,
        trigger="cron",
        hour="19",
        minute="15",
    )
    scheduler.add_job(
        podcasts.scrape_spotify_api,
        trigger="cron",
        hour="9",
        minute="0",
    )
    scheduler.add_job(
        podcasts.scrape_podstat,
        trigger="cron",
        hour="4",
        minute="0",
    )
    scheduler.add_job(
        podcasts.scrape_podcast_data_webtrekk_picker,
        trigger="cron",
        hour="5",
        minute="0",
    )
    scheduler.add_job(
        podcasts.scrape_episode_data_webtrekk_performance,
        trigger="cron",
        hour="12",
        minute="0",
    )
    scheduler.add_job(
        podcasts.scrape_spotify_experimental_demographics,
        trigger="cron",
        hour="8",
        minute="0",
    )
    scheduler.add_job(
        podcasts.scrape_spotify_experimental_performance,
        trigger="cron",
        hour="3",
        minute="0",
    )

    # Pages
    scheduler.add_job(
        pages.scrape_sophora_nodes,
        trigger="cron",
        minute="*/5",
    )
    scheduler.add_job(
        pages.scrape_gsc,
        trigger="cron",
        hour="17",
        minute="0",
    )
    scheduler.add_job(
        pages.scrape_webtrekk,
        trigger="cron",
        hour="14",
        minute="0",
    )


@receiver(post_save, sender=Podcast)
def podcast_created(instance: Podcast, created: bool, **kwargs):
    """Start scraper run for newly added podcast
    (:meth:`okr.scrapers.podcasts.scrape_full`).

    Args:
        instance (Podcast): A Podcast instance
        created (bool): Start scraper if set to True
    """
    logger.debug("{} saved, created={}", instance, created)
    if created:
        scheduler.add_job(podcasts.scrape_full, args=[instance], max_instances=1)


@receiver(post_save, sender=Insta)
def insta_created(instance: Insta, created: bool, **kwargs):
    """Start scraper run for newly added Instagram account
    (:meth:`okr.scrapers.insta.scrape_full`).

    Args:
        instance (Insta): An Insta instance
        created (bool): Don't start scraper if set to False
    """
    logger.debug("{} saved, created={}", instance, created)
    if created:
        scheduler.add_job(insta.scrape_full, args=[instance], max_instances=1)


@receiver(post_save, sender=YouTube)
def youtube_created(instance: YouTube, created: bool, **kwargs):
    """Start scraper run for newly added Youtube channel
    (:meth:`okr.scrapers.youtube.scrape_full`).

    Args:
        instance (YouTube): A YouTube instance
        created (bool): Don't start scraper if set to False
    """
    logger.debug("{} saved, created={}", instance, created)
    if created:
        scheduler.add_job(youtube.scrape_full, args=[instance], max_instances=1)


@receiver(post_save, sender=Property)
def property_created(instance: Property, created: bool, **kwargs):
    """Start scraper run for newly added GSC property
    (:meth:`okr.scrapers.pages.scrape_full_gsc`).

    Args:
        instance (Property): A Property instance
        created (bool): Start scraper if set to True
    """
    logger.debug("{} saved, created={}", instance, created)
    if created:
        scheduler.add_job(pages.scrape_full_gsc, args=[instance], max_instances=1)


@receiver(post_save, sender=SophoraNode)
def sophora_node_created(instance: SophoraNode, created: bool, **kwargs):
    """Start scraper run for newly added Sophora node
    (:meth:`okr.scrapers.pages.scrape_full_sophora`).

    Args:
        instance (SophoraNode): A SophoraNode instance
        created (bool): Start scraper if set to True
    """
    logger.debug("{} saved, created={}", instance, created)
    if created:
        scheduler.add_job(pages.scrape_full_sophora, args=[instance], max_instances=1)


@receiver(post_save, sender=TikTok)
def tiktok_created(instance: TikTok, created: bool, **kwargs):
    """Start scraper run for newly added TikTok account
    (:meth:`okr.scrapers.tiktok.scrape_full`).

    Args:
        instance (TikTok): A TikTok instance
        created (bool): Start scraper if set to True
    """
    logger.debug("{} saved, created={}", instance, created)
    if created:
        scheduler.add_job(tiktok.scrape_full, args=[instance], max_instances=1)
