"""Why are Book Reviews / Recommendations / ReportAccessControl / Wearables
tabs empty for Green Valley? Check row counts per tenant + live endpoints."""

import json
import os
import sys
import urllib.request

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from services.auth.models import School  # noqa: E402

gv = School.objects.filter(name__icontains="Green Valley").first()

# ── 1. model-level counts ────────────────────────────────────────────────────
from django.apps import apps  # noqa: E402

for label in (
    "library.BookReview",
    "library.BookRecommendation",
    "reporting.ReportAccessControl",
    "sports.SportsWearable",
    "sports.WearableData",
):
    try:
        m = apps.get_model(label)
    except LookupError:
        print(f"{label}: MODEL NOT FOUND")
        continue
    total = m._default_manager.count()
    fk_school = any(f.name == "school" for f in m._meta.fields if f.is_relation)
    gvc = m._default_manager.filter(school=gv).count() if fk_school else total
    print(f"{m._meta.label}: relations={[f.name for f in m._meta.fields if f.is_relation]}")
    print(f"    total={total} gv_direct={gvc}")

# ── 2. live endpoints ────────────────────────────────────────────────────────
login_data = json.dumps({"email": "bizaymndl@gmail.com", "password": "Admin@1234"}).encode()
req = urllib.request.Request(
    "http://localhost:8000/api/v1/auth/login/",
    data=login_data,
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(req, timeout=30) as r:  # nosec B310
    tok = json.load(r)["access"]

eps = [
    "library/book-reviews/",
    "library/book-recommendations/",
    "reporting/report-access-controls/",
    "sports/wearables/",
    "sports/wearable-devices/",
    "sports/wearable-data/",
]
for ep in eps:
    rq = urllib.request.Request(
        f"http://localhost:8000/api/v1/{ep}",
        headers={"Authorization": f"Bearer {tok}", "X-School-ID": "Green Valley"},
    )
    try:
        with urllib.request.urlopen(rq, timeout=30) as r:  # nosec B310
            body = json.load(r)
        count = body.get("count", "?") if isinstance(body, dict) else len(body)
        print(f"GET {ep} -> 200 count={count}")
    except Exception as exc:  # noqa: BLE001
        print(f"GET {ep} -> {exc}")
