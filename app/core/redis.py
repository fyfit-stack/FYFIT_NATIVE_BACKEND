import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

redis_client = None


async def init_redis():
    """Try to connect to Redis. If unavailable, log a warning and continue."""
    global redis_client
    try:
        from redis.asyncio import Redis
        redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
        await redis_client.ping()  # Actually test the connection
        logger.info("Redis connected successfully.")
        return redis_client
    except Exception as e:
        logger.warning(f"Redis not available, running without cache: {e}")
        redis_client = None
        return None


async def get_redis():
    """Return redis client or None if not available."""
    return redis_client


async def close_redis() -> None:
    if redis_client is not None:
        await redis_client.aclose()

