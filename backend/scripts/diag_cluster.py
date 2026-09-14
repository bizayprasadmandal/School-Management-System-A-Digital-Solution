"""Print the exception for each failing endpoint."""

import json
import os
import sys
import traceback

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django

django.setup()

import services.auth.models as am  # noqa: E402
from django.test import Client  # noqa: E402
from django.test.utils import setup_test_environment  # noqa: E402
from django.urls import get_resolver  # noqa: E402

user = am.User.objects.filter(is_superuser=True).first() or am.User.objects.first()
client = Client(SERVER_NAME="localhost")
client.force_login(user)

resolver = get_resolver()


def walk(patterns, prefix):
    for p in patterns:
        path = prefix + str(p.pattern)
        if hasattr(p, "url_patterns"):
            yield from walk(p.url_patterns, path)
        elif path.endswith("$") and "{" not in path and "<" not in path:
            yield path.rstrip("$").lstrip("^")


all_routes = list(walk(resolver.url_patterns, ""))
seen = set()
for mod in ["reporting", "conferences", "fees"]:
    routes = sorted({r.replace("^", "") for r in all_routes if f"/{mod}/" in r and r.count("/") <= 4})
    for r in routes:
        resp = client.get("/" + r)
        if resp.status_code == 500 and r not in seen:
            seen.add(r)
            # re-raise to capture traceback
            try:
                client.get("/" + r, raise_request_exception=True)
            except Exception:
                tb = traceback.format_exc().splitlines()
                print(f"== {r}")
                print("\n".join(tb[-6:]))
