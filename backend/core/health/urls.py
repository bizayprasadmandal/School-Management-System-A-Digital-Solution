"""
Health Check — Kubernetes liveness, readiness, and startup probes
"""

import time

from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.urls import path


def liveness(request):
    """
    Liveness probe — Is the process alive?
    Returns 200 if Django is running. No DB/cache check (avoid cascading failures).
    """
    return JsonResponse({"status": "alive", "service": "sms-backend"})


def readiness(request):
    """
    Readiness probe — Is the service ready to handle traffic?
    Checks DB, Redis, and Celery worker connectivity.
    Returns 503 if any dependency is down.
    """
    checks = {}
    healthy = True

    # PostgreSQL check
    db_start = time.monotonic()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["database"] = {
            "status": "ok",
            "latency_ms": round((time.monotonic() - db_start) * 1000, 1),
        }
    except Exception as e:
        checks["database"] = {"status": "error", "detail": str(e)}
        healthy = False

    # Redis check
    redis_start = time.monotonic()
    try:
        cache.set("health_check_ping", "pong", timeout=5)
        result = cache.get("health_check_ping")
        if result != "pong":
            raise ValueError("Cache returned unexpected value")
        checks["cache"] = {
            "status": "ok",
            "latency_ms": round((time.monotonic() - redis_start) * 1000, 1),
        }
    except Exception as e:
        checks["cache"] = {"status": "error", "detail": str(e)}
        healthy = False

    # Celery worker check via ping — SOFT dependency: async workers going down
    # must not pull the HTTP service out of rotation (their queue drains
    # independently and they are alerted on separately via worker liveness /
    # Sentry task-failure alerts). DB and cache above remain hard checks.
    celery_start = time.monotonic()
    try:
        from celery import current_app

        inspect = current_app.control.inspect()
        ping_result = inspect.ping()
        if ping_result:
            checks["celery"] = {
                "status": "ok",
                "latency_ms": round((time.monotonic() - celery_start) * 1000, 1),
                "workers": list(ping_result.keys()),
            }
        else:
            checks["celery"] = {"status": "unavailable", "detail": "No Celery workers responded"}
    except Exception as e:
        checks["celery"] = {"status": "unavailable", "detail": str(e)}

    status_code = 200 if healthy else 503
    return JsonResponse(
        {"status": "ready" if healthy else "not_ready", "checks": checks},
        status=status_code,
    )


def startup(request):
    """Startup probe — Has the app fully initialized?"""
    try:
        from django.db.migrations.executor import MigrationExecutor

        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if plan:
            return JsonResponse(
                {"status": "not_ready", "detail": "Pending migrations"},
                status=503,
            )
        return JsonResponse({"status": "started"})
    except Exception as e:
        return JsonResponse({"status": "error", "detail": str(e)}, status=503)


urlpatterns = [
    path("live/", liveness),
    path("ready/", readiness),
    path("startup/", startup),
]
