"""Probe AYs + budget plans for greenvalley to explain the payroll-budget card."""

import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from services.fees.models import BudgetLineItem, BudgetPlan  # noqa: E402
from services.hr.models import Payslip  # noqa: E402
from services.students.models import AcademicYear  # noqa: E402

for school_name in ["Green Valley", "Springfield"]:
    qs_acs = AcademicYear.objects.filter(school__name__icontains=school_name)
    if not qs_acs.exists():
        continue
    school = qs_acs.first().school
    print(f"== {school.name} ==")
    for ay in qs_acs.order_by("-start_date"):
        print(f"  AY {ay.name} current={ay.is_current} {ay.start_date}..{ay.end_date}")
    for plan in BudgetPlan.objects.filter(school=school).select_related("academic_year"):
        print(f"  PLAN {plan.title} [{plan.status}] ay={plan.academic_year.name} total={plan.total_budget}")
        for li in plan.line_items.all():
            print(f"    LINE {li.description!r} budgeted={li.budgeted_amount} cat={li.category}")
    periods = Payslip.objects.filter(school=school).values_list("period_start", flat=True).distinct()[:5]
    print(f"  payslip periods sample: {sorted(set(str(p) for p in periods))[:5]}")
    print(f"  payslip count: {Payslip.objects.filter(school=school).count()}")
