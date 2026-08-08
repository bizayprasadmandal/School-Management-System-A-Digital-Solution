"""
Email Verification Middleware

Blocks API requests from authenticated users whose email_verified is False,
except for a whitelist of auth/verification endpoints that are needed to
complete the verification flow.

The middleware is opt-in: if the EMAIL_VERIFICATION_ENFORCED setting is not
True, all requests pass through unchanged.
"""

import json
import logging

from django.conf import settings
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class ApiJsonResponse(JsonResponse):
    """JsonResponse with a DRF-style `.data` attribute for API consumers/tests."""

    @property
    def data(self):
        return json.loads(self.content)


# Endpoints that are always allowed, even when email is not verified.
# These include the verification flow itself, auth endpoints needed to
# log in, and public endpoints.
BYPASS_PATHS = [
    "/health/",
    "/admin/",
    "/api/schema/",
    "/api/docs/",
    "/api/redoc/",
    "/metrics",
    "/graphql/",
]

# Auth endpoints allowed before email is verified.
# The user must be able to log in, check their verification status,
# send verification emails, verify tokens, change password, and reset password.
ALLOWED_AUTH_PATHS = [
    "/api/v1/auth/login/",
    "/api/v1/auth/logout/",
    "/api/v1/auth/token/refresh/",
    "/api/v1/auth/me/",
    "/api/v1/auth/profile/",
    "/api/v1/auth/change-password/",
    "/api/v1/auth/send-verification/",
    "/api/v1/auth/verify-email/",
    "/api/v1/auth/password-reset/",
    "/api/v1/auth/password-reset/confirm/",
    "/api/v1/auth/setup-2fa/",
    "/api/v1/auth/verify-2fa/",
    "/api/v1/auth/disable-2fa/",
    "/api/v1/auth/verify-2fa-login/",
]


class EmailVerificationMiddleware:
    """
    Enforces email verification for authenticated users.

    If EMAIL_VERIFICATION_ENFORCED is True in settings, any authenticated
    user with email_verified=False will receive a 403 response when
    accessing endpoints outside the BYPASS and ALLOWED_AUTH lists.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def _resolve_user(request):
        """
        Django middleware runs before DRF's view-level authentication, so
        `request.user` is still AnonymousUser for JWT clients and for test
        clients using force_authenticate(). Resolve the actual user here:
        first from the test client's forced user, then from the Bearer JWT.
        """
        from django.contrib.auth.models import AnonymousUser

        # Test clients (APIClient.force_authenticate)
        forced = getattr(request, "_force_auth_user", None)
        if forced is not None:
            return forced

        # Production: SimpleJWT access token
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if auth.startswith("Bearer "):
            try:
                from rest_framework_simplejwt.tokens import AccessToken

                token = AccessToken(auth[7:])
                from services.auth.models import User

                user = User.objects.filter(id=token["user_id"], is_active=True).first()
                return user or AnonymousUser()
            except Exception:
                return AnonymousUser()

        return AnonymousUser()

    def __call__(self, request):
        # Quick skip: enforcement not enabled
        if not getattr(settings, "EMAIL_VERIFICATION_ENFORCED", False):
            return self.get_response(request)

        path = request.path_info

        # Always allow bypass paths
        if any(path.startswith(p) for p in BYPASS_PATHS):
            return self.get_response(request)

        # Always allow allowed auth paths
        if any(path.startswith(p) for p in ALLOWED_AUTH_PATHS):
            return self.get_response(request)

        # Check if the user is authenticated but email is not verified
        user = getattr(request, "user", None)
        if not (user and user.is_authenticated):
            user = self._resolve_user(request)
        if user and user.is_authenticated and not user.email_verified:
            logger.info(
                "Blocked request from unverified user %s to %s",
                user.email,
                path,
            )
            return ApiJsonResponse(
                {
                    "detail": "Email not verified. "
                    "Please verify your email before accessing this resource. "
                    "Call POST /api/v1/auth/send-verification/ to receive a verification link.",
                    "code": "email_not_verified",
                    "email_verified": False,
                },
                status=403,
            )

        return self.get_response(request)
