"""Live login verification for the canonical credential scheme."""

import json
import os
import urllib.error
import urllib.request

BASE = "http://localhost:8000/api/v1"

PROBES = [
    ("admin@demo.edusphere.school", "Admin@1234", "school_admin/demo"),
    ("admin@brightfuture.edu", "Admin@1234", "school_admin/BFA"),
    ("admin@greenvalley.edu", "Admin@1234", "school_admin/GVS"),
    ("sarah.mitchell@demo.edusphere.school", "Teacher@1234", "teacher/demo"),
    ("alice.morgan@greenvalley.edu", "Teacher@1234", "teacher/GVS"),
    ("student001@demo.edusphere.school", "Student@1234", "student/demo"),
    ("student0001@greenvalley.edu", "Student@1234", "student/GVS"),
    ("parent001@demo.edusphere.school", "Parent@1234", "parent/demo"),
    ("parent0001@brightfuture.edu", "Parent@1234", "parent/BFA"),
    ("counselor@demo.edusphere.school", "Admin@1234", "counselor/demo"),
    ("librarian@demo.edusphere.school", "Admin@1234", "librarian/demo"),
    ("accountant@demo.edusphere.school", "Admin@1234", "accountant/demo"),
    ("alumni1.fowler@alumni.gvs.edu", "Alumni@1234", "alumni/GVS"),
    ("smoke@demo.edusphere.school", "Admin@1234", "super_admin"),
    ("admin@school.edu", "TestPass@1234", "e2e/unchanged"),
]

ok = fail = 0
for email, pwd, label in PROBES:
    body = json.dumps({"email": email, "password": pwd}).encode()
    req = urllib.request.Request(f"{BASE}/auth/login/", data=body, headers={"Content-Type": "application/json"})
    try:
        # Fixed internal URL constant; no user-supplied scheme.
        with urllib.request.urlopen(req, timeout=10) as resp:  # nosec B310
            status = resp.status
    except urllib.error.HTTPError as e:
        status = e.code
    except Exception as e:  # noqa: BLE001
        status = str(e)
    good = status == 200
    ok += good
    fail += not good
    print(f"{'✓' if good else '✗'} {label:<22} {email} / {pwd}  [{status}]")

print(f"\n{ok} ok, {fail} failed")
