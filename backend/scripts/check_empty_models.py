"""Trace why build_kwargs returns None for specific models."""

import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")
import django  # noqa: E402

django.setup()

from django.apps import apps  # noqa: E402
from services.auth.management.commands.seed_module_data import Command  # noqa: E402
from services.auth.models import School  # noqa: E402

gvs = School.objects.filter(name__icontains="green").first()
cmd = Command()
cmd.row_pool = {}
cmd.attempted = set()
cmd.force = False

# Simulate the pool preload for all modules of interest
POOL = [
    "sports",
    "health_clinic",
    "counseling",
    "communication",
    "admissions",
    "conferences",
    "fees",
    "attendance",
    "hr",
    "students",
    "academics",
    "timetable",
]
for app_label in POOL:
    try:
        for m in apps.get_app_config(app_label).get_models():
            qs = m.objects.all()
            if cmd.model_has_school(m):
                qs = qs.filter(school=gvs)
            rows = list(qs[:50])
            if rows:
                cmd.row_pool[m] = rows
    except LookupError:
        pass

print(f"pool has {len(cmd.row_pool)} model classes\n")

MODELS = [
    ("counseling", "CounselingAppointment"),
    ("conferences", "ConferenceAvailability"),
    ("hr", "Employee"),
    ("hr", "Department"),
    ("hr", "Payslip"),
    ("hr", "LeaveRequest"),
]
for app, mname in MODELS:
    try:
        M = apps.get_model(app, mname)
    except LookupError as e:
        print(f"{app}.{mname}: LOOKUP {e}")
        continue
    kw = cmd.build_kwargs(M, gvs, 0)
    if kw is not None:
        print(f"{app}.{mname}: OK (builds fine)")
        continue
    # find the blocking field
    blockers = []
    for f in M._meta.fields:
        if f.auto_created or f.primary_key or getattr(f, "null", False):
            continue
        if f.has_default() or getattr(f, "blank", False):
            continue
        if f.is_relation and f.related_model is not None:
            if f.name == "school":
                continue
            if f.related_model not in cmd.row_pool:
                blockers.append(f"{f.name} -> {f.related_model.__name__} (not in pool)")
    print(f"{app}.{mname}: BLOCKED by {blockers or ['unknown/non-FK field']}")
