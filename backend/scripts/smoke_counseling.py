"""Live smoke test for all counseling endpoints (run inside container)."""

import json
import os
import urllib.request

BASE = os.environ.get("BASE_URL", "http://localhost:8000/api/v1")

# login
login_data = json.dumps(
    {
        "email": os.environ.get("SMOKE_USER", "admin@demo.edusphere.school"),
        "password": os.environ.get("SMOKE_PASS", "admin123456"),
    }
).encode()
req = urllib.request.Request(f"{BASE}/auth/login/", data=login_data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310 - localhost smoke
    body = json.loads(resp.read())
token = body.get("access") or body.get("token") or body.get("key")
assert token, f"login failed: {body}"

SLUGS = [
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

ok, fail = 0, []
for slug in SLUGS:
    url = f"{BASE}/counseling/{slug}/"
    r = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:  # nosec B310 - localhost smoke
            code = resp.status
    except urllib.error.HTTPError as e:
        code = e.code
    if code == 200:
        ok += 1
    else:
        fail.append((slug, code))
        print("FAIL", slug, code)

print(f"OK {ok}/{len(SLUGS)}")
if fail:
    print("failures:", fail)
