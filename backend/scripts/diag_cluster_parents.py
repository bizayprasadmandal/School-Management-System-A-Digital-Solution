"""Verify school FK on parent models used in scoping paths."""

import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django

django.setup()

from services import conferences, fees, reporting  # noqa: E402

PARENTS = [
    (
        "reporting",
        [
            "CustomReport",
            "KPIDefinition",
            "ReportHistory",
            "ReportFolder",
            "ReportSchedule",
            "ReportTemplate",
            "DashboardWidget",
        ],
    ),
    (
        "conferences",
        [
            "ConferenceBooking",
            "ConferenceType",
            "ConferenceSurvey",
            "ConferenceTemplate",
            "ConferenceLocation",
            "RecurringConference",
        ],
    ),
    ("fees", ["BudgetPlan"]),
]

for mod_name, names in PARENTS:
    mod = {"reporting": reporting, "conferences": conferences, "fees": fees}[mod_name]
    print(f"== {mod_name} ==")
    for name in names:
        m = getattr(mod.models, name, None)
        if m is None:
            print(f"  {name}: NOT FOUND")
            continue
        has_school = any(f.name == "school" for f in m._meta.get_fields())
        print(f"  {name}: school={has_school}")
