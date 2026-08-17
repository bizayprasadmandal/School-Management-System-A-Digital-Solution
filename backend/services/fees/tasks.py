"""
Fees Service — Celery tasks for invoicing, fee reminders, overdue processing.
"""

import logging
import uuid
from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def mark_overdue_invoices(self):
    """
    Mark unpaid AND partially-paid invoices as overdue when past due date,
    applying late fees and sending Expo push + in-app notifications to
    students and parents.
    """
    from services.communication.services import send_expo_push_notification, send_in_app_notification

    from .models import FeeInvoice

    today = timezone.now().date()

    try:
        overdue = FeeInvoice.objects.filter(
            status__in=["unpaid", "partial"],
            due_date__lt=today,
        ).select_related("fee_structure", "student__user")

        updated = 0
        for invoice in overdue:
            days_overdue = (today - invoice.due_date).days
            late_fee = (
                invoice.fee_structure.late_fee_per_day * Decimal(str(days_overdue))
                if invoice.fee_structure and invoice.fee_structure.late_fee_per_day
                else Decimal("0")
            )
            invoice.status = "overdue"
            invoice.late_fee = late_fee
            invoice.total_amount = invoice.base_amount + late_fee - invoice.discount_amount
            invoice.save(update_fields=["status", "late_fee", "total_amount"])

            # ── Send notifications ────────────────────────────────────────────
            student = invoice.student
            title = "Fee Payment Overdue"
            body = (
                f"Your fee payment of {invoice.outstanding_amount:,.2f} "
                f"(Invoice #{invoice.invoice_number}) is now overdue by {days_overdue} day(s). "
                f"Late fee of {invoice.late_fee:,.2f} applied."
            )
            push_data = {
                "route": "Fees",
                "reference_type": "fee_invoice",
                "reference_id": str(invoice.id),
            }

            # Notify student
            send_in_app_notification.delay(
                user_id=str(student.user.id),
                title=title,
                body=body,
                reference_type="fee_invoice",
                reference_id=str(invoice.id),
            )
            send_expo_push_notification.delay(
                user_id=str(student.user.id),
                title=title,
                body=body,
                data=push_data,
            )

            # Notify parents
            for sg in student.studentguardian_set.filter(guardian__user__isnull=False, portal_access=True):
                parent_body = (
                    f"{student.user.full_name}'s fee payment of "
                    f"{invoice.outstanding_amount:,.2f} "
                    f"(Invoice #{invoice.invoice_number}) is overdue by {days_overdue} day(s)."
                )
                send_in_app_notification.delay(
                    user_id=str(sg.guardian.user.id),
                    title=title,
                    body=parent_body,
                    reference_type="fee_invoice",
                    reference_id=str(invoice.id),
                )
                send_expo_push_notification.delay(
                    user_id=str(sg.guardian.user.id),
                    title=title,
                    body=parent_body,
                    data=push_data,
                )

            updated += 1

        logger.info(
            "mark_overdue_invoices completed",
            extra={
                "marked_overdue": updated,
                "notifications_sent": updated,
            },
        )
        return {"marked_overdue": updated}
    except Exception as exc:
        logger.error("mark_overdue_invoices failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_fee_reminders(self, school_id=None):
    """
    Send reminders for invoices due in 3 days — routed through the standard
    "fee_due" notification template so every channel (email/SMS/push/in-app)
    renders consistently across all schools.

    school_id: optional — restrict to one school's invoices (used by tests to
    keep assertions isolated from other fixtures in the same database).
    """
    from services.communication.models import Notification, NotificationTemplate
    from services.communication.services import NotificationService

    from .models import FeeInvoice

    reminder_date = timezone.now().date() + timedelta(days=3)

    try:
        invoices = FeeInvoice.objects.filter(
            status__in=["unpaid", "partial"],
            due_date=reminder_date,
        ).select_related("student__user", "student__school")
        if school_id is not None:
            invoices = invoices.filter(student__school_id=school_id)
        count = 0
        for invoice in invoices:
            # Never double-remind: skip if an in-app reminder already exists for this invoice.
            if Notification.objects.filter(
                reference_type="fee_invoice",
                reference_id=str(invoice.id),
                channel="in_app",
                title="Fee Reminder",
            ).exists():
                continue

            student = invoice.student
            template = NotificationTemplate.objects.filter(
                school=student.school, event_type="fee_due", is_active=True
            ).first()
            context = {
                "student_name": student.user.full_name,
                "amount": f"{invoice.outstanding_amount:,.2f}",
                "due_date": invoice.due_date.strftime("%B %d, %Y"),
            }

            # Notify student + parents using each user's notification preferences.
            users = [student.user] + [g.user for g in student.guardians.filter(user__isnull=False)]
            for user in users:
                NotificationService.send(
                    user=user,
                    template=template,
                    context=context,
                    reference_type="fee_invoice",
                    reference_id=str(invoice.id),
                )
            count += 1

        logger.info(
            "send_fee_reminders completed",
            extra={
                "reminders_sent": count,
                "reminder_date": str(reminder_date),
            },
        )
        return {"reminders_sent": count}
    except Exception as exc:
        logger.error("send_fee_reminders failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_bulk_invoices(self, structure_id: int, academic_year_id: int):
    """Generate fee invoices for all students in a grade."""
    from services.students.models import Enrollment

    from .models import FeeInvoice, FeeStructure

    structure = FeeStructure.objects.select_related("grade", "academic_year").get(id=structure_id)

    try:
        # Defense in depth: even if the view-level checks are bypassed, only ever
        # generate invoices for students of the structure's own school — never for
        # enrollments that merely share a grade/academic_year with another tenant.
        enrollments = Enrollment.objects.filter(
            classroom__grade=structure.grade,
            academic_year_id=academic_year_id,
            is_active=True,
            student__school=structure.school,
        ).select_related("student")

        created = 0
        for enrollment in enrollments:
            due_date = structure.academic_year.start_date.replace(day=structure.due_day)
            _, new = FeeInvoice.objects.get_or_create(
                student=enrollment.student,
                fee_structure=structure,
                academic_year_id=academic_year_id,
                defaults={
                    "invoice_number": f"INV-{uuid.uuid4().hex[:8].upper()}",
                    "due_date": due_date,
                    "base_amount": structure.amount,
                    "total_amount": structure.amount,
                    "status": "unpaid",
                },
            )
            if new:
                created += 1

        logger.info(
            "generate_bulk_invoices completed",
            extra={
                "created": created,
                "structure_id": structure_id,
                "academic_year_id": academic_year_id,
            },
        )
        return {"created": created, "structure_id": structure_id}
    except Exception as exc:
        logger.error("generate_bulk_invoices failed: %s", exc)
        raise self.retry(exc=exc)
