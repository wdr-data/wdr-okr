""" Set up Redis connection and rq """

import os

import redis
from rq.queue import Queue

REDIS_URL = os.getenv(
    "REDIS_TLS_URL",
    os.getenv("REDIS_URL", "redis://localhost:6379"),
)

kwargs = {}

if REDIS_URL.startswith("rediss"):
    kwargs["ssl_cert_reqs"] = None

conn = redis.from_url(
    REDIS_URL,
    **kwargs,
)
q = Queue(connection=conn)
