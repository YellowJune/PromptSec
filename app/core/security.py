"""Authentication, authorization, and rate limiting utilities."""

import hashlib
import time
from typing import Dict, Optional

from fastapi import Request, HTTPException, status
from app.core.logging import logger


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list[float]] = {}

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        if client_id not in self._requests:
            self._requests[client_id] = []

        # Remove expired entries
        self._requests[client_id] = [
            ts for ts in self._requests[client_id]
            if now - ts < self.window_seconds
        ]

        if len(self._requests[client_id]) >= self.max_requests:
            return False

        self._requests[client_id].append(now)
        return True


rate_limiter = RateLimiter()


async def check_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.is_allowed(client_ip):
        logger.warning(f"Rate limit exceeded for {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )


def hash_prompt(prompt: str) -> str:
    """Generate a SHA256 hash of a prompt for caching purposes."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()
