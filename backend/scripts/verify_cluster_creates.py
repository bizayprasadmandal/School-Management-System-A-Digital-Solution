"""Verify creates work on representative endpoints from each module."""

import json
import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

import urllib.error  # noqa: E402
import urllib.request  # noqa: E402

BASE = os.environ.get("BASE_URL", "http://localhost:8000/api/v1")

login_data = json.dumps({"email": "smoke@demo.edusphere.school", "password": "smoke123456"}).encode()
req = urllib.request.Request(  # nosec B310
    f"{BASE}/auth/login/", data=login_data, headers={"Content-Type": "application/json"}
)
token = json.loads(urllib.request.urlopen(req, timeout=30).read())["access"]  # nosec B310
H = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# (endpoint, payload) — each uses the smoke user's school implicitly
CASES = [
    ("reporting/report-bookmark/", {"name": "smoke bookmark", "report_type": "attendance", "report_id": "x"}),
    ("conferences/conference-location/", {"name": "Smoke Room", "location_type": "room"}),
    ("auth/device-management/", {"device_name": "smoke laptop", "device_type": "laptop"}),
    ("fees/payment-method/", {"name": "Smoke Cash", "payment_type": "cash"}),
]

for ep, payload in CASES:
    url = f"{BASE}/{ep}"
    data = json.dumps(payload).encode()
    try:
        resp = urllib.request.urlopen(  # nosec B310
            urllib.request.Request(url, data=data, headers=H, method="POST"), timeout=30
        )
        print(f"{ep} -> {resp.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        print(f"{ep} -> {e.code}: {body}")
