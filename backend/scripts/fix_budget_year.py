"""Align the demo school's budget data with its payroll data.

The payroll-budget card compares payslips inside the *current* academic
year against that year's salary budget lines. The demo seed left:
- AY 2024-2025 marked current while all payslips are 2026-period
- several faker-named draft BudgetPlans ("Shake Indicate 1", ...)

This patch (rerunnable) creates/marks an AY covering the payslip periods,
gives it an active budget plan with realistic salary lines, and removes
the word-salad draft plans so the Payroll vs budget card reads cleanly.
"""

import os
import sys
from datetime import date
from decimal import Decimal

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from services.fees.models import BudgetLineItem, BudgetPlan  # noqa: E402
from services.hr.models import Payslip  # noqa: E402
from services.students.models import AcademicYear  # noqa: E402

SCHOOL_NAMES = ["Green Valley"]

for school_name in SCHOOL_NAMES:
    school = Payslip.objects.filter(school__name__icontains=school_name).values_list("school", flat=True).first()
    if school is None:
        print(f"no school matching {school_name!r} with payslips — skipping")
        continue

    from services.auth.models import School  # noqa: E402

    school = School.objects.get(pk=school)
    print(f"== {school.name} ==")

    # 1. Remove faker-named draft plans (keep the real "Budget Plan ..." one).
    real = BudgetPlan.objects.filter(school=school, title__startswith="Budget Plan").values_list("id", flat=True)
    junk = BudgetPlan.objects.filter(school=school).exclude(id__in=list(real))
    count = junk.count()
    junk.delete()
    print(f"removed {count} faker draft plans")

    # 2. Ensure an AY that covers the payslip periods is current.
    first_period = (
        Payslip.objects.filter(school=school).order_by("period_start").values_list("period_start", flat=True).first()
    )
    if first_period is None:
        print("no payslips — nothing to align")
        continue
    year_start = date(first_period.year, 8, 1)
    year_end = date(first_period.year + 1, 7, 31)
    ay_name = f"{first_period.year}-{first_period.year + 1}"
    ay, created = AcademicYear.objects.get_or_create(
        school=school,
        name=ay_name,
        defaults={"start_date": year_start, "end_date": year_end},
    )
    ay.is_current = True  # save() demotes other currents inside a lock
    ay.start_date, ay.end_date = year_start, year_end
    ay.save()
    print(f"{'created' if created else 'updated'} AY {ay.name} as current ({year_start}..{year_end})")

    # 3. Active budget plan for that year with salary + overhead lines.
    plan, plan_created = BudgetPlan.objects.get_or_create(
        school=school,
        academic_year=ay,
        title=f"Budget Plan {ay.name}",
        defaults={
            "status": BudgetPlan.Status.ACTIVE,
            "total_budget": Decimal("5000000.00"),
            "allocated": Decimal("3600000.00"),
        },
    )
    if plan_created:
        lines = [
            ("Teacher Salaries", Decimal("2000000.00")),
            ("Staff Salaries", Decimal("800000.00")),
            ("Utilities", Decimal("300000.00")),
            ("Maintenance", Decimal("200000.00")),
            ("Supplies", Decimal("150000.00")),
            ("Technology", Decimal("150000.00")),
        ]
        total = Decimal("0")
        for desc, amount in lines:
            BudgetLineItem.objects.create(budget_plan=plan, description=desc, budgeted_amount=amount)
            total += amount
        plan.allocated = total
        plan.total_budget = total + Decimal("1400000.00")
        plan.save(update_fields=["allocated", "total_budget"])
        print(f"created plan {plan.title!r} with {len(lines)} lines (salary lines = 2,800,000)")
    else:
        print(f"plan {plan.title!r} already exists — leaving lines untouched")

print("done")
