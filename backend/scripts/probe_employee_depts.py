"""Check why seeded payslips group as Unassigned: employee.department state."""

import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from collections import Counter  # noqa: E402

from services.hr.models import Department, Employee, Payslip  # noqa: E402

print("== Departments per school ==")
for school in Department.objects.values_list("school__name", flat=True).distinct():
    depts = Department.objects.filter(school__name=school).values_list("name", flat=True)
    print(f"  {school}: {list(depts)}")

print("\n== Employees with/without department ==")
total = Employee.objects.count()
no_dept = Employee.objects.filter(department__isnull=True).count()
print(f"  total={total}, no_department={no_dept}")
for emp in Employee.objects.select_related("user", "department")[:15]:
    print(f"  {emp.user.email}: dept={emp.department.name if emp.department else None}")

print("\n== Payslips -> employee department ==")
counts = Counter()
for ps in Payslip.objects.select_related("employee__department")[:50]:
    key = ps.employee.department.name if ps.employee and ps.employee.department else "Unassigned"
    counts[key] += 1
print(f"  {dict(counts)}")
