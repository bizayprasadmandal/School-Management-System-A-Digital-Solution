"""Request/response logging middleware."""
import time, logging
logger = logging.getLogger("sms.requests")

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        if request.path.startswith("/api/"):
            user = getattr(request, "user", None)
            uid = str(user.id) if user and user.is_authenticated else "anon"
            logger.info("%s %s %d %.0fms user=%s",
                request.method, request.path, response.status_code,
                (time.monotonic()-start)*1000, uid)
        return response
