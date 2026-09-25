"""Live OpenAPI schema endpoints (/api/schema/, /api/docs/, /api/redoc/).

The contract the docs surface depends on:

1. **The schema endpoint must generate for an anonymous caller.** Schema
   generation introspects every view with a fake request — a viewset whose
   ``get_permissions``/``get_queryset`` dereferences ``request.user.role`` or
   ``request.user.school`` unguarded crashes the whole endpoint with a 500.
   (Both happened: ``AuditLogViewSet.get_permissions`` and the transportation
   vehicle viewsets' ``get_queryset``.)
2. **The document is usable** — OpenAPI 3, ~2200 paths, grouped by module tag,
   with the JWT bearer scheme attached to operations so Swagger UI shows the
   ``Authorize`` button.
3. **UI shells serve** — Swagger UI and ReDoc return HTML for humans.

Schema generation takes minutes for this API, so the document is produced
once per session and shared by all assertions.
"""

import pytest
import yaml
from django.test import Client
from django.urls import reverse


@pytest.fixture(scope="session")
def schema_response(django_db_setup, django_db_blocker):
    """Generate the schema once; the endpoint itself needs no database rows."""
    with django_db_blocker.unblock():
        client = Client(SERVER_NAME="localhost")
        r = client.get(reverse("schema"))
    return r


@pytest.fixture(scope="session")
def schema_doc(schema_response):
    return yaml.safe_load(schema_response.content)


def test_schema_generates_anonymous(schema_response):
    assert schema_response.status_code == 200, schema_response.content[:300]
    assert len(schema_response.content) > 1_000_000  # a stub means something regressed


def test_schema_document_shape(schema_doc):
    assert schema_doc["openapi"].startswith("3.")
    assert len(schema_doc["paths"]) > 2000

    # JWT security scheme registered (Authorize button in Swagger UI).
    assert "jwtAuth" in schema_doc["components"]["securitySchemes"]

    # Operations are grouped by module app — the useless URL-prefix default
    # ("v1") must not survive — and authenticated ops reference the scheme.
    tags = {
        t
        for ops in schema_doc["paths"].values()
        for op in ops.values()
        if isinstance(op, dict)
        for t in op.get("tags", [])
    }
    assert {"students", "fees", "auth", "hr", "library"} <= tags
    assert "v1" not in tags

    op = next(
        o for ops in schema_doc["paths"].values() for o in ops.values() if isinstance(o, dict) and o.get("security")
    )
    assert {"jwtAuth": []} in op["security"]


def test_swagger_ui_and_redoc_serve(db):
    client = Client(SERVER_NAME="localhost")
    for name in ("swagger-ui", "redoc"):
        r = client.get(reverse(name))
        assert r.status_code == 200
        assert b"html" in r.content[:600].lower()
