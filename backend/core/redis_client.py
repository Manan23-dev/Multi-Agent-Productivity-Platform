"""
Redis client configuration for FlowAgent
"""

import redis.asyncio as redis
from typing import Optional

from backend.core.config import get_settings

settings = get_settings()

# Global Redis client
redis_client: Optional[redis.Redis] = None

async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    
    redis_client = redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
        health_check_interval=30
    )
    
    # Test connection
    await redis_client.ping()

async def get_redis() -> redis.Redis:
    """Get Redis client"""
    if redis_client is None:
        await init_redis()
    return redis_client

async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
