"""Smoke all health_clinic endpoints from inside the container.

Auth + probes go through urllib against the local dev server only.
"""

import json
import urllib.request

BASE = "http://localhost:8000/api/v1"

ENDPOINTS = [
    "records",
    "visits",
    "immunizations",
    "medication-logs",
    "forms",
    "form-submissions",
    "allergies",
    "chronic-conditions",
    "emergency-plans",
    "emergency-contacts",
    "screenings",
    "screening-results",
    "medication-inventory",
    "prescriptions",
    "notifications",
    "compliance",
    "nurse-schedule",
    "incidents",
    "referrals",
    "reports",
    "alerts",
    "education",
    "telehealth",
    "dental-record",
    "vision-record",
    "growth-chart",
    "vital-signs",
    "lab-result",
    "medical-history",
    "family-medical-history",
    "health-insurance-record",
    "vaccination-schedule",
    "health-assessment",
    "health-risk-assessment",
    "mental-health-record",
    "health-education-material",
    "health-campaign",
    "health-survey",
    "medical-equipment",
    "equipment-maintenance",
    "health-staff-training",
    "health-audit",
]


def _open(req):
    return urllib.request.urlopen(req, timeout=15)  # nosec


def post(url, payload, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    return _open(req)


def get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    return _open(req)


def main():
    login = post(
        f"{BASE}/auth/login/",
        {"email": "admin@demo.edusphere.school", "password": "admin123456"},
    )
    token = json.load(login).get("access", "")
    print("token len:", len(token))

    ok, bad = 0, 0
    for ep in ENDPOINTS:
        try:
            get(f"{BASE}/health/{ep}/?page_size=1", token)
            ok += 1
        except urllib.error.HTTPError as e:
            bad += 1
            print(f"FAIL {ep}: {e.code}")
        except Exception as e:  # noqa: BLE001
            bad += 1
            print(f"FAIL {ep}: {e}")
    print(f"OK: {ok}  BAD: {bad}")


if __name__ == "__main__":
    main()
