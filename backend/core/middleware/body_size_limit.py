"""
Request Body Size Limit Middleware

Enforces a maximum request body size for API requests to prevent
resource exhaustion attacks (large payload DoS).

The limit is configured via settings.MAX_REQUEST_BODY_SIZE (default 5 MB).
File upload endpoints can bypass this limit via a URL prefix exemption.
"""

import logging
from django.conf import settings
from django.http import JsonResponse

logger = logging.getLogger(__name__)

# Default max body size: 5 MB (nginx is set to 50 MB, so this is an app-level gate)
MAX_BODY_SIZE = getattr(settings, "MAX_REQUEST_BODY_SIZE", 5 * 1024 * 1024)

# These endpoints are exempt from body size limits (file uploads)
EXEMPT_PREFIXES = getattr(settings, "BODY_SIZE_LIMIT_EXEMPT_PREFIXES", [
    "/api/v1/students/upload/",
    "/api/v1/communication/upload/",
    "/api/v1/auth/avatar/",
])


class RequestBodySizeMiddleware:
    """
    Rejects requests with oversized bodies before they reach views.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ("POST", "PUT", "PATCH") and request.path.startswith("/api/"):
            # Check if this path is exempt
            if any(request.path.startswith(prefix) for prefix in EXEMPT_PREFIXES):
                return self.get_response(request)

            content_length = request.META.get("CONTENT_LENGTH")
            if content_length:
                try:
                    if int(content_length) > MAX_BODY_SIZE:
                        logger.warning(
                            "Request body too large: %s bytes on %s %s from %s",
                            content_length,
                            request.method,
                            request.path,
                            request.META.get("REMOTE_ADDR", "unknown"),
                        )
                        return JsonResponse(
                            {
                                "detail": f"Request body too large. Maximum size is {MAX_BODY_SIZE // (1024*1024)} MB.",
                                "status_code": 413,
                            },
                            status=413,
                        )
                except ValueError:
                    pass

        return self.get_response(request)
