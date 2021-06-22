""" Main entrypoint for the worker process """


import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

import django

django.setup()

from django.conf import settings
from rq import SimpleWorker, Queue, Connection

from app.redis import conn

from okr.scrapers import scheduler as scheduler_okr
from bot_seo import scheduler as scheduler_bot_seo

scheduler_modules = [
    scheduler_okr,
    scheduler_bot_seo,
]

# Set up schedulers
for scheduler_module in scheduler_modules:
    scheduler_module.setup()
    if not settings.DEBUG:
        scheduler_module.add_jobs()

# Start rq connection
listen = ["high", "default", "low"]

if __name__ == "__main__":
    with Connection(conn):
        worker = SimpleWorker(map(Queue, listen))
        worker.work()  # Blocking

    # Cleanup
    for scheduler_module in scheduler_modules:
        scheduler_module.scheduler.shutdown()
        if getattr(scheduler_module, "executors", None):
            for executor in scheduler_module.executors.values():
                executor.shutdown()
