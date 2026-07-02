"""
GraphQL View — wraps graphene-django's GraphQLView with DRF JWT authentication
so that `info.context.user` resolves correctly from the Authorization: Bearer header,
matching the same auth used across the REST API.
"""

from django.contrib.auth.models import AnonymousUser
from graphene_django.views import GraphQLView as BaseGraphQLView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class JWTAuthenticatedGraphQLView(BaseGraphQLView):
    """
    Authenticates the incoming request using the same SimpleJWT scheme as the
    REST API, then attaches the resolved user to request.user before Graphene
    processes the query. This makes `info.context.user` behave identically
    to `request.user` in DRF views, so `@login_required` and role checks
    in api/graphql/schema.py work as expected.
    """

    def parse_body(self, request):
        # Authenticate before any resolver runs
        self._authenticate(request)
        return super().parse_body(request)

    @staticmethod
    def _authenticate(request):
        auth = JWTAuthentication()
        try:
            result = auth.authenticate(request)
            if result is not None:
                user, _token = result
                request.user = user
                return
        except (InvalidToken, TokenError):
            pass
        # Fall back to whatever Django's auth middleware already set
        # (e.g. AnonymousUser), so unauthenticated queries can still
        # resolve public fields without raising.
        if not hasattr(request, "user") or request.user is None:
            request.user = AnonymousUser()
