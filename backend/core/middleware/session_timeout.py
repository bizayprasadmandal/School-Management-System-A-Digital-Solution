"""
Session Timeout Middleware
Logs out users whose JWT access token has expired by checking the `exp`
claim directly from the `Authorization: Bearer ...` header.

This works alongside the DRF JWT authentication at the middleware level,
providing an early 401 response before the request reaches the view layer.
It parses the JWT without verifying the signature (signature verification
happens in DRF auth) — we only check the `exp` timestamp for expiry.

Configuration (in settings):
  SESSION_TIMEOUT_ENABLED = True   (default: True)
  JWT_ACCESS_TOKEN_LIFETIME is read from SIMPLE_JWT settings
"""

import json
import base64
import time
import logging
from django.conf import settings
from django.http import JsonResponse

logger = logging.getLogger(__name__)

SESSION_TIMEOUT_ENABLED = getattr(settings, "SESSION_TIMEOUT_ENABLED", True)


def _decode_jwt_payload(token: str) -> dict | None:
    """Decode the payload portion of a JWT without verifying the signature.

    Raises no exceptions — returns None on any parse failure.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        # Pad payload for base64url decoding
        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError, Exception):
        return None


class SessionTimeoutMiddleware:
    """Check JWT `exp` claim on every authenticated request.

    Skips health-check endpoints and requests without a Bearer token.
    Returns 401 if the token's `exp` (epoch seconds) is in the past.
    """

    EXEMPT_PATHS = {"/health/", "/health/live/", "/health/ready/", "/metrics"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not SESSION_TIMEOUT_ENABLED:
            return self.get_response(request)

        path = request.path_info
        if any(path.startswith(exempt) for exempt in self.EXEMPT_PATHS):
            return self.get_response(request)

        # Check for a Bearer token
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return self.get_response(request)

        token = auth_header[7:]  # strip "Bearer "
        payload = _decode_jwt_payload(token)
        if payload is None:
            return self.get_response(request)

        exp = payload.get("exp")
        if exp is None:
            return self.get_response(request)

        # exp is in epoch seconds; add a 30s grace window for clock skew
        if time.time() > exp + 30:
            logger.info(
                "JWT token expired for user (exp=%d, now=%d)",
                exp,
                int(time.time()),
            )
            return JsonResponse(
                {
                    "detail": "Session expired. Please log in again.",
                    "code": "token_expired",
                },
                status=401,
            )

        return self.get_response(request)
