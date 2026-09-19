"""Live check of the payslip view-report endpoint (run inside container)."""

import json  # nosec B404
import os
import sys
import urllib.error  # noqa: S310
import urllib.request  # noqa: S310

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from services.auth.models import User  # noqa: E402

BASE = "http://localhost:8000/api/v1"

u = User.objects.filter(email="admin@greenvalley.edu").first()
login = urllib.request.Request(  # nosec B310
    f"{BASE}/auth/login/",
    data=json.dumps({"email": u.email, "password": "Admin@1234"}).encode(),
    headers={"Content-Type": "application/json"},
)
token = json.load(urllib.request.urlopen(login))["access"]  # nosec B310
r = urllib.request.Request(
    f"{BASE}/hr/payslips/view-report/", headers={"Authorization": f"Bearer {token}"}
)  # nosec B310
try:
    data = json.load(urllib.request.urlopen(r))  # nosec B310
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read().decode()[:200])
    sys.exit(1)
print("rows:", data["count"])
for row in data["results"][:5]:
    print(f'  {row["employee_name"]}: views={row["view_count"]} status={row["status"]} net={row["net_pay"]}')
