"""
Request Logging Middleware
Logs all API requests and responses for monitoring and debugging
"""

import time
import logging
import json
from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("pneumovision.api")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all HTTP requests and responses.
    Tracks request duration, status codes, and potential errors.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()
        
        # Generate request ID
        request_id = f"{time.time():.0f}-{id(request)}"
        
        # Log request
        await self._log_request(request, request_id)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            self._log_response(request, response, duration, request_id)
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            
            return response
            
        except Exception as e:
            # Log error
            duration = time.time() - start_time
            logger.error(
                f"Request {request_id} failed after {duration:.3f}s: {str(e)}",
                exc_info=True,
            )
            raise
    
    async def _log_request(self, request: Request, request_id: str):
        """Log incoming request details."""
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
                # Remove sensitive fields
                if isinstance(body, dict):
                    body = {
                        k: ("***" if k in ["password", "token", "secret"] else v)
                        for k, v in body.items()
                    }
            except (json.JSONDecodeError, AttributeError):
                body = "(non-JSON body)"
        
        logger.info(
            f"Request [{request_id}] {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
            f"{f' body={json.dumps(body)}' if body else ''}"
        )
    
    def _log_response(
        self,
        request: Request,
        response,
        duration: float,
        request_id: str,
    ):
        """Log response details."""
        log_level = (
            logger.warning if response.status_code >= 400
            else logger.error if response.status_code >= 500
            else logger.info
        )
        
        log_level(
            f"Response [{request_id}] {request.method} {request.url.path} "
            f"-> {response.status_code} ({duration:.3f}s)"
        )

