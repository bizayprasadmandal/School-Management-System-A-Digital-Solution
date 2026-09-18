"""Cross-module revenue posting: transport and hostel fee payments hit the books.

The fees module's ledger owns the audit trail (TransactionLog + AccountingEntry).
Transport ``record-payment`` and hostel fee payment creation both call
``post_revenue`` — these tests pin the trail: one credit entry, one log row,
idempotent, and tenant-safe.
"""

import uuid
from datetime import date
from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

TRANSPORT_FEES = f"{API_PREFIX}/transport/fees/"
HOSTEL_FEE_PAYMENTS = f"{API_PREFIX}/hostel/hostel-fee-payment/"
INVENTORY_INVOICE_PAYMENTS = f"{API_PREFIX}/inventory/invoice-payment/"


@pytest.fixture
def school(db):
    from tests.factories import SchoolFactory

    return SchoolFactory(code="XMS")


@pytest.fixture
def admin(db, school):
    from tests.factories import AdminUserFactory

    return AdminUserFactory(school=school)


@pytest.fixture
def admin_client(db, admin):
    c = APIClient()
    c.force_authenticate(user=admin)
    return c


def _make_transport_fee(school, student, amount="1500.00"):
    from services.transportation.models import TransportFee

    return TransportFee.objects.create(
        school=school,
        student=student,
        fee_type=TransportFee.FeeType.MONTHLY,
        amount=Decimal(amount),
        due_date=date.today(),
        status=TransportFee.Status.PENDING,
    )


def _make_hostel_payment(school, student, amount="3000.00"):
    from services.hostel.models import Hostel, HostelAllocation, HostelFeePayment, HostelRoom

    hostel = Hostel.objects.create(school=school, name="Ledger Hall", gender="coed")
    room = HostelRoom.objects.create(hostel=hostel, room_number="101", capacity=2)
    allocation = HostelAllocation.objects.create(student=student, room=room, check_in_date=date.today())
    return HostelFeePayment.objects.create(
        school=school,
        allocation=allocation,
        amount_due=Decimal(amount),
        amount_paid=Decimal(amount),
        status=HostelFeePayment.Status.PAID,
        payment_method="cash",
        due_date=date.today(),
        payment_date=date.today(),
    )


