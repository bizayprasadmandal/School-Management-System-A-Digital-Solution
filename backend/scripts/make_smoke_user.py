"""Create or fetch a dedicated smoke user."""

import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django

django.setup()

from services.auth.models import School, User

u = User.objects.filter(email="smoke@demo.edusphere.school").first()
if not u:
    school = School.objects.first() or School.objects.create(name="Smoke School")
    u = User.objects.create_user(
        email="smoke@demo.edusphere.school",
        password="smoke123456",
        school=school,
        role="admin",
        is_staff=True,
    )
print("SMOKE_USER_READY", u.email, u.school_id)
