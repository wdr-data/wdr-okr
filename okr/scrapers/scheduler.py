"""Configure scheduler to call scraper modules."""

from typing import Any, Callable, List, Mapping, Optional
from concurrent.futures import ThreadPoolExecutor as NativeThreadPoolExecutor

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR
from django.db.models.base import Model
from django.db.models.signals import post_save
from django.dispatch import receiver
from sentry_sdk import capture_exception
from loguru import logger

from ..models import (
    Podcast,
    Insta,
    YouTube,
    TikTok,
    Property,
    Facebook,
    Twitter,
    SophoraNode,
    SnapchatShow,
)
from . import insta, youtube, podcasts, pages, tiktok, facebook, twitter, snapchat_shows
from .common.utils import BERLIN
from .db_cleanup import run_db_cleanup
from app.redis import q


scheduler = None
executors = None


def sentry_listener(event):
    """Forward exception of event to Sentry."""
    if event.exception:
        logger.exception(event.exception)
        capture_exception(event.exception)


def setup():
    """Create and start scheduler instance and set up executors."""
    global scheduler, executors

    # Prevent setting up multiple schedulers
    if scheduler or executors:
        return

    # Set up ThreadPoolExecutors for on-demand tasks received via rq
    executors = {
        "default": NativeThreadPoolExecutor(4),
    }

    initial_executors = {
        f"initial_{model.__name__.lower()}": NativeThreadPoolExecutor(1)
        for model in (
            Facebook,
            Insta,
            Podcast,
            Property,
            SnapchatShow,
            SophoraNode,
            TikTok,
            Twitter,
            YouTube,
        )
    }

    executors.update(initial_executors)

    # Set up scheduler
    scheduler = BackgroundScheduler(
        timezone=BERLIN,
    )
    scheduler.start()


