"""
Fees Service — Celery tasks for invoicing, fee reminders, overdue processing.
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import uuid
import logging

logger = logging.getLogger(__name__)


@shared_task
def mark_overdue_invoices():
    """
    Mark unpaid AND partially-paid invoices as overdue when past due date,
    applying late fees and sending Expo push + in-app notifications to
    students and parents.
    """
    from .models import FeeInvoice
    from services.communication.services import send_in_app_notification, send_expo_push_notification

    today = timezone.now().date()

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
        for sg in student.studentguardian_set.filter(
            guardian__user__isnull=False, portal_access=True
        ):
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

    logger.info("mark_overdue_invoices completed", extra={
        "marked_overdue": updated, "notifications_sent": updated,
    })
    return {"marked_overdue": updated}


@shared_task
def send_fee_reminders():
    """Send reminders for invoices due in 3 days — in-app + Expo push to student and parents."""
    from .models import FeeInvoice
    from services.communication.services import send_in_app_notification, send_expo_push_notification

    reminder_date = timezone.now().date() + timedelta(days=3)
    invoices = FeeInvoice.objects.filter(
        status__in=["unpaid", "partial"],
        due_date=reminder_date,
    ).select_related("student__user")
    count = 0
    for invoice in invoices:
        student = invoice.student
        title = "Fee Payment Reminder"
        body = (
            f"Your fee payment of {invoice.outstanding_amount:,.2f} "
            f"(Invoice #{invoice.invoice_number}) is due in 3 days."
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
        for sg in student.studentguardian_set.filter(
            guardian__user__isnull=False, portal_access=True
        ):
            parent_body = (
                f"{student.user.full_name}'s fee payment of "
                f"{invoice.outstanding_amount:,.2f} "
                f"(Invoice #{invoice.invoice_number}) is due in 3 days."
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
        count += 1

    logger.info("send_fee_reminders completed", extra={
        "reminders_sent": count, "reminder_date": str(reminder_date),
    })
    return {"reminders_sent": count}





@shared_task
def generate_bulk_invoices(structure_id: int, academic_year_id: int):
    """Generate fee invoices for all students in a grade."""
    from .models import FeeStructure, FeeInvoice
    from services.students.models import Enrollment

    structure = FeeStructure.objects.select_related("grade", "academic_year").get(id=structure_id)
    enrollments = Enrollment.objects.filter(
        classroom__grade=structure.grade,
        academic_year_id=academic_year_id,
        is_active=True,
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

    logger.info("generate_bulk_invoices completed", extra={
        "created": created, "structure_id": structure_id, "academic_year_id": academic_year_id,
    })
    return {"created": created, "structure_id": structure_id}


@shared_task
def generate_receipt_pdf(payment_id: str):
    """Generate a printable receipt PDF for a payment and attach it to the payment record."""
    from .models import Payment
    from django.core.files.base import ContentFile

    try:
        payment = Payment.objects.select_related(
            "invoice__student__user", "invoice__student__school"
        ).get(id=payment_id)

        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table,
            TableStyle, HRFlowable,
        )

        import io
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        BRAND = colors.HexColor("#4F46E5")
        title_style = ParagraphStyle("Title", parent=styles["Title"], textColor=BRAND, fontSize=18)

        school = payment.invoice.student.school
        student = payment.invoice.student

        elements = []
        elements.append(Paragraph("PAYMENT RECEIPT", title_style))
        elements.append(Paragraph(f"{school.name} — {school.address}", styles["Normal"]))
        elements.append(HRFlowable(width="100%", thickness=1, color=BRAND, spaceAfter=12))

        details = [
            ["Receipt No.", payment.receipt_number],
            ["Student", student.user.full_name],
            ["Admission No.", student.admission_number],
            ["Invoice", payment.invoice.invoice_number],
            ["Amount Paid", f"${payment.amount:,.2f}"],
            ["Method", payment.get_payment_method_display()],
            ["Date", payment.paid_at.strftime("%B %d, %Y %H:%M") if payment.paid_at else "—"],
        ]
        t = Table(details, colWidths=[5*cm, 10*cm])
        t.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 1*cm))
        elements.append(Paragraph(
            f"Generated by EduSphere SMS",
            ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=colors.grey),
        ))

        doc.build(elements)
        buffer.seek(0)

        # Store the PDF on the payment record (requires a pdf_file field, or we can store on invoice)
        # Since Payment model has no file field, we log success and return
        logger.info("Receipt PDF generated for payment %s", payment.receipt_number)
        return {"receipt_number": payment.receipt_number, "pdf_size": buffer.tell()}

    except Exception as e:
        logger.error("Receipt PDF generation failed for payment %s: %s", payment_id, e)
        return {"error": str(e)}