@pytest.mark.django_db
class TestTransportFeePaymentPosting:
    def test_record_payment_posts_to_books(self, admin_client, school):
        from services.fees.models import AccountingEntry, TransactionLog
        from tests.factories import StudentFactory

        fee = _make_transport_fee(school, StudentFactory(school=school))
        r = admin_client.post(
            f"{TRANSPORT_FEES}{fee.id}/record-payment/",
            {"amount": "800.00", "payment_method": "cash"},
            format="json",
        )
        assert r.status_code == status.HTTP_200_OK
        assert r.data["paid_amount"] == "800.00"
        assert r.data["status"] == "pending"  # partial payment stays pending

        entry = AccountingEntry.objects.get(reference_type="transport_fee", reference_id=str(fee.id))
        assert entry.entry_type == "credit"
        assert entry.amount == Decimal("800.00")
        assert entry.account_code == "4000"

        log = TransactionLog.objects.get(transaction_id=f"TRANSPORT_FEE-{fee.id}")
        assert log.amount == Decimal("800.00")
        assert log.status == "success"

    def test_full_payment_marks_paid_once(self, admin_client, school):
        from services.fees.models import AccountingEntry, TransactionLog
        from tests.factories import StudentFactory

        fee = _make_transport_fee(school, StudentFactory(school=school), amount="500.00")
        r1 = admin_client.post(f"{TRANSPORT_FEES}{fee.id}/record-payment/", {"amount": "500.00"}, format="json")
        assert r1.status_code == status.HTTP_200_OK
        assert r1.data["status"] == "paid"

        # Idempotent audit: a second POST with the same reference cannot double-post
        # (the fee is paid now, so this attempt is rejected outright)
        r2 = admin_client.post(f"{TRANSPORT_FEES}{fee.id}/record-payment/", {"amount": "100.00"}, format="json")
        assert r2.status_code == status.HTTP_400_BAD_REQUEST
        assert AccountingEntry.objects.filter(reference_type="transport_fee", reference_id=str(fee.id)).count() == 1
        assert TransactionLog.objects.filter(transaction_id=f"TRANSPORT_FEE-{fee.id}").count() == 1

    def test_record_payment_validates_amount(self, admin_client, school):
        from tests.factories import StudentFactory

        fee = _make_transport_fee(school, StudentFactory(school=school))
        for payload in ({}, {"amount": "0"}, {"amount": "-5"}, {"amount": "abc"}):
            r = admin_client.post(f"{TRANSPORT_FEES}{fee.id}/record-payment/", payload, format="json")
            assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_record_payment_tenant_isolation(self, db):
        from tests.factories import AdminUserFactory, SchoolFactory, StudentFactory

        school_a = SchoolFactory(code="TPA1")
        school_b = SchoolFactory(code="TPB1")
        fee_b = _make_transport_fee(school_b, StudentFactory(school=school_b))
        admin_a = AdminUserFactory(school=school_a)
        c = APIClient()
        c.force_authenticate(user=admin_a)
        r = c.post(f"{TRANSPORT_FEES}{fee_b.id}/record-payment/", {"amount": "10.00"}, format="json")
        assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestHostelFeePaymentPosting:
    def test_paid_payment_posts_to_books(self, admin_client, school):
        """Creating a paid payment through the API posts revenue + audit trail."""
        from services.fees.models import AccountingEntry, TransactionLog
        from services.hostel.models import Hostel, HostelAllocation, HostelRoom
        from tests.factories import StudentFactory

        student = StudentFactory(school=school)
        hostel = Hostel.objects.create(school=school, name="API Hall", gender="coed")
        room = HostelRoom.objects.create(hostel=hostel, room_number="201", capacity=2)
        allocation = HostelAllocation.objects.create(student=student, room=room, check_in_date=date.today())
        r = admin_client.post(
            HOSTEL_FEE_PAYMENTS,
            {
                "allocation": str(allocation.id),
                "amount_due": "3000.00",
                "amount_paid": "3000.00",
                "status": "paid",
                "payment_method": "cash",
                "due_date": date.today().isoformat(),
                "payment_date": date.today().isoformat(),
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED, r.data
        payment_id = r.data["id"]

        entry = AccountingEntry.objects.get(reference_type="hostel_fee_payment", reference_id=str(payment_id))
        assert entry.entry_type == "credit"
        assert entry.amount == Decimal("3000.00")
        assert entry.account_code == "4000"
        log = TransactionLog.objects.get(transaction_id=f"HOSTEL_FEE_PAYMENT-{payment_id}")
        assert log.student == student

    def test_updating_payment_to_paid_posts_once(self, admin_client, school):
        """Marking a pending payment paid via PATCH posts the trail exactly once."""
        from services.fees.models import AccountingEntry
        from tests.factories import StudentFactory

        payment = _make_hostel_payment(school, StudentFactory(school=school))
        payment.status = "pending"
        payment.amount_paid = Decimal("0")
        payment.save()

        r = admin_client.patch(
            f"{HOSTEL_FEE_PAYMENTS}{payment.id}/",
            {"status": "paid", "amount_paid": "3000.00"},
            format="json",
        )
        assert r.status_code == status.HTTP_200_OK, r.data
        assert (
            AccountingEntry.objects.filter(reference_type="hostel_fee_payment", reference_id=str(payment.id)).count()
            == 1
        )

    def test_pending_payment_does_not_post(self, db, school):
        from services.fees.models import AccountingEntry
        from services.hostel.models import HostelFeePayment
        from tests.factories import StudentFactory

        student = StudentFactory(school=school)
        payment = _make_hostel_payment(school, student)
        payment.status = HostelFeePayment.Status.PENDING
        payment.amount_paid = Decimal("0")
        payment.save()
        assert AccountingEntry.objects.filter(reference_type="hostel_fee_payment").count() == 0
        assert payment.status == "pending"


@pytest.mark.django_db
class TestSupplierInvoicePaymentPosting:
    def _make_invoice(self, school, total="1000.00"):
        from services.inventory.models import Invoice, Supplier

        supplier = Supplier.objects.create(school=school, name="PayLoop Supplier")
        return Invoice.objects.create(
            school=school,
            supplier=supplier,
            invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}",
            invoice_date=date.today(),
            due_date=date.today(),
            total=Decimal(total),
        )

    def test_payment_posts_debit_and_clears_invoice(self, admin_client, school):
        from services.fees.models import AccountingEntry, TransactionLog

        invoice = self._make_invoice(school)
        r = admin_client.post(
            INVENTORY_INVOICE_PAYMENTS,
            {
                "invoice": str(invoice.id),
                "payment_date": date.today().isoformat(),
                "amount": "400.00",
                "payment_method": "bank_transfer",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED, r.data
        payment_id = r.data["id"]

        entry = AccountingEntry.objects.get(reference_type="supplier_invoice_payment", reference_id=str(payment_id))
        assert entry.entry_type == "debit"
        assert entry.account_code == "2000"
        assert entry.amount == Decimal("400.00")

        log = TransactionLog.objects.get(transaction_id=f"SUPPLIER_INVOICE_PAYMENT-{payment_id}")
        assert log.amount == Decimal("400.00")

        invoice.refresh_from_db()
        assert invoice.amount_paid == Decimal("400.00")
        assert invoice.status == "partial"

    def test_full_payment_marks_invoice_paid(self, admin_client, school):
        invoice = self._make_invoice(school, total="600.00")
        r = admin_client.post(
            INVENTORY_INVOICE_PAYMENTS,
            {
                "invoice": str(invoice.id),
                "payment_date": date.today().isoformat(),
                "amount": "600.00",
                "payment_method": "cash",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        invoice.refresh_from_db()
        assert invoice.status == "paid"

    def test_tenant_isolation(self, db):
        from services.inventory.models import Invoice, Supplier
        from tests.factories import AdminUserFactory, SchoolFactory

        school_a = SchoolFactory(code="PLA1")
        school_b = SchoolFactory(code="PLB1")
        supplier_b = Supplier.objects.create(school=school_b, name="Other Supplier")
        invoice_b = Invoice.objects.create(
            school=school_b,
            supplier=supplier_b,
            invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}",
            invoice_date=date.today(),
            due_date=date.today(),
            total=Decimal("500.00"),
        )
        admin_a = AdminUserFactory(school=school_a)
        c = APIClient()
        c.force_authenticate(user=admin_a)
        r = c.post(
            INVENTORY_INVOICE_PAYMENTS,
            {
                "invoice": str(invoice_b.id),
                "payment_date": date.today().isoformat(),
                "amount": "100.00",
                "payment_method": "cash",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST


HR_PAYSLIPS = f"{API_PREFIX}/hr/payslips/"


def _make_payslip(school, amount="45000.00"):
    """An approved payslip ready to be marked paid."""
    from services.hr.models import Department, Employee, Payslip
    from tests.factories import UserFactory

    emp_user = UserFactory(school=school, role="teacher", email=f"pay-{uuid.uuid4().hex[:6]}@school.edu")
    dept = Department.objects.create(school=school, name="Payroll Dept", code=f"PD{uuid.uuid4().hex[:4]}")
    emp = Employee.objects.create(
        school=school,
        user=emp_user,
        department=dept,
        employee_id=f"EMP-{uuid.uuid4().hex[:6].upper()}",
        designation="Teacher",
        joining_date=date.today(),
    )
    return Payslip.objects.create(
        school=school,
        employee=emp,
        period_start=date.today().replace(day=1),
        period_end=date.today(),
        basic_salary=Decimal(amount),
        gross_pay=Decimal(amount),
        total_deductions=Decimal("0.00"),
        net_pay=Decimal(amount),
        status=Payslip.Status.APPROVED,
    )


@pytest.mark.django_db
class TestPayrollPosting:
    """Marking a payslip paid posts the salary expense to the shared ledger."""

    def test_mark_paid_posts_debit_entry_and_log(self, admin_client, school):
        from services.fees.models import AccountingEntry, TransactionLog

        payslip = _make_payslip(school)
        r = admin_client.post(f"{HR_PAYSLIPS}{payslip.id}/mark-paid/", {}, format="json")
        assert r.status_code == status.HTTP_200_OK

        entry = AccountingEntry.objects.get(reference_type="payslip", reference_id=str(payslip.id))
        assert entry.entry_type == AccountingEntry.EntryType.DEBIT
        assert entry.amount == payslip.net_pay
        assert entry.account_code == "5001"
        log = TransactionLog.objects.get(transaction_id=f"PAYSLIP-{payslip.id}")
        assert log.school == school

    def test_mark_paid_is_idempotent(self, admin_client, school):
        from services.fees.models import AccountingEntry

        payslip = _make_payslip(school)
        r = admin_client.post(f"{HR_PAYSLIPS}{payslip.id}/mark-paid/", {}, format="json")
        assert r.status_code == status.HTTP_200_OK
        # A retried mark-paid is rejected by the state guard (already paid)…
        r2 = admin_client.post(f"{HR_PAYSLIPS}{payslip.id}/mark-paid/", {}, format="json")
        assert r2.status_code == status.HTTP_400_BAD_REQUEST
        # …and even a direct double-post of the same reference never duplicates.
        from services.fees.ledger import post_revenue
        from services.fees.models import TransactionLog

        post_revenue(
            school=school,
            amount=payslip.net_pay,
            reference_type="payslip",
            reference_id=str(payslip.id),
            description="retry",
            entry_type=AccountingEntry.EntryType.DEBIT,
            account_code="5001",
            account_name="Salary Expense",
            transaction_type=TransactionLog.TransactionType.OTHER,
        )
        assert AccountingEntry.objects.filter(reference_type="payslip", reference_id=str(payslip.id)).count() == 1

    def test_draft_payslip_never_posts(self, admin_client, school):
        from services.fees.models import AccountingEntry
        from services.hr.models import Payslip

        payslip = _make_payslip(school)
        payslip.status = Payslip.Status.DRAFT
        payslip.save(update_fields=["status"])
        r = admin_client.post(f"{HR_PAYSLIPS}{payslip.id}/mark-paid/", {}, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert not AccountingEntry.objects.filter(reference_type="payslip", reference_id=str(payslip.id)).exists()

    def test_tenant_isolation(self, db):
        from services.fees.models import AccountingEntry
        from tests.factories import AdminUserFactory, SchoolFactory

        school_a = SchoolFactory(code="PAYA")
        school_b = SchoolFactory(code="PAYB")
        payslip_b = _make_payslip(school_b)
        admin_a = AdminUserFactory(school=school_a)
        c = APIClient()
        c.force_authenticate(user=admin_a)
        r = c.post(f"{HR_PAYSLIPS}{payslip_b.id}/mark-paid/", {}, format="json")
        assert r.status_code == status.HTTP_404_NOT_FOUND
        assert not AccountingEntry.objects.filter(reference_type="payslip").exists()
