"""Ensure a demo teacher exists with payslips for self-service verification."""

import os
import sys
from datetime import date
from decimal import Decimal

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from services.auth.models import School  # noqa: E402
from services.hr.models import Department, Employee, Payslip  # noqa: E402

User = get_user_model()

school = School.objects.filter(name="Green Valley School").first() or School.objects.first()

TEACHER_EMAIL = "payslip.demo@greenvalley.edu"
TEACHER_PASS = "Teacher@1234"

user = User.objects.filter(email=TEACHER_EMAIL).first()
if not user:
    user = User.objects.create_user(
        email=TEACHER_EMAIL,
        password=TEACHER_PASS,
        first_name="Pay",
        last_name="Slip",
        school=school,
        role="teacher",
    )
    user.email_verified = True
    user.save(update_fields=["email_verified"])
    print(f"created user {TEACHER_EMAIL}")
else:
    print(f"user exists: {TEACHER_EMAIL}")

dept = Department.objects.filter(school=school, name="Academics").first()

emp = Employee.objects.filter(user=user).first()
if not emp:
    emp = Employee.objects.create(
        school=school,
        user=user,
        department=dept,
        employee_id=f"{school.code}-EMP-901",
        designation="Teacher",
        employment_type=Employee.EmploymentType.FULL_TIME,
        status=Employee.Status.ACTIVE,
        joining_date=date(2024, 8, 1),
    )
    print("created employee record")

made = 0
for i, (start, end) in enumerate(
    [
        (date(2026, 7, 1), date(2026, 7, 31)),
        (date(2026, 8, 1), date(2026, 8, 31)),
        (date(2026, 9, 1), date(2026, 9, 30)),
    ]
):
    _, created = Payslip.objects.get_or_create(
        school=school,
        employee=emp,
        period_start=start,
        period_end=end,
        defaults=dict(
            basic_salary=Decimal("30000"),
            housing_allowance=Decimal("5000"),
            transport_allowance=Decimal("2000"),
            medical_allowance=Decimal("1000"),
            other_allowances=Decimal("0"),
            tax_deduction=Decimal("3000"),
            pension_deduction=Decimal("1500"),
            other_deductions=Decimal("500"),
            gross_pay=Decimal("38000"),
            total_deductions=Decimal("5000"),
            net_pay=Decimal("33000"),
            status="paid",
            payment_date=end,
            payment_method="bank_transfer",
        ),
    )
    made += 1 if created else 0
print(f"payslips ensured (new: {made})")
print(f"LOGIN: {TEACHER_EMAIL} / {TEACHER_PASS}")
