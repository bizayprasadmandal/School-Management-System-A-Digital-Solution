"""Live smoke test for all sports endpoints (run inside container)."""

import json
import os
import urllib.error
import urllib.request

BASE = os.environ.get("BASE_URL", "http://localhost:8000/api/v1")

login_data = json.dumps(
    {
        "email": os.environ.get("SMOKE_USER", "admin@demo.edusphere.school"),
        "password": os.environ.get("SMOKE_PASS", "admin123456"),
    }
).encode()
req = urllib.request.Request(  # nosec B310
    f"{BASE}/auth/login/", data=login_data, headers={"Content-Type": "application/json"}
)
token = json.loads(urllib.request.urlopen(req, timeout=30).read())["access"]  # nosec B310

HEADERS = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

ENDPOINTS = """sports teams team-members events achievements registrations attendance practices
statistics rosters lineups injuries medical-clearances equipment uniform-orders league-standings
communications photos fundraising sponsorships travel volunteers analytics referees
referee-assignments facility-bookings live-scores videos wearables development-plans tryouts
tryout-scores season-passes schedule-conflicts refunds compliance weather-alerts live-streams
suspensions tournament-brackets tournament-matches merchandise merchandise-orders insurance
eligibility-rules student-eligibility transfers season-archives badges badge-awards
leaderboards""".split()

ok, bad = [], []
for ep in ENDPOINTS:
    r = urllib.request.Request(f"{BASE}/sports/{ep}/", headers=HEADERS)  # nosec B310
    try:
        urllib.request.urlopen(r, timeout=30)  # nosec B310
        ok.append(ep)
    except urllib.error.HTTPError as e:
        bad.append((ep, e.code, e.read()[:200].decode(errors="replace")))
    except Exception as e:  # noqa: BLE001
        bad.append((ep, "ERR", str(e)[:200]))

print(f"OK: {len(ok)}  BAD: {len(bad)}")
for ep, code, msg in bad:
    print(f"  {code} /sports/{ep}/ :: {msg[:160]}")
