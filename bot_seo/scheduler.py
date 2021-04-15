"""Configure scheduler to call scraper modules."""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR
from sentry_sdk import capture_exception

from okr.scrapers.common.utils import BERLIN
from .todo import bot as bot_todo


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

    # SEO suggestions
    scheduler.add_job(
        bot_todo.run(),
        trigger="cron",
        hour="13",
        minute="0",
    )
