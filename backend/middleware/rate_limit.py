"""
Rate Limiting Middleware
Prevents API abuse by limiting request frequency
"""

import os
import time
import logging
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using token bucket algorithm.
    
    Limits requests per client IP within a time window.
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.max_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.window_size = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
        self.requests: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, 0.0))
        self.cleanup_interval = 300  # Cleanup every 5 minutes
        self.last_cleanup = time.time()
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        
        # Skip rate limiting for certain paths
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        current_time = time.time()
        count, window_start = self.requests[client_ip]
        
        # Reset if window has expired
        if current_time - window_start > self.window_size:
            count = 0
            window_start = current_time
        
        # Check if limit exceeded
        if count >= self.max_requests:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": int(self.window_size - (current_time - window_start)),
                },
                headers={
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(window_start + self.window_size)),
                    "Retry-After": str(int(self.window_size - (current_time - window_start))),
                },
            )
        
        # Update counter
        self.requests[client_ip] = (count + 1, window_start)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(self.max_requests - count - 1)
        response.headers["X-RateLimit-Reset"] = str(int(window_start + self.window_size))
        
        # Periodic cleanup of old entries
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup(current_time)
            self.last_cleanup = current_time
        
        return response
    
    def _cleanup(self, current_time: float):
        """Remove expired entries from rate limit tracking."""
        expired = [
            ip for ip, (_, start) in self.requests.items()
            if current_time - start > self.window_size * 2
        ]
        for ip in expired:
            del self.requests[ip]
        if expired:
            logger.debug(f"Cleaned up {len(expired)} expired rate limit entries")

