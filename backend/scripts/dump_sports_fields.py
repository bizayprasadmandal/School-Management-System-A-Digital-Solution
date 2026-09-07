"""Dump serializer fields for all sports endpoints (run inside container)."""

import json
import urllib.request  # nosec B310

BASE = "http://localhost:8000/api/v1"
login = json.dumps({"email": "admin@demo.edusphere.school", "password": "admin123456"}).encode()
req = urllib.request.Request(  # nosec B310
    BASE + "/auth/login/", data=login, headers={"Content-Type": "application/json"}
)
token = json.loads(urllib.request.urlopen(req, timeout=30).read())["access"]  # nosec B310
H = {"Authorization": f"Bearer {token}"}

ENDPOINTS = """sports teams team-members events achievements registrations attendance practices
statistics rosters lineups injuries medical-clearances equipment uniform-orders league-standings
communications photos fundraising sponsorships travel volunteers analytics referees
referee-assignments facility-bookings live-scores videos wearables development-plans tryouts
tryout-scores season-passes schedule-conflicts refunds compliance weather-alerts live-streams
suspensions tournament-brackets tournament-matches merchandise merchandise-orders insurance
eligibility-rules student-eligibility transfers season-archives badges badge-awards
leaderboards""".split()

for ep in ENDPOINTS:
    try:
        r = urllib.request.Request(f"{BASE}/sports/{ep}/", headers=H)  # nosec B310
        data = json.loads(urllib.request.urlopen(r, timeout=30).read())  # nosec B310
        results = data.get("results", data if isinstance(data, list) else [])
        if results:
            fields = sorted(results[0].keys())
        else:
            fields = ["<no rows>"]
        print(f"{ep}: {fields}")
    except Exception as e:  # noqa: BLE001
        print(f"{ep}: ERROR {e}")
