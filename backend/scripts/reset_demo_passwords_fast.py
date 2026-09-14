"""Bulk password reset: hash each role password once, then raw SQL updates.

Avoids per-user .save() (expensive signal side-effects) and per-user
hashing (746 hashes is minutes; 5 hashes is milliseconds).
"""

import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")
import django  # noqa: E402

django.setup()

from django.contrib.auth.hashers import make_password  # noqa: E402
from django.db import connection  # noqa: E402
from services.auth.models import School, User  # noqa: E402

skip_school_ids = list(
    School.objects.filter(name__in=["E2E Test School", "Test School 0"]).values_list("id", flat=True)
)

ROLE_PASSWORDS = [
    ("school_admin", "Admin@1234"),
    ("super_admin", "Admin@1234"),
    ("teacher", "Teacher@1234"),
    ("student", "Student@1234"),
    ("parent", "Parent@1234"),
    ("counselor", "Admin@1234"),
    ("librarian", "Admin@1234"),
    ("accountant", "Admin@1234"),
    ("alumni", "Alumni@1234"),
]

with connection.cursor() as cur:
    for role, pwd in ROLE_PASSWORDS:
        hashed = make_password(pwd)
        cur.execute(
            """
            UPDATE users
            SET password = %s
            WHERE role = %s
              AND (school_id IS NULL OR school_id::text <> ALL(%s::text[]))
              AND email NOT LIKE '%%gmail.com'
              AND email NOT LIKE '%%api.test%%'
              AND email NOT LIKE '%%formdata.test%%'
              AND email NOT LIKE '%%verifytest%%'
              AND password <> %s
            """,
            [hashed, role, [str(x) for x in skip_school_ids], hashed],
        )
        print(f"{role:<13} rows updated: {cur.rowcount}")

print("done")
