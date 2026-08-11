"""
Test settings — for running pytest locally against Docker PostgreSQL.
Sets environment defaults BEFORE importing base so that env() calls
in base.py resolve successfully. Overrides external service configs
for test isolation.
"""

import os

# ── Set environment defaults BEFORE importing base ────────────────────────────
# base.py calls env() at module level, so these must be set first.
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("DATABASE_URL", "postgresql://sms:sms@localhost:5432/sms_db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("ALLOWED_HOSTS", "localhost,127.0.0.1")
os.environ.setdefault("CORS_ALLOWED_ORIGINS", "http://localhost:3000")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")
os.environ.setdefault("DEBUG", "False")

from .base import *  # noqa: F403, F401, E402 — safe now that env vars are set

# Remove debug_toolbar (it's in development.py only)
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]
MIDDLEWARE = [m for m in MIDDLEWARE if "debug_toolbar" not in m]

DEBUG = False

# Database — connect to Docker PostgreSQL on localhost
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "sms_db",
        "USER": "sms",
        "PASSWORD": "sms_password",
        "HOST": "localhost",
        "PORT": 5432,
        # ATOMIC_REQUESTS intentionally off — see comment in base.py (DRF
        # set_rollback on 4xx would wipe Axes/backup-code failure counters.
    }
}

# Cache — in-memory for tests (no Redis needed)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Channels — in-memory for tests
CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
}

# Email — locmem backend for tests (no SMTP server needed)
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# File storage — local filesystem for tests
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# Disable throttling for tests
REST_FRAMEWORK = {**REST_FRAMEWORK, "DEFAULT_THROTTLE_CLASSES": []}

# Disable Axes (brute-force protection) for tests
AXES_ENABLED = False

# Disable Sentry for tests
SENTRY_DSN = ""

# Disable email verification enforcement for tests
EMAIL_VERIFICATION_ENFORCED = False

# Disable payment gateways for tests
STRIPE_SECRET_KEY = ""
STRIPE_PUBLISHABLE_KEY = ""
KHALTI_SECRET_KEY = ""
KHALTI_MERCHANT_ID = ""
ESEWA_MERCHANT_CODE = ""
ESEWA_SECRET_KEY = ""
ZOOM_ACCOUNT_ID = ""
ZOOM_CLIENT_ID = ""
ZOOM_CLIENT_SECRET = ""
TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_PHONE_NUMBER = ""
SMS_PROVIDER = "console"  # Use console logging in tests, not real SMS
FIREBASE_CREDENTIALS = ""
