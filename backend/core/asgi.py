"""
ASGI Configuration — Django Channels routing for HTTP + WebSocket

WARNING: All Django-dependent imports (channels, middleware, routing)
MUST come AFTER get_asgi_application() to avoid AppRegistryNotReady.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

# get_asgi_application() MUST be called first to fully initialize Django's
# app registry. Any import that touches Django models (including channels
# middleware like JWTAuthMiddlewareStack) will crash if imported before this.
django_asgi_app = get_asgi_application()

# ── All Django-dependent imports go AFTER get_asgi_application() ──────────────

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.security.websocket import OriginValidator  # noqa: E402
from core.middleware.jwt_auth import JWTAuthMiddlewareStack  # noqa: E402
from services.communication.routing import websocket_urlpatterns  # noqa: E402
from django.conf import settings  # noqa: E402

# ── Determine valid WebSocket origins ─────────────────────────────────────────
# AllowedHostsOriginValidator normally passes ALLOWED_HOSTS to OriginValidator.
# However, OriginValidator compares ports too — and dev servers use non-default
# ports (3000, 8000), causing rejections even when the hostname is valid.
#
# In DEBUG mode, skip WebSocket origin checks for local dev convenience.
# In production, ALLOWED_HOSTS hostnames match via OriginValidator's
# is_same_domain path (no port comparison), so production is unaffected.
ALLOWED_WS_ORIGINS = ["*"] if settings.DEBUG else list(settings.ALLOWED_HOSTS)

# ── Application ───────────────────────────────────────────────────────────────

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": OriginValidator(
        JWTAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
        ALLOWED_WS_ORIGINS,
    ),
})
