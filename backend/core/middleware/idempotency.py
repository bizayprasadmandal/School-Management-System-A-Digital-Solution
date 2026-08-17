"""
Idempotency Middleware

Prevents duplicate processing of mutating API requests (including payment
webhooks) by requiring an Idempotency-Key header on POST/PUT/PATCH/DELETE
endpoints. The key is claimed ATOMICALLY in the cache (SETNX semantics via
cache.add) with a TTL; duplicate keys receive the previously stored response,
or a 409 Conflict while the first request is still in flight.

Webhook endpoints (Stripe /fees/stripe/webhook/, Khalti/eSewa
/fees/nepali/verify/) are NOT bypassed. Their primary replay protection is the
gateway signature/token verification inside the views themselves; the
Idempotency-Key dedup applies on top whenever a caller supplies the header.
Requests without an Idempotency-Key header pass through unchanged.

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

# Sentinel value stored while the first request is in flight, so a concurrent
# duplicate is rejected even before the real response is available to cache.
_PROCESSING = {"_processing": True}


class IdempotencyMiddleware:
    """
    Middleware that enforces idempotency for mutating API requests.

    - Reads Idempotency-Key header
    - Atomically claims the key with cache.add() (SETNX) — only the first
      caller executes the request; concurrent duplicates are rejected
    - Returns 409 Conflict if the key was already claimed and no response
      is stored yet
    - Returns the cached response for the key's TTL on later duplicates
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only apply to mutating API requests
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return self.get_response(request)

        if not request.path.startswith("/api/"):
            return self.get_response(request)

        idempotency_key = request.headers.get("Idempotency-Key", "").strip()
        if not idempotency_key:
            # Idempotency-Key is recommended but not required for all endpoints
            return self.get_response(request)

        # Create a cache key from the idempotency key + request path + caller
        # credential. Binding the key to the Authorization header (or session
        # user) prevents one client from replaying/stealing another's cached
        # response when they happen to use the same key value on the same path.
        caller = request.META.get("HTTP_AUTHORIZATION", "")
        if not caller and getattr(request, "user", None) is not None:
            caller = getattr(request.user, "id", "") or ""
        cache_key = f"idempotency:{hashlib.sha256((idempotency_key + caller).encode()).hexdigest()}:{request.path}"

        # Atomically claim the key (Redis SETNX semantics via cache.add).
        # Only the caller that wins the claim may execute the action; this
        # closes the check-then-set TOCTOU race between two concurrent
        # requests carrying the same key.
        if cache.add(cache_key, _PROCESSING, IDEMPOTENCY_TTL):
            response = self.get_response(request)

            # Only cache successful responses (2xx) and client errors (4xx)
            if 200 <= response.status_code < 500:
                try:
                    import json

                    response_data = json.loads(response.content) if response.content else {}
                    response_data["_status_code"] = response.status_code
                    cache.set(cache_key, response_data, IDEMPOTENCY_TTL)
                except (ValueError, AttributeError):
                    # Non-JSON response, skip caching — release the claim so a
                    # legitimate retry is not blocked for the whole TTL.
                    cache.delete(cache_key)
            else:
                # Server errors are not cached — release the claim for retries.
                cache.delete(cache_key)
            return response

        # The key was already claimed: return the stored response if the first
        # request finished, otherwise reject the in-flight duplicate.
        cached_response = cache.get(cache_key)
        if cached_response is not None and cached_response != _PROCESSING:
            logger.info(
                "Idempotency hit: key=%s method=%s path=%s",
                idempotency_key[:16],
                request.method,
                request.path,
            )
            status_code = cached_response.pop("_status_code", 409)
            return JsonResponse(cached_response, status=status_code)

        logger.info(
            "Idempotency duplicate in flight: key=%s method=%s path=%s",
            idempotency_key[:16],
            request.method,
            request.path,
        )
        return JsonResponse(
            {"detail": "Duplicate request: a request with this Idempotency-Key is already being processed."},
            status=409,
        )
