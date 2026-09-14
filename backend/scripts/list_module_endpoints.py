"""Enumerate list endpoints for given URL prefixes via Django URL resolution."""

import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from django.urls import get_resolver  # noqa: E402

MODULES = sys.argv[1:] if len(sys.argv) > 1 else ["reporting", "conferences", "auth", "fees"]
resolver = get_resolver()


def walk(patterns, prefix):
    for p in patterns:
        path = prefix + str(p.pattern)
        if hasattr(p, "url_patterns"):
            yield from walk(p.url_patterns, path)
        elif path.endswith("$") and "{" not in path and "<" not in path:
            yield path.rstrip("$")


all_routes = list(walk(resolver.url_patterns, ""))
for mod in MODULES:
    hits = sorted({r for r in all_routes if f"/{mod}/" in r and r.count("/") <= 4})
    print(f"== {mod} ({len(hits)}) ==")
    for r in hits:
        print(r)
