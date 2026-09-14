"""Live smoke for reporting/conferences/auth/fees with dedicated smoke user."""

import json
import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

import urllib.error  # noqa: E402
import urllib.request  # noqa: E402

from django.urls import get_resolver  # noqa: E402

BASE = os.environ.get("BASE_URL", "http://localhost:8000/api/v1")
EMAIL = "smoke@demo.edusphere.school"
PASS = "smoke123456"

login_data = json.dumps({"email": EMAIL, "password": PASS}).encode()
req = urllib.request.Request(  # nosec B310
    f"{BASE}/auth/login/", data=login_data, headers={"Content-Type": "application/json"}
)
try:
    token = json.loads(urllib.request.urlopen(req, timeout=30).read())["access"]  # nosec B310
except Exception as e:
    print("LOGIN FAILED:", e)
    sys.exit(1)

MODULES = sys.argv[1:] or ["reporting", "conferences", "auth", "fees"]
resolver = get_resolver()


def walk(patterns, prefix):
    for p in patterns:
        path = prefix + str(p.pattern)
        if hasattr(p, "url_patterns"):
            yield from walk(p.url_patterns, path)
        elif path.endswith("$") and "{" not in path and "<" not in path:
            yield path.rstrip("$").lstrip("^")


all_routes = list(walk(resolver.url_patterns, ""))

total_ok = total_bad = 0
for mod in MODULES:
    routes = sorted({r.replace("^", "") for r in all_routes if f"/{mod}/" in r and r.count("/") <= 4})
    ok = bad = 0
    for r in routes:
        url = "http://localhost:8000/" + r
        req2 = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})  # nosec B310
        try:
            resp = urllib.request.urlopen(req2, timeout=30)  # nosec B310
            code = resp.status
        except urllib.error.HTTPError as e:
            code = e.code
        if code == 200:
            ok += 1
        else:
            bad += 1
            print(f"  {r} -> {code}")
    total_ok += ok
    total_bad += bad
    print(f"{mod}: {ok} ok, {bad} bad / {len(routes)}")
print(f"TOTAL: {total_ok} ok, {total_bad} bad")
