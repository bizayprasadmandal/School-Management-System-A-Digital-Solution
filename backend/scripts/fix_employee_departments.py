"""One-off demo-data repair: give employees real departments.

- Renames the faker-generated department names ("Campaign Loss 5-5" etc.)
  to a standard set so any department UI reads sensibly.
- Assigns every employee (currently department=None) a department,
  round-robin, so payslip grouping shows real groups.
"""

import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from services.hr.models import Department, Employee  # noqa: E402

STANDARD = [
    "Academics",
    "Administration",
    "Finance & Accounts",
    "Library",
    "IT & Maintenance",
    "Sports",
]

# Rename faker-named departments to the standard set, in stable pk order.
for i, dept in enumerate(Department.objects.order_by("pk")):
    real = STANDARD[i % len(STANDARD)]
    if dept.name != real:
        print(f"  rename dept pk={dept.pk}: {dept.name!r} -> {real!r}")
        dept.name = real
        dept.save(update_fields=["name"])

# Assign every department-less employee, round-robin over the school's depts.
fixed = 0
for school_id in Employee.objects.values_list("school_id", flat=True).distinct():
    depts = list(Department.objects.filter(school_id=school_id).order_by("pk"))
    if not depts:
        continue
    emps = Employee.objects.filter(school_id=school_id, department__isnull=True).order_by("pk")
    for idx, emp in enumerate(emps):
        emp.department = depts[idx % len(depts)]
        emp.save(update_fields=["department"])
        fixed += 1

print(f"assigned departments to {fixed} employees")
for emp in Employee.objects.select_related("department").order_by("pk"):
    print(f"  {emp.user.email}: {emp.department.name if emp.department else None}")
