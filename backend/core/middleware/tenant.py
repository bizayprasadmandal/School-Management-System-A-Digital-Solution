"""
Tenant Middleware — Resolves school from subdomain and attaches to request.
Supports both subdomain-based and header-based multi-tenancy.
"""

import logging
from django.http import JsonResponse
from django.core.cache import cache

logger = logging.getLogger(__name__)


class TenantMiddleware:
    """
    Resolves the current school (tenant) from:
      1. Subdomain: school1.edusphere.school → school code "school1"
      2. X-School-ID header (for mobile/API clients)
      3. Authenticated user's school FK (fallback)
    """

    BYPASS_PATHS = ["/admin/", "/api/schema/", "/api/docs/", "/health/", "/metrics"]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip non-tenant paths
        if any(request.path.startswith(p) for p in self.BYPASS_PATHS):
            return self.get_response(request)

        school = self._resolve_school(request)
        request.school = school
        return self.get_response(request)

    def _resolve_school(self, request):
        from services.auth.models import School

        # 1. Header override (API clients / mobile)
        school_id = request.headers.get("X-School-ID")
        if school_id:
            return self._get_school_cached(pk=school_id)

        # 2. Subdomain routing
        host = request.get_host().split(":")[0]  # strip port
        parts = host.split(".")
        if len(parts) >= 3:
            subdomain = parts[0]
            school = self._get_school_cached(subdomain=subdomain)
            if school:
                return school

        # 3. Fall back to authenticated user's school
        if hasattr(request, "user") and request.user.is_authenticated:
            return request.user.school

        return None

    def _get_school_cached(self, pk=None, subdomain=None):
        from services.auth.models import School

        if pk:
            cache_key = f"school_pk_{pk}"
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            try:
                school = School.objects.get(pk=pk, is_active=True)
                cache.set(cache_key, school, timeout=300)
                return school
            except School.DoesNotExist:
                return None

        if subdomain:
            cache_key = f"school_subdomain_{subdomain}"
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            try:
                school = School.objects.get(subdomain=subdomain, is_active=True)
                cache.set(cache_key, school, timeout=300)
                return school
            except School.DoesNotExist:
                return None

        return None
