"""Check why hostel tabs show 0 rows while the DB has rows.

Logs in as the super admin, switches to Green Valley via X-School-ID, and
counts rows for every /hostel/<ep>/ endpoint the HostelCenter page uses.
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from services.auth.models import User  # noqa: E402

BASE = "http://localhost:8000/api/v1"
SCHOOL_NAME = "Green Valley School"

ENDPOINTS = [
    "allocations",
    "attendance",
    "checkouts",
    "common-area-booking",
    "complaints",
    "emergency-contacts",
    "feedback",
    "fees",
    "hostel-asset",
    "hostel-asset-transfer",
    "hostel-attendance-alert",
    "hostel-emergency-drill",
    "hostel-emergency-protocol",
    "hostel-event",
    "hostel-event-participant",
    "hostel-fee-payment",
    "hostel-inspection-schedule",
    "hostels",
    "inspections",
    "inventory",
    "laundry-service",
    "leaves",
    "maintenance",
    "mess",
    "mess-attendance",
    "mess-dietary-request",
    "mess-feedback",
    "mess-menu-plan",
    "notifications",
    "reports",
    "room-key",
    "roommate-assignment",
    "roommate-match-request",
    "roommate-preference",
    "rooms",
    "transfers",
    "visitor-pass",
    "visitors",
    "wellness-check",
]


def get_school_id(name):
    from services.auth.models import School

    s = School.objects.filter(name__icontains=name.split()[0]).first()
    return str(s.id) if s else None


def main():
    u = User.objects.filter(email="bizaymndl@gmail.com").first()
    if not u:
        print("NO USER")
        return

    school_id = get_school_id(SCHOOL_NAME)
    print("school id:", school_id)

    data = urllib.parse.urlencode({"email": u.email, "password": "Admin@1234"}).encode()
    req = urllib.request.Request(f"{BASE}/auth/login/", data=data)
    with urllib.request.urlopen(req, timeout=15) as r:  # nosec B310
        token = json.loads(r.read()).get("access") or json.loads(r.read()).get("token")

    headers = {"Authorization": f"Bearer {token}", "X-School-ID": school_id or ""}

    for ep in ENDPOINTS:
        req = urllib.request.Request(f"{BASE}/hostel/{ep}/", headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as r:  # nosec B310
                body = json.loads(r.read())
            count = body.get("count", len(body) if isinstance(body, list) else "?")
            print(f"{ep:28s} -> {r.status}  count={count}")
        except urllib.error.HTTPError as e:
            print(f"{ep:28s} -> HTTP {e.code}")
        except Exception as e:  # noqa: BLE001
            print(f"{ep:28s} -> ERR {e}")


if __name__ == "__main__":
    main()
