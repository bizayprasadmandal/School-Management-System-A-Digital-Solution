"""
One-off script: seeds today's attendance records and current-month fee payments
so the admin dashboard shows real numbers.

Run: python manage.py shell < seed_today_data.py
"""

from datetime import date, timedelta
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
import random
import sys

from services.auth.models import User, UserRole
from services.students.models import Student, Enrollment, AcademicYear
from services.attendance.models import AttendanceRecord
from services.fees.models import FeeInvoice, Payment

today = timezone.now().date()
yesterday = today - timedelta(days=1)

school_admin = User.objects.filter(role=UserRole.SCHOOL_ADMIN).first()
if not school_admin:
    print("ERROR: No school admin found")
    sys.exit(1)

school = school_admin.school
ay = AcademicYear.objects.filter(school=school, is_current=True).first()
if not ay:
    print("ERROR: No current academic year")
    sys.exit(1)

admin_user = school_admin
students = list(Student.objects.filter(school=school, is_active=True).select_related("user"))
teachers = list(User.objects.filter(school=school, role=UserRole.TEACHER))

print(f"Seeding today ({today}) and yesterday ({yesterday}) attendance for {len(students)} students...")

with transaction.atomic():
    today_created = 0
    for student in students:
        enrollment = Enrollment.objects.filter(
            student=student, academic_year=ay, is_active=True
        ).first()
        if not enrollment:
            continue

        r = random.random()
        if r < 0.80:
            status = "P"
            remarks = ""
        elif r < 0.88:
            status = "L"
            remarks = f"Arrived {random.randint(5, 20)} min late"
        elif r < 0.95:
            status = "A"
            remarks = random.choice(["Called in sick", "Family emergency", ""])
        elif r < 0.98:
            status = "E"
            remarks = "Prior intimation given"
        else:
            status = "H"
            remarks = "Left early"

        _, created = AttendanceRecord.objects.get_or_create(
            student=student, date=today,
            defaults={
                "classroom": enrollment.classroom,
                "academic_year": ay,
                "status": status,
                "recorded_by": random.choice(teachers) if teachers else admin_user,
                "remarks": remarks,
                "notified_guardian": status in ("A", "E"),
            },
        )
        if created:
            today_created += 1

    # Yesterday
    yesterday_created = 0
    for student in students:
        enrollment = Enrollment.objects.filter(
            student=student, academic_year=ay, is_active=True
        ).first()
        if not enrollment:
            continue

        r = random.random()
        if r < 0.82:
            status = "P"
            remarks = ""
        elif r < 0.90:
            status = "L"
            remarks = f"Arrived {random.randint(5, 20)} min late"
        elif r < 0.96:
            status = "A"
            remarks = random.choice(["Sick leave", "Medical appointment", ""])
        elif r < 0.99:
            status = "E"
            remarks = "Prior approved leave"
        else:
            status = "H"
            remarks = "Half day"

        _, created = AttendanceRecord.objects.get_or_create(
            student=student, date=yesterday,
            defaults={
                "classroom": enrollment.classroom,
                "academic_year": ay,
                "status": status,
                "recorded_by": random.choice(teachers) if teachers else admin_user,
                "remarks": remarks,
                "notified_guardian": status in ("A", "E"),
            },
        )
        if created:
            yesterday_created += 1

    # Current month payments
    current_month_start = today.replace(day=1)
    payments_created = 0
    invoices = FeeInvoice.objects.filter(
        student__school=school,
        status__in=["unpaid", "partial"],
    )[:100]

    for inv in invoices:
        pay_amt = inv.outstanding_amount
        if pay_amt <= 0:
            continue

        pay_method = random.choice(["cash", "bank_transfer", "card", "online", "mobile"])
        receipt_num = f"RCT-TODAY-{inv.student.admission_number}-{random.randint(100, 999)}"

        # Use sequence-based receipt number to avoid collisions
        from services.fees.models import Payment as P
        max_receipt = P.objects.filter(receipt_number__startswith="RCT-TODAY-").count()
        safe_receipt = f"RCT-TODAY-{inv.student.admission_number}-{payments_created + max_receipt + 1:04d}"

        Payment.objects.create(
            invoice=inv,
            amount=pay_amt,
            payment_method=pay_method,
            status="successful",
            receipt_number=safe_receipt,
            paid_at=current_month_start + timedelta(days=random.randint(0, max((today - current_month_start).days, 1))),
            collected_by=admin_user,
            notes="Bulk payment recorded",
        )
        payments_created += 1

        inv.paid_amount += pay_amt
        inv.status = "paid" if inv.paid_amount >= inv.total_amount else "partial"
        inv.save(update_fields=["paid_amount", "status"])

print(f"\nDone!")
print(f"  Today's attendance: {today_created} records")
print(f"  Yesterday's attendance: {yesterday_created} records")
print(f"  Current-month payments: {payments_created} records")

# Preview
present = AttendanceRecord.objects.filter(student__school=school, date=today, status__in=["P", "L"]).count()
total = AttendanceRecord.objects.filter(student__school=school, date=today).count()
pct = round(present / total * 100, 1) if total else 0
print(f"\n  Dashboard will show: {present}/{total} = {pct}% attendance today")
