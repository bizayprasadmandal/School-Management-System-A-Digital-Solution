"""Probe school-scoped endpoints as a school-switched super admin.

Logs in over HTTP as the super admin, picks a school via ``X-School-ID``, then
hits each endpoint the admin panel's pages call and reports status + a compact
payload signature. Used to tell "data exists but the page shows nothing" (real
UI bug) apart from "that school simply has no rows" (unseeded).

Run inside the backend container:

    python scripts/audit_school_endpoints.py "Green Valley School"
"""

import json
import os
import sys
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

# Page -> endpoint hit by its default tab / summary cards.
ENDPOINTS = [
    ("Dashboard", "reporting/dashboard-stats/"),
    ("HR Center (top cards)", "hr/hr-dashboard/"),
    ("HR Center (metrics model)", "hr/hr-dashboard-metrics/"),
    ("HR Center (payroll runs)", "hr/payroll-runs/"),
    ("HR Center (employees)", "hr/employees/"),
    ("Hostel (allocations)", "hostel/allocations/"),
    ("Hostel (rooms)", "hostel/rooms/"),
    ("Auth Center (api keys)", "auth/api-keys/"),
    ("Communication (announcements)", "communication/announcements/"),
    ("Communication (unread count)", "communication/notifications/unread-count/"),
]


def login():
    data = json.dumps({"email": EMAIL, "password": PASSWORD}).encode()
    req = urllib.request.Request(f"{BASE}/auth/login/", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:  # nosec B310
        return json.loads(r.read())["access"]


def call(path, token, sid=None):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    if sid:
        headers["X-School-ID"] = sid
    req = urllib.request.Request(f"{BASE}/{path}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:  # nosec B310
            body = r.read()
            status = r.status
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:200].decode(errors="replace")
    except Exception as exc:  # noqa: BLE001
        return "ERR", str(exc)[:200]
    try:
        payload = json.loads(body)
    except Exception:  # noqa: BLE001
        return status, body[:120].decode(errors="replace")
    if isinstance(payload, dict) and "count" in payload:
        return status, f"count={payload['count']}"
    if isinstance(payload, dict):
        keys = list(payload)[:6]
        return status, f"dict keys={keys}"
    return status, f"list len={len(payload)}"


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "Green Valley School"
    school = School.objects.filter(name__icontains=name).first()
    if not school:
        print(f"no school matching {name!r}")
        return
    print(f"school: {school.name} ({school.id})\n")
    token = login()

    print(f"{'ENDPOINT':45} {'STATUS':7} PAYLOAD")
    print("-" * 90)
    for label, path in ENDPOINTS:
        status, sig = call(path, token, str(school.id))
        print(f"{path:45} {str(status):7} {sig[:60]}")
        if label != path:
            pass
    print()


if __name__ == "__main__":
    main()
