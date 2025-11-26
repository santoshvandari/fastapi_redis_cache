from aiocache import caches
from fastapi.logger import logger


class RedisCacheInit:
    def __init__(self, hostname="localhost", port=6379, namespace="main", timeout=5):
        self.hostname = hostname
        self.port = port
        self.namespace = namespace
        self.timeout = timeout
        self.cache = None

    async def initialize(self):
        try:
            caches.set_config(
                {
                    "default": {
                        "cache": "aiocache.backends.redis.RedisCache",
                        "endpoint": self.hostname,
                        "port": self.port,
                        "namespace": self.namespace,
                        "timeout": self.timeout,
                    }
                }
            )

            self.cache = caches.get("default")

            try:
                await self.cache.get("test")
                logger.info("Redis cache connected successfully.")
            except Exception:
                logger.error("Redis is unreachable — running in fallback mode.")
                self.cache = None

        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            self.cache = None

        return self.cache
