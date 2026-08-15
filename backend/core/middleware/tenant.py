"""
Tenant Middleware — Resolves school from subdomain and attaches to request.
Supports both subdomain-based and header-based multi-tenancy.
"""

import logging

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
        from services.auth.models import UserRole

        # 1. Header override (API clients / mobile)
        school_id = request.headers.get("X-School-ID")
        if school_id:
            header_school = self._get_school_cached(pk=school_id)
            # Authenticated users must never be redirected to another tenant
            # via the header. The header may only confirm the user's own
            # school; only super admins may use it to select a school. When
            # the header disagrees, fall back to the user's own school.
            if hasattr(request, "user") and request.user.is_authenticated:
                is_super = getattr(request.user, "role", None) == UserRole.SUPER_ADMIN
                if not is_super:
                    user_school = getattr(request.user, "school", None)
                    if user_school is not None:
                        if header_school is None or header_school.pk != user_school.pk:
                            return user_school
            if header_school is not None:
                return header_school

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
            cached_pk = cache.get(cache_key)
            if cached_pk is not None:
                try:
                    return School.objects.get(pk=cached_pk, is_active=True)
                except School.DoesNotExist:
                    return None
            try:
                school = School.objects.get(pk=pk, is_active=True)
                cache.set(cache_key, school.pk, timeout=300)
                return school
            except School.DoesNotExist:
                return None

        if subdomain:
            cache_key = f"school_subdomain_{subdomain}"
            cached_pk = cache.get(cache_key)
            if cached_pk is not None:
                try:
                    return School.objects.get(pk=cached_pk, is_active=True)
                except School.DoesNotExist:
                    return None
            try:
                school = School.objects.get(subdomain=subdomain, is_active=True)
                cache.set(cache_key, school.pk, timeout=300)
                return school
            except School.DoesNotExist:
                return None

        return None
