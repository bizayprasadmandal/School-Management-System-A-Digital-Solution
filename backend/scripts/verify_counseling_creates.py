"""Verify creates work on counseling endpoints (school auto-set server-side)."""

import json
import os
import urllib.error
import urllib.request

BASE = os.environ.get("BASE_URL", "http://localhost:8000/api/v1")

login_data = json.dumps({"email": "admin@demo.edusphere.school", "password": "admin123456"}).encode()
req = urllib.request.Request(f"{BASE}/auth/login/", data=login_data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310 - localhost smoke
    token = json.loads(resp.read())["access"]

H = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def call(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(f"{BASE}/counseling/{path}", data=data, headers=H, method=method)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:  # nosec B310 - localhost smoke
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:300]


def cleanup(method, path):
    try:
        call(method, path)
    except Exception:
        pass


created = []

# 1. workshop (school FK, has title)
code, body = call(
    "POST",
    "workshops/",
    {"title": "SMOKE Stress Mgmt", "description": "smoke", "workshop_type": "group", "status": "planned"},
)
print("workshop create:", code)
if code in (200, 201):
    created.append(("DELETE", f"workshops/{body['id']}/"))
    wid = body["id"]
    # workshop-registration (child)
    code2, body2 = call("POST", "workshop-registrations/", {"workshop": wid, "status": "registered"})
    print("workshop-registration create:", code2)
    if code2 in (200, 201):
        created.append(("DELETE", f"workshop-registrations/{body2['id']}/"))

# 2. provider (school FK)
code, body = call(
    "POST", "providers/", {"name": "SMOKE Counseling Associates", "provider_type": "therapist", "status": "active"}
)
print("provider create:", code)
if code in (200, 201):
    created.append(("DELETE", f"providers/{body['id']}/"))
    pid = body["id"]
    code2, body2 = call("POST", "referral-tracking/", {"provider": pid, "status": "referred"})
    print("referral-tracking create:", code2)
    if code2 in (200, 201):
        created.append(("DELETE", f"referral-tracking/{body2['id']}/"))

# 3. survey (school FK)
code, body = call(
    "POST", "surveys/", {"title": "SMOKE Program Feedback", "survey_type": "satisfaction", "status": "draft"}
)
print("survey create:", code)
if code in (200, 201):
    created.append(("DELETE", f"surveys/{body['id']}/"))

# get a student id for student-FK creates
r = urllib.request.Request(f"{BASE}/students/", headers={"Authorization": f"Bearer {token}"})
try:
    with urllib.request.urlopen(r, timeout=30) as resp:  # nosec B310 - localhost smoke
        students = json.loads(resp.read())
        rows = students.get("results", students)
        sid = rows[0]["id"] if rows else None
except Exception as e:
    print("students list failed:", e)
    sid = None

if sid:
    code, body = call(
        "POST",
        "sel-goals/",
        {"student": sid, "goal_description": "SMOKE goal", "domain": "self_awareness", "status": "active"},
    )
    print("sel-goal create:", code)
    if code in (200, 201):
        created.append(("DELETE", f"sel-goals/{body['id']}/"))
else:
    print("no student id — skipping student-FK create tests")

# cleanup in reverse
for method, path in reversed(created):
    m, resp = call(method, path)
    print("cleanup", path, m)

print("done")
