import os
from flask_caching import Cache

cache = Cache(
    config={
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_URL": os.getenv(
            "CACHE_REDIS_URL", "redis://localhost:6379"
        ),
        "CACHE_DEFAULT_TIMEOUT": 60 * 60 * 12,
    }
)
