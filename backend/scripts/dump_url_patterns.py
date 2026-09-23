"""Dump every registered URL pattern (as a regex) to JSON.

Feeds ``check_frontend_routes.py``, which compares the paths the web app calls
against the routes the API actually exposes — catching dead tabs/endpoints
(e.g. a page calling ``/hr/hr-dashboard/`` when only ``hr-dashboard/metrics/``
exists).

Run inside the backend container:

    python scripts/dump_url_patterns.py /tmp/url_patterns.json
"""

import json
import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from django.urls import get_resolver  # noqa: E402


def walk(patterns, prefix=""):
    for p in patterns:
        if hasattr(p, "url_patterns"):
            yield from walk(p.url_patterns, prefix + str(p.pattern))
        else:
            yield prefix + str(p.pattern)


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "url_patterns.json"  # nosec B108
    routes = sorted(set(walk(get_resolver().url_patterns)))
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(routes, fh, indent=1)
    print(f"wrote {len(routes)} patterns to {out_path}")


if __name__ == "__main__":
    main()
