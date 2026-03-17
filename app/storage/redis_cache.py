"""In-memory cache (Redis-compatible interface) for caching and rate limiting."""

import time
from typing import Optional, Dict, Any

from app.core.logging import logger

# In-memory cache (can be replaced with Redis)
_cache: Dict[str, Dict[str, Any]] = {}


async def init_redis() -> None:
    """Initialize cache."""
    logger.info("Cache initialized (in-memory store).")


async def get_cached(key: str) -> Optional[str]:
    """Get a cached value by key."""
    if key in _cache:
        entry = _cache[key]
        if entry.get("ttl") and time.time() > entry["ttl"]:
            del _cache[key]
            return None
        return entry.get("value")
    return None


async def set_cached(key: str, value: str, ttl_seconds: int = 86400) -> None:
    """Set a cached value with TTL."""
    _cache[key] = {
        "value": value,
        "ttl": time.time() + ttl_seconds,
    }


async def delete_cached(key: str) -> None:
    """Delete a cached value."""
    _cache.pop(key, None)


async def clear_cache() -> None:
    """Clear all cached values."""
    _cache.clear()
    logger.info("Cache cleared.")
