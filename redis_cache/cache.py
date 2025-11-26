import json
from functools import wraps
from typing import Optional

from fastapi.logger import logger

redis_cache = None


def set_redis_instance(redis_instance):
    global redis_cache
    redis_cache = redis_instance


def cache(expire: int = 60, key: Optional[str] = None, namespace: Optional[str] = None):
    """
    Decorator to cache endpoint responses in Redis.
    Args:
        expire: cache TTL in seconds
        key: optional custom key
        namespace: optional namespace prefix
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # If Redis not initialized → run without cache
            if redis_cache is None:
                return await func(*args, **kwargs)

            try:
                args_key = json.dumps(args, default=str)
                kwargs_key = json.dumps(kwargs, default=str)
                final_key = key or f"{func.__name__}:{args_key}:{kwargs_key}"
            except Exception:
                final_key = key or func.__name__

            if namespace:
                final_key = f"{namespace}:{final_key}"

            try:
                cached_value = await redis_cache.get(final_key)
                if cached_value:
                    return json.loads(cached_value)
            except Exception:
                logger.error("Redis GET failed")

            response = await func(*args, **kwargs)

            try:
                await redis_cache.set(final_key, json.dumps(response), ttl=expire)
            except Exception:
                logger.error("Redis SET failed")

            return response

        return wrapper

    return decorator
