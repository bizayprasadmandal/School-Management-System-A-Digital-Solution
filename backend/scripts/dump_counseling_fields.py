"""Dump counseling serializer fields via DRF OPTIONS metadata for the UI configs."""

import json
import urllib.request

BASE = "http://localhost:8000/api/v1"

login_data = json.dumps({"email": "admin@demo.edusphere.school", "password": "admin123456"}).encode()
req = urllib.request.Request(f"{BASE}/auth/login/", data=login_data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310 - localhost smoke
    token = json.loads(resp.read())["access"]

H = {"Authorization": f"Bearer {token}"}

endpoints = [
    "appointments",
    "referrals",
    "sessions",
    "intervention-plans",
    "intervention-goals",
    "screenings",
    "screening-responses",
    "crisis",
    "crisis-followups",
    "progress",
    "progress-milestones",
    "consent",
    "group-sessions",
    "group-attendance",
    "cases",
    "outcomes",
    "reports",
    "availability",
    "feedback",
    "academic-advising",
    "bullying-followups",
    "bullying-reports",
    "career-assessments",
    "career-goals",
    "case-notes",
    "college-applications",
    "contracts",
    "goal-tracking",
    "notifications",
    "session-logs",
    "surveys",
    "survey-responses",
    "waitlist",
    "workshops",
    "absences",
    "coverage",
    "counselor-profiles",
    "course-recommendations",
    "providers",
    "group-members",
    "peer-mentors",
    "peer-mentoring-sessions",
    "referral-tracking",
    "restorative-commitments",
    "restorative-sessions",
    "sel-assessments",
    "sel-goals",
    "session-attachments",
    "special-education-referrals",
    "workshop-registrations",
]

for ep in endpoints:
    req = urllib.request.Request(f"{BASE}/counseling/{ep}/", headers=H)  # nosec B310 - localhost smoke
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310 - localhost smoke
            data = json.loads(resp.read())
            rows = data.get("results", data) if isinstance(data, dict) else data
            if rows:
                f = list(rows[0].keys())
                print(f"{ep}: {f}")
            else:
                # OPTIONS for structure
                op = urllib.request.Request(f"{BASE}/counseling/{ep}/", headers=H, method="OPTIONS")
                with urllib.request.urlopen(op, timeout=30) as r2:  # nosec B310 - localhost smoke
                    meta = json.loads(r2.read())
                    actions = meta.get("actions", {}).get("POST", {})
                    print(f"{ep}: (empty) fields={list(actions.keys())}")
    except Exception as e:
        print(f"{ep}: ERROR {e}")
