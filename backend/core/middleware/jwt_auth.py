"""
JWT Auth Middleware Stack for Django Channels WebSocket connections.
Authenticates WebSocket connections using Bearer tokens from query params or headers.
"""

import logging
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)


@database_sync_to_async
def get_user_from_token(token_key: str):
    """Validate JWT and return the associated user or AnonymousUser."""
    from services.auth.models import User

    try:
        token = AccessToken(token_key)
        user_id = token["user_id"]
        return User.objects.select_related("school").get(id=user_id, is_active=True)
    except (TokenError, InvalidToken, User.DoesNotExist) as exc:
        logger.debug("WS JWT auth failed: %s", exc)
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Extracts token from:
      1. Query string: ?token=<access_token>
      2. Subprotocol header: Sec-WebSocket-Protocol: Bearer, <token>
    """

    async def __call__(self, scope, receive, send):
        # Try query string first
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token_list = params.get("token", [])

        if token_list:
            token_key = token_list[0]
            logger.warning("WS auth via query string is deprecated — use Sec-WebSocket-Protocol header instead.")
        else:
            # Try subprotocol header
            headers = dict(scope.get("headers", []))
            protocol_header = headers.get(b"sec-websocket-protocol", b"").decode()
            parts = [p.strip() for p in protocol_header.split(",")]
            token_key = parts[1] if len(parts) >= 2 and parts[0].lower() == "bearer" else ""

        scope["user"] = await get_user_from_token(token_key) if token_key else AnonymousUser()
        return await super().__call__(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)