def add_jobs():
    """Add and define scheduler for each scraper module.

    Controls schedules for:

    * :meth:`~okr.scrapers.insta.scrape_insights`
    * :meth:`~okr.scrapers.insta.scrape_stories`
    * :meth:`~okr.scrapers.insta.scrape_posts`
    * :meth:`~okr.scrapers.insta.scrape_comments`
    * :meth:`~okr.scrapers.scrape_demographics`
    * :meth:`~okr.scrapers.scrape_hourly_followers`
    * :meth:`~okr.scrapers.facebook.scrape_insights`
    * :meth:`~okr.scrapers.facebook.scrape_posts`
    * :meth:`~okr.scrapers.twitter.scrape_insights`
    * :meth:`~okr.scrapers.twitter.scrape_tweets`
    * :meth:`~okr.scrapers.youtube.scrape_analytics`
    * :meth:`~okr.scrapers.youtube.scrape_channel_analytics`
    * :meth:`~okr.scrapers.youtube.scrape_videos`
    * :meth:`~okr.scrapers.youtube.scrape_video_analytics`
    * :meth:`~okr.scrapers.youtube.scrape_video_traffic_sources`
    * :meth:`~okr.scrapers.youtube.scrape_video_external_traffic`
    * :meth:`~okr.scrapers.youtube.scrape_video_search_terms`
    * :meth:`~okr.scrapers.youtube.scrape_video_demographics`
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
        trigger="cron",
        hour="5,9,11,17,23",
        minute="30",
    )
    scheduler.add_job(
        insta.scrape_stories,
        trigger="cron",
        hour="5,9",
        minute="52",
    )
    scheduler.add_job(
        insta.scrape_posts,
        trigger="cron",
        hour="5,9",
        minute="43",
    )
    # Deaktiviert, weil IGTV nicht mehr aktiv ist
    # scheduler.add_job(
    #     insta.scrape_igtv,
    #     trigger="cron",
    #     hour="5,9",
    #     minute="50",
    # )
    scheduler.add_job(
        insta.scrape_demographics,
        trigger="cron",
        hour="5,9",
        minute="54",
    )
    scheduler.add_job(
        insta.scrape_hourly_followers,
        trigger="cron",
        hour="5,9",
        minute="56",
    )
    scheduler.add_job(
        insta.scrape_comments,
        trigger="cron",
        hour="5,9",
        minute="58",
    )

    # Facebook
    scheduler.add_job(
        facebook.scrape_insights,
        trigger="cron",
        hour="5,11,17,23",
        minute="40",
    )
    scheduler.add_job(
        facebook.scrape_posts,
        trigger="cron",
        hour="7,12,15",
        minute="32",
    )

    # Twitter
    scheduler.add_job(
        twitter.scrape_insights,
        trigger="cron",
        hour="4,11,17,23",
        minute="50",
    )
    scheduler.add_job(
        twitter.scrape_tweets,
        trigger="cron",
        hour="7,12,15",
        minute="35",
    )

    # YouTube
    scheduler.add_job(
        youtube.scrape_channel_analytics,
        trigger="cron",
        hour="3",
        minute="35",
    )
    scheduler.add_job(
        youtube.scrape_videos,
        trigger="cron",
        hour="3",
        minute="40",
    )
    scheduler.add_job(
        youtube.scrape_video_analytics,
        trigger="cron",
        hour="3",
        minute="45",
    )
    scheduler.add_job(
        youtube.scrape_video_traffic_sources,
        trigger="cron",
        hour="3",
        minute="50",
    )
    scheduler.add_job(
        youtube.scrape_video_external_traffic,
        trigger="cron",
        hour="3",
        minute="55",
    )
    scheduler.add_job(
        youtube.scrape_video_search_terms,
        trigger="cron",
        hour="4",
        minute="5",
    )
    scheduler.add_job(
        youtube.scrape_video_demographics,
        trigger="cron",
        hour="4",
        minute="20",
    )

    # TikTok
    scheduler.add_job(
        tiktok.scrape_data,
        trigger="cron",
        hour="2",
        minute="00",
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
    # Server ist abgeschaltet
    # scheduler.add_job(
    #     podcasts.scrape_podstat,
    #     trigger="cron",
    #     hour="4",
    #     minute="0",
    # )
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

    # TODO: ARD Audiothek API change
    # scheduler.add_job(
    #     podcasts.scrape_ard_audiothek,
    #     trigger="cron",
    #     hour="4",
    #     minute="25",
    # )

    # Pages
    scheduler.add_job(
        pages.scrape_sophora_nodes,
        trigger="cron",
        minute="*/5",
    )
    scheduler.add_job(
        pages.scrape_gsc,
        trigger="cron",
        hour="5",
        minute="5",
    )
    scheduler.add_job(
        pages.scrape_gsc,
        trigger="cron",
        hour="8,12,15",
        minute="30",
    )
    scheduler.add_job(
        pages.scrape_webtrekk,
        trigger="cron",
        hour="11",
        minute="30",
    )

    # Snapchat shows
    scheduler.add_job(
        snapchat_shows.scrape_insights,
        trigger="cron",
        hour="4,9",
        minute="10",
    )
    scheduler.add_job(
        snapchat_shows.scrape_stories,
        trigger="cron",
        hour="4,9",
        minute="15",
    )
    scheduler.add_job(
        snapchat_shows.scrape_story_snaps,
        trigger="cron",
        hour="4,9",
        minute="20",
    )


def run_in_executor(
    func: Callable,
    *,
    args: Optional[List[Any]] = None,
    kwargs: Optional[Mapping[str, Any]] = None,
    executor: str = "default",
):
    """Run a function in a thread pool executor.

    Args:
        func (Callable): The function to be executed in the executor
        args (Optional[List[Any]]): List of positional arguments for ``func``
        kwargs (Optional[Mapping[str, Any]]): Mapping of keyword arguments for ``func``
        executor (str): The name of the executor ``func`` should run in. Defaults to ``"default"``.
    """

    def catcher():
        try:
            func(*(args or []), **(kwargs or {}))
        except Exception as e:
            logger.exception(
                'Function "{}" running in executor "{}" raised an exception.',
                func.__name__,
                executor,
            )
            capture_exception(e)

    executors[executor].submit(catcher)


def run_in_worker(
    func: Callable,
    *,
    args: Optional[List[Any]] = None,
    kwargs: Optional[Mapping[str, Any]] = None,
    executor: str = "default",
):
    """Remotely calls :meth:`~run_in_executor` in the worker process.

    Args:
        func (Callable): The function to be executed in the executor
        args (Optional[List[Any]]): List of positional arguments for ``func``
        kwargs (Optional[Mapping[str, Any]]): Mapping of keyword arguments for ``func``
        executor (str): The name of the executor ``func`` should run in. Defaults to ``"default"``.
    """
    q.enqueue(
        run_in_executor,
        args=(func,),
        kwargs={
            "args": args,
            "kwargs": kwargs,
            "executor": executor,
        },
    )


def _on_created(scraper: Callable, instance: Model):
    """Wrapper for :meth:`~run_in_worker` for signal receivers"""
    run_in_worker(
        scraper,
        args=[instance],
        executor=f"initial_{instance.__class__.__name__.lower()}",
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
        _on_created(podcasts.scrape_full, instance)


@receiver(post_save, sender=Facebook)
def facebook_created(instance: Facebook, created: bool, **kwargs):
    """Start scraper run for newly added Facebook account
    (:meth:`okr.scrapers.facebook.scrape_full`).

    Args:
        instance (Facebook): A Facebook instance
        created (bool): Don't start scraper if set to False
    """
    logger.debug("{} saved, created={}", instance, created)
    if created:
        _on_created(facebook.scrape_full, instance)


@receiver(post_save, sender=Twitter)
def twitter_created(instance: Twitter, created: bool, **kwargs):
    """Start scraper run for newly added Twitter account
    (:meth:`okr.scrapers.twitter.scrape_full`).

    Args:
        instance (Twitter): A Twitter instance
        created (bool): Don't start scraper if set to False
    """
    logger.debug("{} saved, created={}", instance, created)
    if created:
        _on_created(twitter.scrape_full, instance)


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
        _on_created(insta.scrape_full, instance)


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
        _on_created(youtube.scrape_full, instance)


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
        _on_created(pages.scrape_full_gsc, instance)


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
        _on_created(pages.scrape_full_sophora, instance)


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
        _on_created(tiktok.scrape_full, instance)


@receiver(post_save, sender=SnapchatShow)
def snapchat_show_created(instance: SnapchatShow, created: bool, **kwargs):
    """Start scraper run for newly added Snapchat show account
    (:meth:`okr.scrapers.snapchat_show.scrape_full`).

    Args:
        instance (SnapchatShow): An SnapchatShow instance
        created (bool): Don't start scraper if set to False
    """
    logger.debug("{} saved, created={}", instance, created)
    if created:
        _on_created(snapchat_shows.scrape_full, instance)
