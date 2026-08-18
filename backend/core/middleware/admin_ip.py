"""
Admin IP Allowlist Middleware — restricts /admin/ to whitelisted IPs.

When ADMIN_ALLOWED_IPS contains at least one entry, any request whose path
starts with /admin/ and whose client IP is NOT in the list is rejected with
403 Forbidden. If ADMIN_ALLOWED_IPS is empty (the default), no restriction
is applied.

The client IP is resolved from X-Forwarded-For (first entry) when present,
falling back to REMOTE_ADDR. This matches the standard pattern for
reverse-proxy deployments (nginx → Django).
"""

import logging

from django.conf import settings
from django.http import HttpResponseForbidden

logger = logging.getLogger(__name__)


class AdminIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed = getattr(settings, "ADMIN_ALLOWED_IPS", [])
        if allowed and request.path.startswith("/admin/"):
            ip = self._get_client_ip(request)
            if ip not in allowed:
                logger.warning(
                    "Admin access denied from IP %s (not in ADMIN_ALLOWED_IPS)",
                    ip,
                )
                return HttpResponseForbidden("Access denied")
        return self.get_response(request)

    @staticmethod
    def _get_client_ip(request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")
