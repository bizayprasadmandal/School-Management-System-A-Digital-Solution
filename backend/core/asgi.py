"""
ASGI Configuration — Django Channels routing for HTTP + WebSocket
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from core.middleware.jwt_auth import JWTAuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

# get_asgi_application() must be called before importing routing modules
# to ensure Django is fully initialized (E402 is expected here)
django_asgi_app = get_asgi_application()

# Import routing after Django initialization to avoid circular imports
from services.communication.routing import websocket_urlpatterns  # noqa: E402 — intentional post-init import

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
