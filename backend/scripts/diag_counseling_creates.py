"""Diagnose 400 errors on counseling creates by printing error bodies."""

import json
import urllib.error
import urllib.request

BASE = "http://localhost:8000/api/v1"

login_data = json.dumps({"email": "admin@demo.edusphere.school", "password": "admin123456"}).encode()
req = urllib.request.Request(f"{BASE}/auth/login/", data=login_data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310 - localhost smoke
    token = json.loads(resp.read())["access"]

H = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# grab a staff user id for FK fields like organizer
r = urllib.request.Request(f"{BASE}/auth/me/", headers={"Authorization": f"Bearer {token}"})
try:
    with urllib.request.urlopen(r, timeout=30) as resp:  # nosec B310 - localhost smoke
        ORGANIZER = json.loads(resp.read())["id"]
except Exception:
    ORGANIZER = None


def post(path, payload):
    data = json.dumps(payload).encode()
    r = urllib.request.Request(f"{BASE}/counseling/{path}", data=data, headers=H, method="POST")
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:  # nosec B310 - localhost smoke
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:500]


print(
    "workshop:",
    post(
        "workshops/",
        {
            "title": "DIAG Stress Mgmt",
            "description": "diag",
            "workshop_type": "stress",
            "status": "planned",
            "start_date": "2026-10-01",
            "start_time": "10:00",
            "organizer": ORGANIZER,
        },
    ),
)
print("provider:", post("providers/", {"name": "DIAG Associates", "provider_type": "therapist", "status": "active"}))
print("survey:", post("surveys/", {"title": "DIAG Feedback", "survey_type": "satisfaction", "status": "draft"}))

# get a student for the sel-goal probe
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
    print(
        "sel-goal:",
        post(
            "sel-goals/",
            {
                "student": sid,
                "goal_description": "DIAG goal",
                "domain": "self_awareness",
                "status": "active",
                "start_date": "2026-10-01",
            },
        ),
    )
