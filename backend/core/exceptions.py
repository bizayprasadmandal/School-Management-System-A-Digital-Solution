import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # django-axes records the lockout flag on the DRF request object
        # (SimpleJWT passes `self.context["request"]` into authenticate()), but
        # the AxesMiddleware inspects the raw Django request and never sees it.
        # Surface a locked-out failed login as 403 here instead of a plain 401.
        if response.status_code == status.HTTP_401_UNAUTHORIZED and getattr(
            context.get("request"), "axes_locked_out", False
        ):
            try:
                from axes.helpers import get_lockout_message

                detail = get_lockout_message()
            except Exception:  # pragma: no cover - axes always installed
                detail = "Too many failed login attempts. You are temporarily " "locked out. Try again in 30 minutes."
            return Response(
                {"detail": detail, "status_code": status.HTTP_403_FORBIDDEN},
                status=status.HTTP_403_FORBIDDEN,
            )

        response.data["status_code"] = response.status_code
        # Capture 5xx errors to Sentry
        if response.status_code >= 500:
            _capture_to_sentry(exc, context)
        return response

    logger.exception("Unhandled exception in view %s", context.get("view"))
    _capture_to_sentry(exc, context)
    return Response(
        {"detail": "An unexpected server error occurred.", "status_code": 500},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _capture_to_sentry(exc, context):
    """Send exception details to Sentry if configured."""
    try:
        import sentry_sdk

        sentry_sdk.capture_exception(exc)
    except ImportError:
        pass  # sentry-sdk not installed — Sentry not configured
    except Exception:
        pass  # Sentry is optional; don't let failures cascade
