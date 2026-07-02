"""Development settings — hot reload, debug toolbar, verbose logging."""
from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Debug toolbar
INSTALLED_APPS += ["debug_toolbar"]  # noqa
MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa
INTERNAL_IPS = ["127.0.0.1"]

# Sync email to console in dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable throttling locally
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []  # noqa

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
