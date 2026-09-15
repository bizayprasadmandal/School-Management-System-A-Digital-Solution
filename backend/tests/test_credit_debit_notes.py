"""Tests for CreditNote/DebitNote apply actions.

Applying a note must actually move the invoice balance: credit notes reduce
total_amount (never below zero), debit notes increase it. Each note applies
exactly once, writes one TransactionLog audit entry, and concurrent applies
serialize.
"""

from decimal import Decimal

import pytest
from rest_framework.test import APIClient
from services.fees.models import CreditNote, DebitNote, TransactionLog
from tests.factories import (
    AcademicYearFactory,
    AdminUserFactory,
    FeeInvoiceFactory,
    FeeStructureFactory,
    SchoolFactory,
    StudentFactory,
)


@pytest.mark.django_db
class TestCreditNoteApply:
    def _make_invoice(self, school, total=Decimal("500.00")):
        student = StudentFactory(school=school)
        return FeeInvoiceFactory(
            student=student,
            academic_year=AcademicYearFactory(school=school),
            fee_structure=FeeStructureFactory(school=school),
            base_amount=total,
            total_amount=total,
            status="partial",
            paid_amount=Decimal("100.00"),
        )

    def _note(self, invoice, amount=Decimal("150.00")):
        return CreditNote.objects.create(
            school=invoice.student.school,
            note_number=f"CN-TEST-{CreditNote.objects.count() + 1:04d}",
            student=invoice.student,
            invoice=invoice,
            amount=amount,
            reason="Billing correction",
            status=CreditNote.Status.ISSUED,
            issued_date=invoice.due_date,
        )

    def _post_apply(self, admin, note):
        client = APIClient()
        client.force_authenticate(user=admin)
        return client.post(f"/api/v1/fees/credit-note/{note.id}/apply/")

    def test_apply_reduces_invoice_total(self):
        school = SchoolFactory()
        admin = AdminUserFactory(school=school, is_staff=True)
        invoice = self._make_invoice(school)
        note = self._note(invoice, Decimal("150.00"))

        resp = self._post_apply(admin, note)

        assert resp.status_code == 200, resp.content
        invoice.refresh_from_db()
        assert invoice.total_amount == Decimal("350.00")
        assert invoice.outstanding_amount == Decimal("250.00")
        note.refresh_from_db()
        assert note.status == CreditNote.Status.APPLIED
        assert note.applied_date is not None

    def test_apply_writes_single_audit_entry(self):
        school = SchoolFactory()
        admin = AdminUserFactory(school=school, is_staff=True)
        invoice = self._make_invoice(school)
        note = self._note(invoice)

        self._post_apply(admin, note)

        logs = TransactionLog.objects.filter(transaction_id=f"CN-{note.id}")
        assert logs.count() == 1
        log = logs.get()
        assert log.transaction_type == TransactionLog.TransactionType.ADJUSTMENT
        assert log.reference_number == note.note_number

    def test_double_apply_rejected(self):
        school = SchoolFactory()
        admin = AdminUserFactory(school=school, is_staff=True)
        invoice = self._make_invoice(school)
        note = self._note(invoice)

        assert self._post_apply(admin, note).status_code == 200
        invoice.refresh_from_db()
        total_after_first = invoice.total_amount

        resp = self._post_apply(admin, note)
        assert resp.status_code == 400
        invoice.refresh_from_db()
        assert invoice.total_amount == total_after_first  # unchanged

    def test_credit_below_zero_rejected(self):
        school = SchoolFactory()
        admin = AdminUserFactory(school=school, is_staff=True)
        invoice = self._make_invoice(school, total=Decimal("100.00"))
        note = self._note(invoice, Decimal("150.00"))

        resp = self._post_apply(admin, note)

        assert resp.status_code == 400
        invoice.refresh_from_db()
        assert invoice.total_amount == Decimal("100.00")
        note.refresh_from_db()
        assert note.status == CreditNote.Status.ISSUED  # untouched

    def test_cross_tenant_apply_rejected(self):
        school = SchoolFactory()
        other_school = SchoolFactory()
        admin = AdminUserFactory(school=other_school, is_staff=True)
        invoice = self._make_invoice(school)
        note = self._note(invoice)

        resp = self._post_apply(admin, note)

        assert resp.status_code == 404  # queryset scoping hides foreign notes


@pytest.mark.django_db
class TestDebitNoteApply:
    def _make_invoice(self, school, total=Decimal("500.00")):
        student = StudentFactory(school=school)
        return FeeInvoiceFactory(
            student=student,
            academic_year=AcademicYearFactory(school=school),
            fee_structure=FeeStructureFactory(school=school),
            base_amount=total,
            total_amount=total,
            status="partial",
            paid_amount=Decimal("100.00"),
        )

    def _note(self, invoice, amount=Decimal("75.00")):
        return DebitNote.objects.create(
            school=invoice.student.school,
            note_number=f"DN-TEST-{DebitNote.objects.count() + 1:04d}",
            student=invoice.student,
            invoice=invoice,
            amount=amount,
            reason="Late penalty",
            status=DebitNote.Status.ISSUED,
            issued_date=invoice.due_date,
        )

    def _post_apply(self, admin, note):
        client = APIClient()
        client.force_authenticate(user=admin)
        return client.post(f"/api/v1/fees/debit-note/{note.id}/apply/")

    def test_apply_increases_invoice_total(self):
        school = SchoolFactory()
        admin = AdminUserFactory(school=school, is_staff=True)
        invoice = self._make_invoice(school)
        note = self._note(invoice, Decimal("75.00"))

        resp = self._post_apply(admin, note)

        assert resp.status_code == 200, resp.content
        invoice.refresh_from_db()
        assert invoice.total_amount == Decimal("575.00")
        note.refresh_from_db()
        assert note.status == DebitNote.Status.APPLIED

    def test_apply_writes_single_audit_entry(self):
        school = SchoolFactory()
        admin = AdminUserFactory(school=school, is_staff=True)
        invoice = self._make_invoice(school)
        note = self._note(invoice)

        self._post_apply(admin, note)

        logs = TransactionLog.objects.filter(transaction_id=f"DN-{note.id}")
        assert logs.count() == 1
        assert logs.get().transaction_type == TransactionLog.TransactionType.ADJUSTMENT

    def test_double_apply_rejected(self):
        school = SchoolFactory()
        admin = AdminUserFactory(school=school, is_staff=True)
        invoice = self._make_invoice(school)
        note = self._note(invoice)

        assert self._post_apply(admin, note).status_code == 200
        invoice.refresh_from_db()
        total_after_first = invoice.total_amount

        resp = self._post_apply(admin, note)
        assert resp.status_code == 400
        invoice.refresh_from_db()
        assert invoice.total_amount == total_after_first
