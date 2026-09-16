"""
Seed finance & operations module with realistic fake data.

Usage:
    python manage.py seed_fees_data
    python manage.py seed_fees_data --clear   # clear existing fees data first
"""

import random
import uuid
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import models, transaction
from django.utils import timezone
from faker import Faker
from services.auth.models import School, User
from services.fees.models import (
    AccountingEntry,
    AdvancePayment,
    BudgetLineItem,
    BudgetPlan,
    CreditNote,
    DebitNote,
    ExpenseTracking,
    FeeAdjustment,
    FeeCategory,
    FeeCollectionDashboard,
    FeeConcession,
    FeeDiscount,
    FeeExemption,
    FeeInvoice,
    FeeStructure,
    FeeTemplate,
    FeeWaiver,
    FeeWaiverApproval,
    InstallmentPayment,
    InstallmentPlan,
    LateFeeRule,
    ParentAccount,
    Payment,
    PaymentGatewayConfig,
    PaymentReminder,
    RefundRecord,
    RevenueReport,
    Scholarship,
    SiblingDiscount,
    StudentFinancialAccount,
    StudentLedger,
    TransactionLog,
)
from services.students.models import AcademicYear, Enrollment, Grade, Student

fake = Faker()


class Command(BaseCommand):
    help = "Seed finance & operations module with realistic fake data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing fees data before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing fees data...")
            self._clear_data()

        self.stdout.write("Seeding finance & operations data...")
        with transaction.atomic():
            school = School.objects.first()
            if not school:
                self.stderr.write(self.style.ERROR("No school found. Run seed_demo_data first."))
                return

            admin_user = User.objects.filter(school=school, role="school_admin").first()
            accountant = User.objects.filter(school=school, role="accountant").first()
            if not admin_user:
                admin_user = User.objects.filter(school=school).first()
            if not accountant:
                accountant = admin_user

            academic_year = AcademicYear.objects.filter(school=school, is_current=True).first()
            if not academic_year:
                academic_year = AcademicYear.objects.filter(school=school).first()
            if not academic_year:
                self.stderr.write(self.style.ERROR("No academic year found. Run seed_demo_data first."))
                return

            grades = list(Grade.objects.filter(school=school))
            students = list(Student.objects.filter(school=school))
            if not students:
                self.stderr.write(self.style.ERROR("No students found. Run seed_demo_data first."))
                return

            enrollments = list(
                Enrollment.objects.filter(
                    student__school=school,
                    academic_year=academic_year,
                    is_active=True,
                )
            )

            self._seed_payment_gateway(school)
            self._seed_fee_categories(school)
            self._seed_fee_structures(school, academic_year, grades)
            self._seed_late_fee_rules(school)
            self._seed_fee_templates(school, admin_user)
            self._seed_discounts(school, grades)
            self._seed_invoices(school, academic_year, students, enrollments, admin_user)
            self._seed_payments(school, admin_user, accountant)
            self._seed_scholarships(school, academic_year, students, admin_user)
            self._seed_concessions(school, academic_year, students, admin_user)
            self._seed_waivers(school, academic_year, students, admin_user)
            self._seed_exemptions(school, students, admin_user)
            self._seed_adjustments(school, students, admin_user)
            self._seed_installment_plans(school, students, admin_user)
            self._seed_payment_reminders(school, students)
            self._seed_student_ledgers(school, academic_year, students)
            self._seed_student_accounts(school, students)
            self._seed_refunds(school, students, admin_user)
            self._seed_credit_debit_notes(school, students, admin_user)
            self._seed_expenses(school, admin_user)
            self._seed_budgets(school, academic_year, admin_user)
            self._seed_accounting_entries(school, admin_user)
            self._seed_transaction_logs(school, students)
            self._seed_reports(school, admin_user)

        self.stdout.write(self.style.SUCCESS("Finance & operations data seeded successfully!"))

    def _clear_data(self):
        models = [
            TransactionLog,
            AccountingEntry,
            BudgetLineItem,
            BudgetPlan,
            ExpenseTracking,
            DebitNote,
            CreditNote,
            RefundRecord,
            AdvancePayment,
            StudentFinancialAccount,
            ParentAccount,
            StudentLedger,
            PaymentReminder,
            InstallmentPayment,
            InstallmentPlan,
            FeeExemption,
            FeeWaiverApproval,
            FeeWaiver,
            FeeConcession,
            Scholarship,
            FeeAdjustment,
            Payment,
            FeeInvoice,
            FeeDiscount,
            SiblingDiscount,
            LateFeeRule,
            FeeTemplate,
            FeeStructure,
            FeeCategory,
            PaymentGatewayConfig,
            RevenueReport,
            FeeCollectionDashboard,
        ]
        for model in models:
            model.objects.all().delete()

    def _seed_payment_gateway(self, school):
        PaymentGatewayConfig.objects.get_or_create(
            school=school,
            defaults={
                "stripe_enabled": True,
                "khalti_enabled": True,
                "esewa_enabled": True,
            },
        )
        self.stdout.write("  Payment gateway config created")

    def _seed_fee_categories(self, school):
        categories = [
            ("Tuition Fee", True, True, "monthly"),
            ("Transport Fee", True, True, "monthly"),
            ("Library Fee", True, True, "annual"),
            ("Lab Fee", True, False, "one_time"),
            ("Sports Fee", True, True, "annual"),
            ("Exam Fee", True, False, "quarterly"),
            ("Activity Fee", False, True, "monthly"),
            ("Hostel Fee", False, True, "monthly"),
        ]
        created = 0
        for name, mandatory, recurring, recurrence in categories:
            _, was_created = FeeCategory.objects.get_or_create(
                school=school,
                name=name,
                defaults={
                    "description": f"Fee for {name.lower()}",
                    "is_mandatory": mandatory,
                    "is_recurring": recurring,
                    "recurrence": recurrence,
                },
            )
            if was_created:
                created += 1
        self.stdout.write(f"  {created} fee categories created")

    def _seed_fee_structures(self, school, academic_year, grades):
        categories = list(FeeCategory.objects.filter(school=school))
        amounts = {
            "Tuition Fee": (5000, 15000),
            "Transport Fee": (2000, 5000),
            "Library Fee": (500, 1500),
            "Lab Fee": (1000, 3000),
            "Sports Fee": (800, 2000),
            "Exam Fee": (1500, 4000),
            "Activity Fee": (300, 1000),
            "Hostel Fee": (8000, 20000),
        }
        created = 0
        for grade in grades:
            for cat in categories:
                min_amt, max_amt = amounts.get(cat.name, (1000, 5000))
                amount = Decimal(str(random.randint(min_amt, max_amt)))
                _, was_created = FeeStructure.objects.get_or_create(
                    school=school,
                    academic_year=academic_year,
                    grade=grade,
                    fee_category=cat,
                    defaults={
                        "amount": amount,
                        "due_day": random.choice([5, 10, 15]),
                        "late_fee_per_day": Decimal(str(random.randint(50, 200))),
                        "is_active": True,
                    },
                )
                if was_created:
                    created += 1
        self.stdout.write(f"  {created} fee structures created")

    def _seed_late_fee_rules(self, school):
        rules = [
            ("Early Reminder", 3, 0, "fixed", 0, 500),
            ("Standard Late Fee", 7, 100, "fixed", 0, 2000),
            ("Severe Late Fee", 15, 200, "fixed", 0, 5000),
            ("Percentage Penalty", 30, 0, "percentage", 5, 10000),
        ]
        created = 0
        for name, days, fee, ftype, pct, max_fee in rules:
            _, was_created = LateFeeRule.objects.get_or_create(
                school=school,
                name=name,
                defaults={
                    "days_after_due": days,
                    "fee_amount": Decimal(str(fee)),
                    "fee_type": ftype,
                    "percentage": Decimal(str(pct)),
                    "max_late_fee": Decimal(str(max_fee)),
                    "applies_to": "all",
                    "is_active": True,
                },
            )
            if was_created:
                created += 1
        self.stdout.write(f"  {created} late fee rules created")

    def _seed_fee_templates(self, school, admin_user):
        templates = [
            ("Monthly Tuition", "tuition", 8000, True, "monthly"),
            ("Annual Sports", "sports", 3000, False, "annual"),
            ("Quarterly Exam", "exam", 2500, False, "quarterly"),
            ("Transport Monthly", "transport", 3500, True, "monthly"),
            ("Lab Fee One-Time", "lab", 2000, False, "one_time"),
        ]
        created = 0
        for name, ttype, amount, recurring, recurrence in templates:
            _, was_created = FeeTemplate.objects.get_or_create(
                school=school,
                name=name,
                defaults={
                    "template_type": ttype,
                    "description": f"Template for {name.lower()}",
                    "default_amount": Decimal(str(amount)),
                    "is_recurring": recurring,
                    "recurrence": recurrence,
                    "is_mandatory": True,
                    "late_fee_per_day": Decimal("100"),
                    "is_active": True,
                    "created_by": admin_user,
                },
            )
            if was_created:
                created += 1
        self.stdout.write(f"  {created} fee templates created")

    def _seed_discounts(self, school, grades):
        # Fee discounts
        discounts = [
            ("Early Bird Discount", "percentage", 10, "all", None),
            ("Grade 1 Merit", "percentage", 15, "grade", grades[0] if grades else None),
            ("Flat Fee Reduction", "fixed", 500, "all", None),
        ]
        created = 0
        for name, dtype, value, applies, grade in discounts:
            _, was_created = FeeDiscount.objects.get_or_create(
                school=school,
                name=name,
                defaults={
                    "discount_type": dtype,
                    "value": Decimal(str(value)),
                    "applies_to": applies,
                    "grade": grade,
                    "start_date": timezone.now().date() - timedelta(days=30),
                    "end_date": timezone.now().date() + timedelta(days=180),
                    "is_active": True,
                },
            )
            if was_created:
                created += 1

        # Sibling discounts
        sibling_discounts = [
            ("Sibling 10% Off", "percent", 10, 2),
            ("Sibling 15% Off", "percent", 15, 3),
        ]
        for name, dtype, value, min_sib in sibling_discounts:
            _, was_created = SiblingDiscount.objects.get_or_create(
                school=school,
                name=name,
                defaults={
                    "discount_type": dtype,
                    "discount_value": Decimal(str(value)),
                    "min_siblings": min_sib,
                    "is_active": True,
                    "priority": 10 if min_sib == 2 else 20,
                },
            )
            if was_created:
                created += 1
        self.stdout.write(f"  {created} discounts created")

    def _seed_invoices(self, school, academic_year, students, enrollments, admin_user):
        structures = list(FeeStructure.objects.filter(school=school, academic_year=academic_year))
        if not structures:
            return

        now = timezone.now().date()
        statuses = ["unpaid", "unpaid", "unpaid", "partial", "paid", "paid", "paid", "overdue"]
        invoices = []
        created = 0

        for student in students:
            # Generate 3-6 invoices per student
            num_invoices = random.randint(3, 6)
            for _ in range(num_invoices):
                structure = random.choice(structures)
                base_amount = structure.amount
                discount = Decimal(str(random.choice([0, 0, 0, 100, 200, 500])))
                total = base_amount - discount
                status = random.choice(statuses)
                paid = Decimal("0")
                if status == "paid":
                    paid = total
                elif status == "partial":
                    paid = total * Decimal(str(random.uniform(0.3, 0.7)))
                    paid = paid.quantize(Decimal("0.01"))

                due = now + timedelta(days=random.randint(-30, 60))
                inv = FeeInvoice(
                    invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}",
                    student=student,
                    academic_year=academic_year,
                    fee_structure=structure,
                    due_date=due,
                    base_amount=base_amount,
                    discount_amount=discount,
                    late_fee=Decimal(str(random.choice([0, 0, 0, 50, 100, 200]))),
                    total_amount=total,
                    paid_amount=paid,
                    status=status,
                    created_by=admin_user,
                )
                invoices.append(inv)
                created += 1

        FeeInvoice.objects.bulk_create(invoices, batch_size=500)
        self.stdout.write(f"  {created} invoices created")

    def _seed_payments(self, school, admin_user, accountant):
        invoices = list(FeeInvoice.objects.filter(student__school=school).exclude(status="paid"))
        methods = ["cash", "cash", "bank_transfer", "card", "khalti", "esewa", "online"]
        statuses = ["successful", "successful", "successful", "successful", "pending", "failed"]
        now = timezone.now()
        payments = []
        created = 0

        for inv in invoices[:200]:  # Limit to avoid too many
            outstanding = inv.total_amount - inv.paid_amount
            if outstanding <= 0:
                continue
            min_payment = min(Decimal("500"), outstanding)
            max_payment = outstanding
            amount = min(outstanding, Decimal(str(random.randint(int(min_payment), int(max_payment)))))
            method = random.choice(methods)
            pay_status = random.choice(statuses)
            paid_at = now - timedelta(days=random.randint(0, 30)) if pay_status == "successful" else None

            pay = Payment(
                invoice=inv,
                amount=amount,
                payment_method=method,
                status=pay_status,
                transaction_id=uuid.uuid4().hex[:16] if method in ["card", "online", "khalti", "esewa"] else "",
                gateway_response={"status": pay_status} if method in ["card", "online", "khalti", "esewa"] else {},
                receipt_number=f"RCPT-{uuid.uuid4().hex[:10].upper()}",
                paid_at=paid_at,
                collected_by=random.choice([admin_user, accountant]),
            )
            payments.append(pay)
            created += 1

        Payment.objects.bulk_create(payments, batch_size=500)

        # Update invoice paid amounts
        for inv in FeeInvoice.objects.filter(student__school=school):
            total_paid = inv.payments.filter(status="successful").aggregate(total=models.Sum("amount"))[
                "total"
            ] or Decimal("0")
            inv.paid_amount = total_paid
            if total_paid >= inv.total_amount:
                inv.status = "paid"
            elif total_paid > 0:
                inv.status = "partial"
            inv.save(update_fields=["paid_amount", "status"])

        self.stdout.write(f"  {created} payments created")

    def _seed_scholarships(self, school, academic_year, students, admin_user):
        scholarships = [
            ("Merit Scholarship", "percent", 20, "Top academic performer"),
            ("Sports Scholarship", "fixed", 5000, "Athletic excellence"),
            ("Need-Based Aid", "percent", 30, "Financial assistance"),
            ("Sibling Discount", "percent", 10, "Family enrolled"),
        ]
        students_sample = random.sample(students, min(30, len(students)))
        created = 0
        for student in students_sample:
            name, dtype, value, reason = random.choice(scholarships)
            _, was_created = Scholarship.objects.get_or_create(
                school=school,
                student=student,
                academic_year=academic_year,
                name=f"{name} - {student.user.first_name}",
                defaults={
                    "discount_type": dtype,
                    "discount_value": Decimal(str(value)),
                    "reason": reason,
                    "approved_by": admin_user,
                    "is_active": True,
                },
            )
            if was_created:
                created += 1
        self.stdout.write(f"  {created} scholarships created")

    def _seed_concessions(self, school, academic_year, students, admin_user):
        types = ["sibling", "staff_ward", "merit", "need_based", "sports"]
        students_sample = random.sample(students, min(20, len(students)))
        created = 0
        now = timezone.now().date()
        for student in students_sample:
            ctype = random.choice(types)
            _, was_created = FeeConcession.objects.get_or_create(
                school=school,
                student=student,
                academic_year=academic_year,
                name=f"{ctype.title()} Concession - {student.user.first_name}",
                defaults={
                    "concession_type": ctype,
                    "discount_type": random.choice(["percent", "fixed"]),
                    "discount_value": Decimal(str(random.choice([5, 10, 15, 500, 1000]))),
                    "max_amount": Decimal(str(random.choice([2000, 5000, 10000]))),
                    "status": random.choice(["approved", "approved", "pending"]),
                    "approved_by": admin_user,
                    "valid_from": now,
                    "valid_until": now + timedelta(days=365),
                    "reason": f"{ctype.title()} concession for student",
                },
            )
            if was_created:
                created += 1
        self.stdout.write(f"  {created} concessions created")

    def _seed_waivers(self, school, academic_year, students, admin_user):
        types = ["full", "partial", "category"]
        students_sample = random.sample(students, min(15, len(students)))
        created = 0
        now = timezone.now().date()
        for student in students_sample:
            wtype = random.choice(types)
            waiver = FeeWaiver.objects.create(
                school=school,
                student=student,
                academic_year=academic_year,
                waiver_type=wtype,
                amount=Decimal(str(random.choice([1000, 2000, 5000, 10000]))),
                status="approved",
                approved_by=admin_user,
                approved_at=timezone.now(),
                valid_from=now,
                valid_until=now + timedelta(days=365),
                reason="Special circumstance fee waiver",
            )
            FeeWaiverApproval.objects.create(
                school=school,
                waiver=waiver,
                approver=admin_user,
                status="approved",
                comments="Approved by admin",
                approved_date=timezone.now().date(),
            )
            created += 1
        self.stdout.write(f"  {created} waivers created")

    def _seed_exemptions(self, school, students, admin_user):
        structures = list(FeeStructure.objects.filter(school=school)[:10])
        students_sample = random.sample(students, min(10, len(students)))
        created = 0
        now = timezone.now().date()
        for student in students_sample:
            _, was_created = FeeExemption.objects.get_or_create(
                school=school,
                student=student,
                defaults={
                    "fee_structure": random.choice(structures) if structures else None,
                    "reason": "Fee exemption approved by administration",
                    "exemption_type": random.choice(["full", "partial"]),
                    "percentage": Decimal(str(random.choice([50, 75, 100]))),
                    "approved_by": admin_user,
                    "approved_date": now,
                    "valid_from": now,
                    "valid_to": now + timedelta(days=365),
                    "is_active": True,
                },
            )
            if was_created:
                created += 1
        self.stdout.write(f"  {created} exemptions created")

    def _seed_adjustments(self, school, students, admin_user):
        types = ["discount", "surcharge", "waiver", "penalty", "credit"]
        invoices = list(FeeInvoice.objects.filter(student__school=school)[:50])
        created = 0
        for inv in invoices:
            atype = random.choice(types)
            amount = Decimal(str(random.choice([100, 200, 500, 1000, -100, -200])))
            FeeAdjustment.objects.create(
                school=school,
                student=inv.student,
                invoice=inv,
                adjustment_type=atype,
                amount=amount,
                description=f"{atype.title()} adjustment applied",
                approved_by=admin_user,
                adjustment_date=timezone.now().date(),
            )
            created += 1
        self.stdout.write(f"  {created} adjustments created")

    def _seed_installment_plans(self, school, students, admin_user):
        invoices = list(FeeInvoice.objects.filter(student__school=school, status="unpaid")[:30])
        created = 0
        now = timezone.now().date()
        for inv in invoices:
            num_installments = random.choice([3, 4, 6])
            installment_amount = (inv.total_amount / num_installments).quantize(Decimal("0.01"))
            plan = InstallmentPlan.objects.create(
                school=school,
                student=inv.student,
                invoice=inv,
                total_amount=inv.total_amount,
                number_of_installments=num_installments,
                installment_amount=installment_amount,
                start_date=now,
                end_date=now + timedelta(days=30 * num_installments),
                status="active",
                late_fee_per_installment=Decimal("100"),
                grace_period_days=5,
                approved_by=admin_user,
            )
            for i in range(1, num_installments + 1):
                InstallmentPayment.objects.create(
                    installment_plan=plan,
                    installment_number=i,
                    amount=installment_amount,
                    due_date=now + timedelta(days=30 * i),
                    status=random.choice(["pending", "pending", "paid"]),
                )
            created += 1
        self.stdout.write(f"  {created} installment plans created")

    def _seed_payment_reminders(self, school, students):
        unpaid_invoices = list(FeeInvoice.objects.filter(student__school=school, status__in=["unpaid", "overdue"])[:50])
        types = ["email", "sms", "in_app"]
        created = 0
        now = timezone.now()
        for inv in unpaid_invoices:
            PaymentReminder.objects.create(
                school=school,
                invoice=inv,
                student=inv.student,
                reminder_type=random.choice(types),
                status=random.choice(["sent", "delivered", "pending"]),
                subject=f"Payment Reminder - Invoice {inv.invoice_number}",
                message=(
                    f"Dear parent, fee payment of Rs. {inv.outstanding_amount}"
                    f" is due for {inv.student.user.first_name}."
                ),
                scheduled_date=now.date() - timedelta(days=random.randint(0, 7)),
            )
            created += 1
        self.stdout.write(f"  {created} payment reminders created")

    def _seed_student_ledgers(self, school, academic_year, students):
        created = 0
        for student in students:
            invoices = FeeInvoice.objects.filter(student=student, academic_year=academic_year)
            balance = Decimal("0")
            ledger_entries = []
            for inv in invoices:
                balance += inv.total_amount
                ledger_entries.append(
                    StudentLedger(
                        school=school,
                        student=student,
                        academic_year=academic_year,
                        transaction_type="invoice",
                        amount=inv.total_amount,
                        balance_after=balance,
                        invoice=inv,
                        description=f"Invoice {inv.invoice_number} generated",
                        transaction_date=inv.created_at.date() if inv.created_at else timezone.now().date(),
                    )
                )
                payments = inv.payments.filter(status="successful")
                for pay in payments:
                    balance -= pay.amount
                    ledger_entries.append(
                        StudentLedger(
                            school=school,
                            student=student,
                            academic_year=academic_year,
                            transaction_type="payment",
                            amount=-pay.amount,
                            balance_after=balance,
                            payment=pay,
                            description=f"Payment {pay.receipt_number} received",
                            transaction_date=pay.paid_at.date() if pay.paid_at else timezone.now().date(),
                        )
                    )
            StudentLedger.objects.bulk_create(ledger_entries, batch_size=500)
            created += len(ledger_entries)
        self.stdout.write(f"  {created} ledger entries created")

    def _seed_student_accounts(self, school, students):
        created = 0
        for student in students:
            total_paid = Payment.objects.filter(invoice__student=student, status="successful").aggregate(
                total=models.Sum("amount")
            )["total"] or Decimal("0")
            total_outstanding = FeeInvoice.objects.filter(student=student).exclude(
                status__in=["paid", "waived", "cancelled"]
            ).aggregate(total=models.Sum(models.F("total_amount") - models.F("paid_amount")))["total"] or Decimal("0")

            StudentFinancialAccount.objects.get_or_create(
                student=student,
                school=school,
                defaults={
                    "account_type": "regular",
                    "balance": total_paid - total_outstanding,
                    "credit_limit": Decimal("50000"),
                    "total_paid": total_paid,
                    "total_outstanding": total_outstanding,
                    "is_active": True,
                },
            )
            created += 1
        self.stdout.write(f"  {created} student accounts created")

    def _seed_refunds(self, school, students, admin_user):
        successful_payments = list(Payment.objects.filter(invoice__student__school=school, status="successful")[:20])
        created = 0
        for pay in successful_payments:
            RefundRecord.objects.create(
                school=school,
                student=pay.invoice.student,
                payment=pay,
                invoice=pay.invoice,
                amount=pay.amount * Decimal(str(random.uniform(0.3, 1.0))).quantize(Decimal("0.01")),
                reason=random.choice(
                    [
                        "Student withdrew from school",
                        "Duplicate payment",
                        "Fee structure change",
                        "Scholarship applied retroactively",
                    ]
                ),
                status=random.choice(["pending", "approved", "processed"]),
                approved_by=admin_user,
            )
            created += 1
        self.stdout.write(f"  {created} refund records created")

    def _seed_credit_debit_notes(self, school, students, admin_user):
        students_sample = random.sample(students, min(15, len(students)))
        created = 0
        for student in students_sample:
            CreditNote.objects.create(
                school=school,
                note_number=f"CN-{uuid.uuid4().hex[:8].upper()}",
                student=student,
                amount=Decimal(str(random.choice([500, 1000, 2000, 3000]))),
                reason=random.choice(
                    [
                        "Overpayment correction",
                        "Fee structure adjustment",
                        "Promotional credit",
                    ]
                ),
                status="applied",
                issued_date=timezone.now().date(),
                issued_by=admin_user,
            )
            DebitNote.objects.create(
                school=school,
                note_number=f"DN-{uuid.uuid4().hex[:8].upper()}",
                student=student,
                amount=Decimal(str(random.choice([200, 500, 1000, 1500]))),
                reason=random.choice(
                    [
                        "Late fee applied",
                        "Additional charges",
                        "Penalty for damage",
                    ]
                ),
                status="applied",
                issued_date=timezone.now().date(),
                issued_by=admin_user,
            )
            created += 2

        # Open (draft/issued) notes linked to real invoices so the
        # apply-to-invoice workflow is demoable in the UI.
        open_invoices = FeeInvoice.objects.filter(school=school, status__in=["unpaid", "partial", "overdue"]).order_by(
            "?"
        )[:6]
        for invoice in open_invoices:
            for Model, prefix, reasons, amounts in (
                (
                    CreditNote,
                    "CN",
                    ["Overpayment correction", "Fee structure adjustment"],
                    [500, 1000],
                ),
                (
                    DebitNote,
                    "DN",
                    ["Late fee applied", "Additional charges"],
                    [200, 500],
                ),
            ):
                Model.objects.create(
                    school=school,
                    note_number=f"{prefix}-{uuid.uuid4().hex[:8].upper()}",
                    student=invoice.student,
                    invoice=invoice,
                    amount=Decimal(str(random.choice(amounts))),
                    reason=random.choice(reasons),
                    status="issued",
                    issued_date=timezone.now().date(),
                    issued_by=admin_user,
                )
                created += 1
        self.stdout.write(f"  {created} credit/debit notes created")

    def _seed_expenses(self, school, admin_user):
        expenses = [
            ("salary", "Teacher salaries - January", 500000),
            ("salary", "Staff salaries - January", 200000),
            ("utility", "Electricity bill", 25000),
            ("utility", "Internet service", 8000),
            ("maintenance", "Building repairs", 15000),
            ("supplies", "Office supplies", 5000),
            ("transport", "School bus fuel", 30000),
            ("event", "Annual day celebration", 50000),
            ("maintenance", "Playground equipment", 25000),
            ("utility", "Water supply", 10000),
        ]
        created = 0
        for etype, desc, amount in expenses:
            ExpenseTracking.objects.create(
                school=school,
                expense_type=etype,
                description=desc,
                amount=Decimal(str(amount)),
                vendor=fake.company(),
                invoice_number=fake.numerify("INV-####"),
                expense_date=timezone.now().date() - timedelta(days=random.randint(0, 60)),
                status=random.choice(["approved", "paid", "paid"]),
                approved_by=admin_user,
            )
            created += 1
        self.stdout.write(f"  {created} expenses created")

    def _seed_budgets(self, school, academic_year, admin_user):
        plan = BudgetPlan.objects.create(
            school=school,
            academic_year=academic_year,
            title=f"Budget Plan {academic_year.name}",
            total_budget=Decimal("5000000"),
            allocated=Decimal("4500000"),
            spent=Decimal("3200000"),
            status="active",
            approved_by=admin_user,
        )
        categories = list(FeeCategory.objects.filter(school=school))
        line_items = [
            ("Teacher Salaries", 2000000, 1800000),
            ("Staff Salaries", 800000, 750000),
            ("Utilities", 300000, 280000),
            ("Maintenance", 200000, 150000),
            ("Events & Activities", 250000, 200000),
            ("Supplies", 150000, 120000),
            ("Transport", 400000, 350000),
            ("Technology", 200000, 100000),
        ]
        for desc, budgeted, actual in line_items:
            BudgetLineItem.objects.create(
                budget_plan=plan,
                category=random.choice(categories) if categories else None,
                description=desc,
                budgeted_amount=Decimal(str(budgeted)),
                actual_amount=Decimal(str(actual)),
                variance=Decimal(str(budgeted - actual)),
            )
        self.stdout.write("  1 budget plan with 8 line items created")

    def _seed_accounting_entries(self, school, admin_user):
        entries = [
            ("debit", "1001", "Cash", "Tuition fee collection", 500000),
            ("credit", "4001", "Tuition Revenue", "Monthly tuition income", 500000),
            ("debit", "1002", "Bank Account", "Transport fee deposit", 150000),
            ("credit", "4002", "Transport Revenue", "Transport income", 150000),
            ("debit", "5001", "Salary Expense", "Teacher payroll", 500000),
            ("credit", "2001", "Salary Payable", "Pending salary", 500000),
        ]
        created = 0
        for etype, code, name, desc, amount in entries:
            AccountingEntry.objects.create(
                school=school,
                entry_type=etype,
                account_code=code,
                account_name=name,
                description=desc,
                amount=Decimal(str(amount)),
                entry_date=timezone.now().date() - timedelta(days=random.randint(0, 30)),
                created_by=admin_user,
            )
            created += 1
        self.stdout.write(f"  {created} accounting entries created")

    def _seed_transaction_logs(self, school, students):
        types = ["payment", "refund", "adjustment", "late_fee", "waiver"]
        statuses = ["success", "failed", "pending"]
        created = 0
        for _ in range(100):
            TransactionLog.objects.create(
                school=school,
                transaction_type=random.choice(types),
                transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
                student=random.choice(students) if random.random() > 0.2 else None,
                amount=Decimal(str(random.randint(100, 50000))),
                payment_method=random.choice(["cash", "card", "bank_transfer", "khalti", "esewa"]),
                reference_number=f"REF-{uuid.uuid4().hex[:8].upper()}",
                status=random.choice(statuses),
                description=fake.sentence(),
            )
            created += 1
        self.stdout.write(f"  {created} transaction logs created")

    def _seed_reports(self, school, admin_user):
        now = timezone.now()
        report_types = ["daily", "weekly", "monthly", "outstanding", "defaulters"]
        created = 0
        for i in range(10):
            rtype = random.choice(report_types)
            RevenueReport.objects.create(
                school=school,
                title=f"{rtype.title()} Revenue Report - {(now - timedelta(days=i*7)).strftime('%B %Y')}",
                report_type=rtype,
                status=random.choice(["generated", "sent", "archived"]),
                period_start=(now - timedelta(days=30 + i * 7)).date(),
                period_end=(now - timedelta(days=i * 7)).date(),
                total_collected=Decimal(str(random.randint(100000, 500000))),
                total_outstanding=Decimal(str(random.randint(50000, 200000))),
                total_refunded=Decimal(str(random.randint(0, 20000))),
                total_scholarships=Decimal(str(random.randint(10000, 50000))),
                generated_by=admin_user,
            )
            created += 1

        # Dashboard
        total_expected = FeeInvoice.objects.filter(student__school=school).aggregate(total=models.Sum("total_amount"))[
            "total"
        ] or Decimal("0")
        total_collected = Payment.objects.filter(invoice__student__school=school, status="successful").aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0")

        FeeCollectionDashboard.objects.create(
            school=school,
            total_expected=total_expected,
            total_collected=total_collected,
            total_outstanding=total_expected - total_collected,
            collection_percentage=(
                (total_collected / total_expected * 100).quantize(Decimal("0.01")) if total_expected > 0 else 0
            ),
            total_defaulters=FeeInvoice.objects.filter(student__school=school, status="overdue").count(),
        )
        self.stdout.write(f"  {created} reports + dashboard created")
