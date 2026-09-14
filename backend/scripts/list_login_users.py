"""Dump all login-capable users grouped by school and role."""

import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")
import django  # noqa: E402

django.setup()

from collections import defaultdict  # noqa: E402

from services.auth.models import School, User  # noqa: E402

by_school = defaultdict(lambda: defaultdict(list))
for u in User.objects.select_related("school").order_by("school__name", "role", "email"):
    school = u.school.name if u.school else "(no school)"
    by_school[school][u.role].append(u.email)

for school, roles in by_school.items():
    print(f"\n=== {school} ===")
    for role, emails in sorted(roles.items()):
        print(f"  [{role}] ({len(emails)})")
        for e in emails[:12]:
            print(f"    {e}")
        if len(emails) > 12:
            print(f"    … and {len(emails) - 12} more")

print(f"\nTotal users: {User.objects.count()}")
print(f"Schools: {School.objects.count()}")
