"""
School Management System — Base Django Settings
"""

import os
from datetime import timedelta
from pathlib import Path

import environ

env = environ.Env(DEBUG=(bool, False))

BASE_DIR = Path(__file__).resolve().parent.parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1", "0.0.0.0"],  # nosec B104 — allowlist of hostnames, not a bind address
)

# ─── Applications ────────────────────────────────────────────────────────────

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "whitenoise.runserver_nostatic",
    "corsheaders",
    "django_filters",
    "graphene_django",
    "channels",
    "django_celery_beat",
    "storages",
    "drf_spectacular",
    "axes",
    "django_prometheus",
]

LOCAL_APPS = [
    "services.auth",
    "services.students",
    "services.academics",
    "services.attendance",
    "services.gradebook",
    "services.timetable",
    "services.communication",
    "services.reporting",
    "services.fees",
    "services.behavior",
    "services.library",
    "services.conferences",
    "services.hr",
    "services.transportation",
    "services.inventory",
    "services.hostel",
    "services.sports",
    "services.health_clinic",
    "services.alumni",
    "services.cafeteria",
    "services.counseling",
    "services.admissions",
    "services.infrastructure",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ─── Middleware ───────────────────────────────────────────────────────────────

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
    "core.middleware.request_logging.RequestLoggingMiddleware",
    "core.middleware.tenant.TenantMiddleware",
    "core.middleware.email_verification.EmailVerificationMiddleware",
    "core.middleware.api_versioning.APIVersioningMiddleware",
    "core.middleware.body_size_limit.RequestBodySizeMiddleware",
    "core.middleware.idempotency.IdempotencyMiddleware",
    "core.middleware.session_timeout.SessionTimeoutMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "core.urls"

# ─── Templates ───────────────────────────────────────────────────────────────

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ASGI_APPLICATION = "core.asgi.application"

# ─── Database ────────────────────────────────────────────────────────────────

DATABASES = {
    "default": env.db("DATABASE_URL", default="postgresql://sms:sms@localhost:5432/sms_db"),
}
# NOTE: ATOMIC_REQUESTS is intentionally NOT enabled. DRF's exception_handler
# calls set_rollback() for every handled 4xx response, which would roll back the
# whole request transaction — silently discarding writes made earlier in the
# request (e.g. Axes brute-force AccessAttempt records and backup-code failure
# counters). Flows that need atomicity use explicit transaction.atomic blocks.

# ─── Cache (Redis) ────────────────────────────────────────────────────────────

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://localhost:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
            "IGNORE_EXCEPTIONS": True,
        },
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# ─── Auth ────────────────────────────────────────────────────────────────────

AUTH_USER_MODEL = "auth_service.User"
# Axes 6.x backends are monitoring-only (they never authenticate users), so
# ModelBackend must follow the Axes backend to perform the real login.
AUTHENTICATION_BACKENDS = [
    "services.auth.backends.AxesNextAttemptLockoutBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ─── Axes (Brute-force protection) ───────────────────────────────────────────

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=30)
# Login payloads carry `email`, not `username`, so track failures per email
# (otherwise every user on the same IP shares one failure bucket).
AXES_USERNAME_FORM_FIELD = "email"
# Axes 6.x defaults to IP-only lockout ("ip_address") unless this legacy flag
# is set — per-account (username + IP) buckets so one user's failures never
# lock out everyone behind the same NAT/IP.
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
# Lock out on the attempt AFTER the 5th failure (not on the 5th itself), so
# users see the 5 failed attempts as plain 401s and only the 6th is blocked.
# With AXES_LOCK_OUT_AT_FAILURE=False the stock Axes never blocks, so the
# blocking is re-implemented in services.auth.backends.AxesNextAttemptLockoutBackend,
# which flags the request; core.exceptions.py turns that into a 403 because
# the Django AxesMiddleware (raw request) cannot see the flag on the DRF request.
AXES_LOCK_OUT_AT_FAILURE = False

# ─── REST Framework ───────────────────────────────────────────────────────────

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "50/hour",
        "user": "500/hour",
        # Anon login limit — raised in e2e environments via AUTH_LOGIN_THROTTLE_RATE
        # so suites (many sequential logins from one IP) aren't throttled mid-run.
        "auth_login": env("AUTH_LOGIN_THROTTLE_RATE", default="10/minute"),
        # 2FA verification (TOTP + backup codes) per-IP limit.
        "auth_verify_2fa_login": env("AUTH_VERIFY_2FA_THROTTLE_RATE", default="5/minute"),
    },
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
}

# ─── JWT ─────────────────────────────────────────────────────────────────────

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "TOKEN_OBTAIN_SERIALIZER": "services.auth.serializers.CustomTokenObtainPairSerializer",
}

# ─── Channels (WebSocket) ─────────────────────────────────────────────────────

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env("REDIS_URL", default="redis://localhost:6379/0")],
        },
    },
}

# ─── Celery ───────────────────────────────────────────────────────────────────

CELERY_BROKER_URL = env("REDIS_URL", default="redis://localhost:6379/1")
CELERY_RESULT_BACKEND = env("REDIS_URL", default="redis://localhost:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# The beat schedule lives in one place: `core/celery.py` (app.conf.beat_schedule),
# which is assigned after config_from_object so it always wins. Keeping a
# second copy here caused drift and stale DB entries.

# ─── Storage (S3) ─────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="sms-documents")
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default=None)
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = "private"

