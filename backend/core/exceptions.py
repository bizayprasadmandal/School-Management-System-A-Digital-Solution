import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
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
