""" Set up Redis connection and rq """

import os

import redis
from rq.queue import Queue

redis_url = os.getenv(
    "REDIS_TLS_URL",
    os.getenv("REDIS_URL", "redis://localhost:6379"),
)
conn = redis.from_url(redis_url)
q = Queue(connection=conn)
