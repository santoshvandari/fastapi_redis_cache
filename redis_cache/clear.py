from typing import Any, List, Optional

redis_cache: Any = None


def set_redis_instance(redis_instance: Any) -> None:
    global redis_cache
    redis_cache = redis_instance


async def clear_cache(
    key: Optional[str] = None, namespace: Optional[str] = None
) -> None:
    """
    Clear Redis cache:
    - key only  → delete key
    - namespace only → delete all keys in namespace
    - key + namespace → delete one namespaced key
    - none → clear all cache
    """

    if redis_cache is None:
        return
    try:
        if key and namespace:
            namespaced_key = f"{namespace}:{key}"
            await redis_cache.delete(namespaced_key)
            return

        if key:
            await redis_cache.delete(key)
            return

        if namespace:
            pattern = f"{namespace}:*"
            keys: List[str] = await redis_cache.keys(pattern)
            for k in keys:
                await redis_cache.delete(k)
            return
        await redis_cache.clear()
    except Exception:
        pass
