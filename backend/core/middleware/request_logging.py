"""
Request/response logging middleware with request ID tracking.
Attaches a unique request_id to each incoming request for traceability
across middleware, views, and downstream Celery tasks.
"""
import time
import uuid
import logging

logger = logging.getLogger("sms.requests")


class RequestLoggingMiddleware:
    """
    Logs all API requests with method, path, status, duration, user, and a
    unique request_id that can be passed to background tasks for tracing.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = str(uuid.uuid4())[:8]
        start = time.monotonic()
        response = self.get_response(request)
        if request.path.startswith("/api/"):
            user = getattr(request, "user", None)
            uid = str(user.id) if user and user.is_authenticated else "anon"
            logger.info(
                "request_id=%s method=%s path=%s status=%d duration=%.0fms user=%s",
                request.request_id,
                request.method,
                request.path,
                response.status_code,
                (time.monotonic() - start) * 1000,
                uid,
            )
        return response
