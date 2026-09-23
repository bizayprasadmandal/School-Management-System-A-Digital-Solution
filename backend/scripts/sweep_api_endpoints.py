"""Sweep every parameterless GET route as a school-switched super admin.

Broken viewsets are invisible until someone opens the page that uses them: an
invalid ``prefetch_related`` or a mistyped annotation surfaces as HTTP 500 and
the tab just looks empty. This walks the whole route table in one pass and
prints everything that is not a clean 2xx.

Run inside the backend container:

    python scripts/sweep_api_endpoints.py "Green Valley School"
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from services.auth.models import School  # noqa: E402

BASE = "http://localhost:8000/api/v1"
EMAIL = os.environ.get("AUDIT_USER", "bizaymndl@gmail.com")
PASSWORD = os.environ.get("AUDIT_PASS", "Admin@1234")
PATTERNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "url_patterns.json")

# Routes that are expected to reject a plain GET (write-only or method-routed).
IGNORE_STATUS = {405}

# Anything with a regex construct in it is a parameterised route (detail, action
# or converter) — only the plain list/collection routes are swept.
PARAM_CHARS = set("[]()\\<>^$?*+|{")
LIST_HINT = re.compile(r"/$")


def login():
    data = json.dumps({"email": EMAIL, "password": PASSWORD}).encode()
    req = urllib.request.Request(f"{BASE}/auth/login/", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:  # nosec B310
        return json.loads(r.read())["access"]


def call(path, token, sid):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-School-ID": sid,
    }
    req = urllib.request.Request(path, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:  # nosec B310
            return r.status, r.read(400).decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read(400).decode(errors="replace")
    except Exception as exc:  # noqa: BLE001
        return "ERR", str(exc)[:200]


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "Green Valley School"
    school = School.objects.filter(name__icontains=name).first()
    sid = str(school.id)
    token = login()

    raw = json.load(open(PATTERNS, encoding="utf-8"))
    paths = []
    for pattern in raw:
        # Included patterns are concatenated ("api/v1/hr/" + "^employees/$"),
        # so strip the anchors before deciding whether the route is plain.
        if "api/v1/" not in pattern:
            continue
        tail = pattern.replace("^", "").replace("$", "")
        tail = tail[tail.index("api/v1/") :]
        if PARAM_CHARS & set(tail):
            continue
        if not LIST_HINT.search(tail):
            continue
        paths.append("http://localhost:8000/" + tail)
    paths = sorted(set(paths))
    print(f"school: {school.name} | sweeping {len(paths)} parameterless routes\n", flush=True)

    bad = []
    start = time.time()
    for i, url in enumerate(paths, 1):
        status, body = call(url, token, sid)
        if status not in (200, 201, 204) and status not in IGNORE_STATUS:
            bad.append((status, url, body[:120].replace("\n", " ")))
            print(f"  {status} {url.replace('http://localhost:8000', '')} -> {body[:90]!r}", flush=True)
        if i % 100 == 0:
            print(f"  ... {i}/{len(paths)} ({time.time() - start:.0f}s)", flush=True)

    print(f"\nswept {len(paths)} routes in {time.time() - start:.0f}s | problems: {len(bad)}")
    by_status = {}
    for status, _url, _b in bad:
        by_status[status] = by_status.get(status, 0) + 1
    print(f"by status: {by_status}")


if __name__ == "__main__":
    main()
