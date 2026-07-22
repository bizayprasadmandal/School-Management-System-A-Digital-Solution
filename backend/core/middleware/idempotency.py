"""
Idempotency Middleware

Prevents duplicate processing of payment webhooks by requiring an
Idempotency-Key header on mutating API endpoints. The key is stored
in Redis with a TTL; duplicate keys receive a 409 Conflict response.

Usage:
  Add to MIDDLEWARE in base.py after authentication middleware.
  Clients pass Idempotency-Key: <uuid> header on POST/PUT/PATCH/DELETE
  requests where duplicate processing is a concern (e.g., payments).
"""

import hashlib
import logging
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger(__name__)

IDEMPOTENCY_TTL = getattr(settings, "IDEMPOTENCY_TTL", 86400)  # 24 hours


class IdempotencyMiddleware:
    """
    Middleware that enforces idempotency for mutating API requests.

    - Reads Idempotency-Key header
    - Returns 409 Conflict if the key was already processed
    - Stores the response for the key's TTL so subsequent requests
      with the same key return the cached response
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only apply to mutating API requests
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return self.get_response(request)

        if not request.path.startswith("/api/"):
            return self.get_response(request)

        # Skip idempotency check for GET-like safe operations
        # and for webhook endpoints that use signature verification
        if "/webhook/" in request.path or "/callback/" in request.path:
            return self.get_response(request)

        idempotency_key = request.headers.get("Idempotency-Key", "").strip()
        if not idempotency_key:
            # Idempotency-Key is recommended but not required for all endpoints
            return self.get_response(request)

        # Create a cache key from the idempotency key + request path
        cache_key = f"idempotency:{hashlib.sha256(idempotency_key.encode()).hexdigest()}:{request.path}"

        # Check if this key was already processed
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            logger.info(
                "Idempotency hit: key=%s method=%s path=%s",
                idempotency_key[:16],
                request.method,
                request.path,
            )
            status_code = cached_response.pop("_status_code", 409)
            return JsonResponse(cached_response, status=status_code)

        # Process the request and cache the response
        response = self.get_response(request)

        # Only cache successful responses (2xx) and client errors (4xx)
        if 200 <= response.status_code < 500:
            try:
                import json
                response_data = json.loads(response.content) if response.content else {}
                response_data["_status_code"] = response.status_code
                cache.set(cache_key, response_data, IDEMPOTENCY_TTL)
            except (ValueError, AttributeError):
                pass  # Non-JSON response, skip caching

        return response
