from os import getenv

import redis


class Redis:
    def __init__(self):
        self.client = redis.Redis(
            host=getenv("REDIS_HOST"),
            port=getenv("REDIS_PORT"),
            password=getenv("REDIS_PASSWORD"),
        )
