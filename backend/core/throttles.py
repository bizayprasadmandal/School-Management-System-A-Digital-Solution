"""
Custom throttle classes for sensitive auth endpoints.

These provide tighter rate limits than the global defaults (100/hr anon, 1000/hr user)
to protect login, password reset, and token refresh endpoints from abuse.

Works alongside django-axes:
  - Axes: per-account lockout after 5 failed attempts, 30 min cooldown
  - Throttling: per-IP rate limit BEFORE the request hits the view logic
"""

from rest_framework.throttling import AnonRateThrottle


class AuthLoginAnonThrottle(AnonRateThrottle):
    """Limit anonymous login attempts per IP.

    Rate comes from ``DEFAULT_THROTTLE_RATES["auth_login"]`` (default
    10/minute; raised to 10000/minute in e2e environments via
    ``AUTH_LOGIN_THROTTLE_RATE`` so suites firing many sequential logins from
    one IP aren't throttled mid-run). No class-level ``rate`` here on purpose:
    DRF skips ``get_rate()`` (and therefore ``THROTTLE_RATES``) whenever the
    class attribute is set.
    """

    scope = "auth_login"


class AuthPasswordResetThrottle(AnonRateThrottle):
    """Limit password reset requests to 5 per hour per IP."""

    rate = "5/hour"
    scope = "auth_password_reset"


class AuthPasswordResetConfirmThrottle(AnonRateThrottle):
    """Limit password reset confirmation to 10 per hour per IP."""

    rate = "10/hour"
    scope = "auth_password_reset_confirm"


class AuthVerify2FALoginThrottle(AnonRateThrottle):
    """
    Limit 2FA verification (TOTP + backup code) attempts to 5 per minute per IP.
    This complements the per-account backup-code lockout (3 failed before 30min ban)
    by adding a per-IP rate limit before the request reaches the business logic.
    """

    rate = "5/minute"
    scope = "auth_verify_2fa_login"
