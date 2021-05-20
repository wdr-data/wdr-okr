"""Configure scheduler to call scraper modules."""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR
from sentry_sdk import capture_exception

from okr.scrapers.common.utils import BERLIN
from .todo import bot as bot_todo
from .top_articles import bot as bot_top_articles


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
    """Add and define the scrape schedule for this bot."""

    scheduler.add_listener(sentry_listener, EVENT_JOB_ERROR)

    # SEO suggestions I
    scheduler.add_job(
        bot_todo.run,
        trigger="cron",
        hour="5",
        minute="30",
    )

    # SEO suggestions II
    scheduler.add_job(
        bot_todo.run,
        trigger="cron",
        hour="9",
        minute="0",
    )

    # SEO suggestions III
    scheduler.add_job(
        bot_todo.run,
        trigger="cron",
        hour="13",
        minute="0",
    )

    # SEO top 3
    scheduler.add_job(
        bot_top_articles.run,
        trigger="cron",
        hour="16",
        minute="0",
    )
