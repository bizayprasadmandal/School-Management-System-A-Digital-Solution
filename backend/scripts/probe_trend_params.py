"""Probe the monthly_trend endpoint with different months params."""

import json
import os
import sys
import urllib.request  # noqa: S310

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from rest_framework_simplejwt.tokens import RefreshToken  # noqa: E402
from services.auth.models import User  # noqa: E402

u = User.objects.filter(email="admin@greenvalley.edu").first()
token = str(RefreshToken.for_user(u).access_token)

for q in ["?months=12", "?months=3", ""]:
    req = urllib.request.Request(
        f"http://localhost:8000/api/v1/fees/accounting-entry/monthly_trend/{q}",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        # nosec B310 — fixed https URL against the local dev server
        body = json.loads(urllib.request.urlopen(req, timeout=15).read())  # nosec B310
        print(f"{q or 'default'} -> {len(body['months'])} months: {body['months'][0]} .. {body['months'][-1]}")
    except Exception as e:  # noqa: BLE001
        print(f"{q or 'default'} ERROR: {e}")
