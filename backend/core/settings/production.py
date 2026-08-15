"""
Production settings — extends base, enforces security, uses real services
"""

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

# Explicit imports from base (star import needed for Django settings convention)
from .base import *  # noqa: F401, F403 — Django settings require wildcard import

# ─── Security overrides ────────────────────────────────────────────────────────

DEBUG = False

SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# ─── Static / media (S3) ──────────────────────────────────────────────────────

# Allow disabling S3 during Docker build where MinIO is not available
USE_S3 = env.bool("USE_S3", default=True)
if USE_S3:
    STORAGES["default"]["BACKEND"] = "storages.backends.s3boto3.S3Boto3Storage"
    STORAGES["staticfiles"]["BACKEND"] = "storages.backends.s3boto3.S3StaticStorage"
else:
    # WhiteNoise serves compressed & hashed static files when S3 is unavailable
    STORAGES["default"]["BACKEND"] = "django.core.files.storage.FileSystemStorage"
    STORAGES["staticfiles"]["BACKEND"] = "whitenoise.storage.CompressedManifestStaticFilesStorage"

AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_QUERYSTRING_AUTH = False

# ─── Email (production SendGrid) ──────────────────────────────────────────────

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# ─── Logging ──────────────────────────────────────────────────────────────────

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": ("%(asctime)s %(levelname)s %(name)s %(process)d %(message)s" " %(pathname)s %(lineno)d"),
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "json"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        # Celery worker + task loggers are routed here by the `setup_logging`
        # signal in core/celery.py (JSON lines; task `extra` fields preserved).
        "celery": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "celery.task": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.security": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "services": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

# ─── Sentry error tracking ─────────────────────────────────────────────────────

SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(transaction_style="url"),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment="production",
        release=env("APP_VERSION", default="unknown"),
    )

# ─── Cache (Redis Cluster) ────────────────────────────────────────────────────

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
            "CONNECTION_POOL_KWARGS": {"max_connections": 50},
        },
    }
}

# ─── Database (with read replica support) ─────────────────────────────────────

DATABASES = {
    "default": env.db("DATABASE_URL"),
}

REPLICA_URL = env("DATABASE_REPLICA_URL", default="")
if REPLICA_URL:
    DATABASES["replica"] = env.db_url(REPLICA_URL)
    DATABASE_ROUTERS = ["core.routers.ReadReplicaRouter"]

DATABASES["default"]["CONN_MAX_AGE"] = 60

# ─── Email Verification Enforcement ────────────────────────────────────────────

EMAIL_VERIFICATION_ENFORCED = True

# ─── Stripe webhook (production) ───────────────────────────────────────────────
# Fail closed: without STRIPE_WEBHOOK_SECRET the webhook endpoint rejects every
# request. This overrides base.py's DEBUG-derived default so that a production
# deployment with DEBUG=True can never silently accept unsigned webhooks.

STRIPE_WEBHOOK_REQUIRE_SIGNATURE = env.bool("STRIPE_WEBHOOK_REQUIRE_SIGNATURE", default=True)

# ─── Payment gateway base URLs (production) ───────────────────────────────────
# Override the sandbox defaults from base.py with the live gateway hosts. The
# values are still env-driven (KHALTI_BASE_URL / ESEWA_BASE_URL /
# ESEWA_STATUS_BASE_URL), but a production deployment that omits them falls
# back to the PRODUCTION endpoints — never the sandbox ones — so money can
# never silently flow into a test gateway.

KHALTI_BASE_URL = env("KHALTI_BASE_URL", default="https://khalti.com")
ESEWA_BASE_URL = env("ESEWA_BASE_URL", default="https://epay.esewa.com.np")
ESEWA_STATUS_BASE_URL = env("ESEWA_STATUS_BASE_URL", default="https://esewa.com.np")