# ─── Frontend URL (used in emails etc.) ────────────────────────────────────

FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:3000")

# ─── CORS ─────────────────────────────────────────────────────────────────────

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:3000", "http://localhost:8080"],
)
CORS_ALLOW_CREDENTIALS = True

# ─── GraphQL ─────────────────────────────────────────────────────────────────

GRAPHENE = {
    "SCHEMA": "api.graphql.schema.schema",
    "MIDDLEWARE": [
        "graphql_jwt.middleware.JSONWebTokenMiddleware",
    ],
}

# ─── Email ────────────────────────────────────────────────────────────────────

EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="smtp.sendgrid.net")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="apikey")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@school.edu")

# ─── SMS Providers (Twilio + Vonage fallback) ──────────────────────────────────

TWILIO_ACCOUNT_SID = env("TWILIO_ACCOUNT_SID", default="")
TWILIO_AUTH_TOKEN = env("TWILIO_AUTH_TOKEN", default="")
TWILIO_PHONE_NUMBER = env("TWILIO_PHONE_NUMBER", default="")
TWILIO_MESSAGING_SERVICE_SID = env("TWILIO_MESSAGING_SERVICE_SID", default="")

VONAGE_API_KEY = env("VONAGE_API_KEY", default="")
VONAGE_API_SECRET = env("VONAGE_API_SECRET", default="")
VONAGE_FROM_NUMBER = env("VONAGE_FROM_NUMBER", default="")
SMS_PROVIDER = env("SMS_PROVIDER", default="twilio")  # "twilio" | "vonage" | "console"

# ─── Push Notifications (Expo + Firebase FCM fallback) ──────────────────────

FIREBASE_CREDENTIALS = env("FIREBASE_CREDENTIALS", default="")
EXPO_ACCESS_TOKEN = env("EXPO_ACCESS_TOKEN", default="")

# ─── Zoom (Video Conferencing) ────────────────────────────────────────────────

ZOOM_ACCOUNT_ID = env("ZOOM_ACCOUNT_ID", default="")
ZOOM_CLIENT_ID = env("ZOOM_CLIENT_ID", default="")
ZOOM_CLIENT_SECRET = env("ZOOM_CLIENT_SECRET", default="")

# ─── Stripe (Payment Gateway) ─────────────────────────────────────────────────

STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY", default="")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="")
# When True (and STRIPE_WEBHOOK_SECRET is unset) the webhook endpoint REJECTS
# requests instead of parsing them unsigned — fail-closed. Defaults to the
# inverse of DEBUG (lenient in dev, strict in prod); production.py forces
# True so production can never silently accept unsigned webhooks.
STRIPE_WEBHOOK_REQUIRE_SIGNATURE = env.bool("STRIPE_WEBHOOK_REQUIRE_SIGNATURE", default=not DEBUG)

# ─── Nepali Payment Gateways ─────────────────────────────────────────────────

KHALTI_SECRET_KEY = env("KHALTI_SECRET_KEY", default="")
KHALTI_MERCHANT_ID = env("KHALTI_MERCHANT_ID", default="")
ESEWA_MERCHANT_CODE = env("ESEWA_MERCHANT_CODE", default="")
ESEWA_SECRET_KEY = env("ESEWA_SECRET_KEY", default="")

# Gateway API base URLs. Dev defaults are the sandbox endpoints; production
# deployments MUST override these with the live gateway hosts (see
# production.py for the fail-safe production defaults):
#   KHALTI_BASE_URL          — https://khalti.com
#   ESEWA_BASE_URL           — https://epay.esewa.com.np (payment form)
#   ESEWA_STATUS_BASE_URL    — https://esewa.com.np (status check + refund)
KHALTI_BASE_URL = env("KHALTI_BASE_URL", default="https://dev.khalti.com")
ESEWA_BASE_URL = env("ESEWA_BASE_URL", default="https://rc-epay.esewa.com.np")
ESEWA_STATUS_BASE_URL = env("ESEWA_STATUS_BASE_URL", default="https://rc.esewa.com.np")

# ─── Internationalization ─────────────────────────────────────────────────────

LANGUAGE_CODE = "en-us"
TIME_ZONE = env("TIME_ZONE", default="UTC")
USE_I18N = True
USE_TZ = True

# ─── API Docs ─────────────────────────────────────────────────────────────────

SPECTACULAR_SETTINGS = {
    "TITLE": "School Management System API",
    "DESCRIPTION": "Comprehensive API for the School Management System",
    "VERSION": "2.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "TAGS": [
        {"name": "auth", "description": "Authentication endpoints"},
        {"name": "students", "description": "Student management"},
        {"name": "academics", "description": "Academic management"},
        {"name": "attendance", "description": "Attendance tracking"},
        {"name": "gradebook", "description": "Grades and assessments"},
        {"name": "timetable", "description": "Schedule management"},
        {"name": "communication", "description": "Messaging and announcements"},
        {"name": "reporting", "description": "Reports and analytics"},
        {"name": "fees", "description": "Fee management"},
    ],
}

# ─── Logging ─────────────────────────────────────────────────────────────────

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "services": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}
