"""Live create tests for hr endpoints that had school/user blockers."""

import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from services.auth.models import User  # noqa: E402

BASE = "http://localhost:8000/api/v1"
EMAIL = "smoke@demo.edusphere.school"
PASS = "smoke123456"

login_data = json.dumps({"email": EMAIL, "password": PASS}).encode()
req = urllib.request.Request(  # nosec B310
    f"{BASE}/auth/login/", data=login_data, headers={"Content-Type": "application/json"}
)
token = json.loads(urllib.request.urlopen(req, timeout=30).read())["access"]  # nosec B310
HDR = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}


def post(path, payload):
    req = urllib.request.Request(f"{BASE}/hr/{path}", data=json.dumps(payload).encode(), headers=HDR)  # nosec B310
    try:
        resp = urllib.request.urlopen(req, timeout=30)  # nosec B310
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        return e.code, body


user = User.objects.get(email=EMAIL)

# school-scoped creates (school auto-set server-side)
tests = [
    (
        "policies/",
        {"title": "Smoke Policy", "policy_type": "general", "content": "test", "effective_date": "2026-09-01"},
    ),
    ("onboarding-checklists/", {"name": "Smoke Checklist", "role_type": "teacher"}),
    ("data-retention-policies/", {"name": "Smoke Retention", "data_type": "records", "retention_days": 365}),
    ("accountant-profiles/", {"employee_code": "SMOKE-ACC-1", "hire_date": "2026-09-01"}),
    ("performance-goals/", {"title": "Smoke Goal", "goal_type": "annual", "target_date": "2026-12-31"}),
    ("applicants/", {"first_name": "Smoke", "last_name": "Applicant", "email": "smoke.applicant@example.com"}),
    ("time-entries/", {"date": "2026-09-08", "hours_worked": "8.0"}),
    (
        "leave-requests/",
        {"leave_type": "annual", "start_date": "2026-09-10", "end_date": "2026-09-12", "reason": "smoke"},
    ),
]

for path, payload in tests:
    code, body = post(path, payload)
    mark = "OK " if code in (200, 201) else "!! "
    print(f"{mark}{code} {path} {'' if code in (200, 201) else body}")
