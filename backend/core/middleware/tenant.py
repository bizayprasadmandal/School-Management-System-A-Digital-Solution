"""
Tenant Middleware — Resolves school from subdomain and attaches to request.
Supports both subdomain-based and header-based multi-tenancy.

Also provides ``set_tenant_context`` for DRF authentication time: the
middleware runs before DRF authentication, so on JWT requests its
``request.school`` snapshot is built from an unauthenticated user and the
header override is skipped (the super-admin switcher guard needs the user).
``JWTAuthentication.authenticate`` runs after that and injects the context,
so any view may rely on ``request.school``:

- header override: super admins may select any tenant; everyone else's
  header is only honored if it confirms their own school (tamper-proof),
- fallback: the authenticated user's own school FK.
"""

import logging

from django.core.cache import cache
from django.db.models.signals import pre_save
from django.dispatch import receiver
from services.auth.models import User

logger = logging.getLogger(__name__)


def get_school_cached(pk=None, subdomain=None):
    """Resolve an active School by pk or subdomain with a short cache.

    Shared by ``TenantMiddleware`` and ``set_tenant_context``. Malformed
    (non-UUID) pk values return None — never raise — so a bad header cannot
    bubble up as a 500 from middleware or authentication.
    """
    from django.core.exceptions import ValidationError
    from services.auth.models import School

    if pk:
        cache_key = f"school_pk_{pk}"
        cached_pk = cache.get(cache_key)
        if cached_pk is not None:
            try:
                return School.objects.get(pk=cached_pk, is_active=True)
            except (School.DoesNotExist, ValidationError, ValueError, TypeError):
                return None
        try:
            school = School.objects.get(pk=pk, is_active=True)
            cache.set(cache_key, school.pk, timeout=300)
            return school
        except (School.DoesNotExist, ValidationError, ValueError, TypeError):
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


def _resolve_tenant_for_user(request, user):
    """Resolve the tenant for an *authenticated* user (DRF-time).

    Header override rules: super admins may select any school; other roles
    may only confirm their own school via the header (a foreign header is
    ignored in favor of their own school FK).
    """
    from services.auth.models import School, UserRole  # noqa: F401 (School re-exported)

    school_id = request.headers.get("X-School-ID")
    if school_id:
        school = get_school_cached(pk=school_id)
        is_super = getattr(user, "role", None) == UserRole.SUPER_ADMIN
        if not is_super:
            user_school = getattr(user, "school", None)
            if user_school is not None and (school is None or school.pk != user_school.pk):
                return user_school
        if school is not None:
            return school

    return getattr(user, "school", None)


def set_tenant_context(request, user):
    """Populate ``request.school`` for an authenticated ``user``.

    Called from ``JWTAuthentication.authenticate`` (after the middleware
    pass) so JWT requests get the same tenant resolution rules. Never raises.

    When the resolved tenant differs from the user's own school (the super
    admin switcher flow), the user instance gets an *in-memory* tenant
    override (``school``/``school_id`` point at the selected school) so the
    many viewsets that scope via ``request.user.school`` transparently
    operate on the selected tenant. A ``pre_save`` guard below ensures the
    override can never be persisted to the user row.
    """
    try:
        school = _resolve_tenant_for_user(request, user)
        request.school = school
        own_id = getattr(user, "school_id", None)
        tenant_id = getattr(school, "pk", None)
        if tenant_id and tenant_id != own_id:
            if not getattr(user, "_tenant_school_overridden", False):
                user._original_school_id = own_id
            user._tenant_school_overridden = True
            user.school_id = tenant_id
            user.school = school
    except Exception:
        logger.exception("set_tenant_context failed")
        request.school = getattr(user, "school", None)


@receiver(pre_save, sender=User)
def _prevent_tenant_override_persistence(sender, instance, **kwargs):
    """Never write a switched tenant onto the user's own row.

    If a user with an active in-memory tenant override (super admin school
    switcher) is saved for any reason, restore the original school FK so the
    override stays strictly request-scoped.
    """
    if getattr(instance, "_tenant_school_overridden", False):
        instance.school_id = getattr(instance, "_original_school_id", None)


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

    @staticmethod
    def _resolve_user(request):
        """
        Resolve the authenticated user at middleware time.

        Django middleware runs before DRF's view-level authentication, so for
        JWT clients `request.user` is still AnonymousUser here (only session
        auth is populated by AuthenticationMiddleware). The email-verification
        middleware uses the same pattern; this one additionally honors the test
        client's forced user.
        """
        from django.contrib.auth.models import AnonymousUser

        forced = getattr(request, "_force_auth_user", None)
        if forced is not None:
            return forced
        if getattr(request, "user", None) is not None and request.user.is_authenticated:
            return request.user

        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if auth.startswith("Bearer "):
            try:
                from rest_framework_simplejwt.tokens import AccessToken
                from services.auth.models import User

                token = AccessToken(auth[7:])
                user = User.objects.filter(id=token["user_id"], is_active=True).first()
                return user or AnonymousUser()
            except Exception:
                return AnonymousUser()
        return AnonymousUser()

    def _resolve_school(self, request):
        from services.auth.models import UserRole

        # 1. Header override (API clients / mobile)
        school_id = request.headers.get("X-School-ID")
        if school_id:
            header_school = get_school_cached(pk=school_id)
            # Authenticated users must never be redirected to another tenant
            # via the header. The header may only confirm the user's own
            # school; only super admins may use it to select a school. When
            # the header disagrees, fall back to the user's own school.
            #
            # The user is resolved from the JWT here (not just session auth):
            # previously the guard only worked for session-authenticated
            # requests, so a JWT client of any role could override the tenant
            # via the header.
            user = self._resolve_user(request)
            if user.is_authenticated:
                is_super = getattr(user, "role", None) == UserRole.SUPER_ADMIN
                if not is_super:
                    user_school = getattr(user, "school", None)
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
            school = get_school_cached(subdomain=subdomain)
            if school:
                return school

        # 3. Fall back to authenticated user's school
        if hasattr(request, "user") and request.user.is_authenticated:
            return request.user.school

        return None
