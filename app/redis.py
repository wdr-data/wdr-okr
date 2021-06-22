""" Set up Redis connection and rq """

import os

import redis
from rq.queue import Queue

REDIS_URL = os.getenv(
    "REDIS_TLS_URL",
    os.getenv("REDIS_URL", "redis://localhost:6379"),
)
conn = redis.from_url(
    REDIS_URL,
    ssl_cert_reqs=None,
)
q = Queue(connection=conn)
