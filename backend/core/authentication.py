"""Authentication classes with tenant-context injection.

``JWTAuthenticationWithTenant`` wraps simplejwt's ``JWTAuthentication``:
after the user is resolved, ``set_tenant_context`` populates
``request.school`` using the same header rules as ``TenantMiddleware``
(super admins may select a tenant via ``X-School-ID``; other roles are
pinned to their own school). This is the piece that makes the super-admin
school switcher work for JWT clients, whose ``request.user`` is anonymous
during the middleware pass.
"""

from core.middleware.tenant import set_tenant_context
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTAuthenticationWithTenant(JWTAuthentication):
    def authenticate(self, request):
        response = super().authenticate(request)
        if response is not None:
            user, token = response
            set_tenant_context(request, user)
        return response
