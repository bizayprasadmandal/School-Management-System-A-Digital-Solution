"""
Pytest configuration — shared fixtures and Django settings override for tests.
"""
import pytest
from django.conf import settings


def pytest_configure(config):
    """Override settings for the test run."""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    settings.AXES_ENABLED = False  # Disable brute-force protection in tests
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
    settings.CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
    }


@pytest.fixture(autouse=True)
def reset_cache():
    """Clear cache between tests."""
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def rf():
    """DRF APIRequestFactory."""
    from rest_framework.test import APIRequestFactory
    return APIRequestFactory()


@pytest.fixture
def authenticated_request(rf):
    """Return a factory that creates authenticated requests."""
    def _make(user):
        from rest_framework.test import APIClient
        client = APIClient()
        client.force_authenticate(user=user)
        return client
    return _make
