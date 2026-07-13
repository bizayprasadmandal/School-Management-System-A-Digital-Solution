"""
API Versioning Middleware

Supports transparent fallback from /api/v2/ to /api/v1/ endpoints so that
v1 views can serve both versions until v2 views are implemented.
Clients indicate version via URL prefix (/api/v1/... or /api/v2/...) or
via the X-API-Version header.

Usage:
  1. Add to MIDDLEWARE in base.py after TenantMiddleware.
  2. Implement v2 views in a services/*/urls_v2.py with namespace *_v2.
  3. Register v2 urls in core/urls.py with path("api/v2/...", ...).
"""

import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class APIVersioningMiddleware:
    """
    Rewrites /api/v2/<path> to /api/v1/<path> transparently so that
    existing v1 views can serve v2 requests until dedicated v2 views
    are created.

    Also reads X-API-Version header and attaches version info to
    request.api_version for views that want to conditionally respond.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Detect version from URL prefix
        path = request.path_info

        # Default to v1
        request.api_version = "1.0"

        if path.startswith("/api/v2/"):
            request.api_version = "2.0"
            # Rewrite path to v1 for fallback routing
            rewritten = path.replace("/api/v2/", "/api/v1/", 1)
            request.path_info = rewritten
            logger.debug(
                "API versioning: rewrote %s → %s", path, rewritten
            )

        elif path.startswith("/api/v1/"):
            request.api_version = "1.0"

        # Header override
        header_version = request.headers.get("X-API-Version", "")
        if header_version:
            request.api_version = header_version

        response = self.get_response(request)

        # Restore original path for response reference
        request.path_info = path

        # Add API version to response headers for all API calls
        if path.startswith("/api/"):
            response["X-API-Version"] = request.api_version

        return response
