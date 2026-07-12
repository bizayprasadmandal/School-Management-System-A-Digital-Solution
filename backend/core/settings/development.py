"""Development settings — hot reload, debug toolbar, verbose logging."""
# Explicit imports from base instead of star import to avoid # noqa
import sys
from .base import (
    INSTALLED_APPS as BASE_INSTALLED_APPS,
    MIDDLEWARE as BASE_MIDDLEWARE,
    REST_FRAMEWORK as BASE_REST_FRAMEWORK,
    CELERY_TASK_ALWAYS_EAGER as BASE_CELERY_EAGER,
    CELERY_TASK_EAGER_PROPAGATES as BASE_CELERY_PROPAGATES,
    *  # noqa: F403 — wildcard needed for Django settings convention
)

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Debug toolbar
INSTALLED_APPS = BASE_INSTALLED_APPS + ["debug_toolbar"]
MIDDLEWARE = list(BASE_MIDDLEWARE)
MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
INTERNAL_IPS = ["127.0.0.1"]

# Sync email to console in dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable throttling locally
REST_FRAMEWORK = {**BASE_REST_FRAMEWORK, "DEFAULT_THROTTLE_CLASSES": []}

# Make Celery tasks run synchronously (no broker needed locally)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

LOGGING = {
    "version": 1, "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "DEBUG"},
    "loggers": {
        "django.db.backends": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}
