"""OpenAPI schema customization for drf-spectacular.

Two jobs:

1. **JWT security scheme** — :class:`core.authentication.JWTAuthenticationWithTenant`
   isn't known to drf-spectacular, so without an extension the generated
   schema has no security definitions and Swagger UI shows no ``Authorize``
   button. The extension below registers it as an HTTP Bearer scheme.

2. **Per-app operation tags** — the default URL-path-prefix splitting lumps
   every operation under a single ``v1`` tag, which is useless for a
   2200-path API. :class:`TaggedAutoSchema` derives the tag from the URL
   segment after ``/api/v1/`` (e.g. ``students``, ``fees``), falling back to
   spectacular's default for anything mounted outside that prefix.

Wiring:

- ``REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = "core.schema.TaggedAutoSchema"``
- ``from core import schema  # noqa`` in ``CoreConfig.ready()`` so the
  authentication extension registers for both live serving and the
  ``spectacular`` management command.
"""

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.openapi import AutoSchema


class JWTWithTenantScheme(OpenApiAuthenticationExtension):
    """Expose ``JWTAuthenticationWithTenant`` as HTTP Bearer auth."""

    target_class = "core.authentication.JWTAuthenticationWithTenant"
    name = "jwtAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "SimpleJWT access token from ``/api/v1/auth/login/``.",
        }


class TaggedAutoSchema(AutoSchema):
    """Tag operations by their app URL segment (``/api/v1/<app>/...``)."""

    def get_tags(self):
        parts = [p for p in self.path.strip("/").split("/") if p]
        if len(parts) >= 3 and parts[0] == "api" and parts[1] == "v1":
            return [parts[2]]
        return super().get_tags()


__all__ = ["JWTWithTenantScheme", "TaggedAutoSchema"]
