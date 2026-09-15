"""
Fees Service — Celery tasks for invoicing, fee reminders, overdue processing.
"""

import logging
from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


def _compute_rule_late_fee(invoice, rule) -> Decimal:
    """Late fee from a LateFeeRule: fixed amount or percentage of base, capped."""
    if rule.fee_type == "percentage":
        fee = (invoice.base_amount * rule.percentage / Decimal("100")).quantize(Decimal("0.01"))
    else:
        fee = rule.fee_amount
    if rule.max_late_fee > 0:
        fee = min(fee, rule.max_late_fee)
    return fee


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def mark_overdue_invoices(self):
    """
    Mark unpaid AND partially-paid invoices as overdue when past due date,
    applying late fees and sending Expo push + in-app notifications to
    students and parents.

    Late-fee source, per school:
    - Active LateFeeRule rows take precedence: the most severe rule whose
      ``days_after_due`` has already elapsed applies (fixed amount or
      percentage of the invoice base, capped by ``max_late_fee`` when set).
    - Schools without any rules fall back to the legacy per-day amount on
      the fee structure (``late_fee_per_day × days overdue``).

    The fee is computed once at the unpaid/partial → overdue transition,
    using the rule applicable on that day; an already-overdue invoice is
    never re-processed, so students get exactly one notification and the
    audit trail records the fee exactly once.
    """
    from services.communication.services import send_expo_push_notification, send_in_app_notification

    from .models import FeeInvoice, LateFeeRule, TransactionLog

    today = timezone.now().date()

    try:
        from django.db.models import Prefetch
        from services.students.models import StudentGuardian

        overdue = (
            FeeInvoice.objects.filter(
                status__in=["unpaid", "partial"],
                due_date__lt=today,
            )
            .select_related("fee_structure", "student__user", "student__school")
            .prefetch_related(
                Prefetch(
                    "student__studentguardian_set",
                    queryset=StudentGuardian.objects.filter(
                        guardian__user__isnull=False, portal_access=True
                    ).select_related("guardian__user"),
                    to_attr="active_guardians",
                )
            )
        )

        # Active rules grouped per school, most severe (largest
        # days_after_due) first — 1 query instead of one per invoice.
        rules_by_school: dict[int, list] = {}
        for rule in LateFeeRule.objects.filter(is_active=True).order_by("school_id", "-days_after_due"):
            rules_by_school.setdefault(rule.school_id, []).append(rule)

        updated = 0
        for invoice in overdue:
            days_overdue = (today - invoice.due_date).days

            school_rules = rules_by_school.get(invoice.student.school_id, [])
            if school_rules:
                late_fee = Decimal("0")
                for rule in school_rules:
                    if days_overdue >= rule.days_after_due:
                        late_fee = _compute_rule_late_fee(invoice, rule)
                        break
            else:
                late_fee = (
                    invoice.fee_structure.late_fee_per_day * Decimal(str(days_overdue))
                    if invoice.fee_structure and invoice.fee_structure.late_fee_per_day
                    else Decimal("0")
                )

            invoice.status = "overdue"
            invoice.late_fee = late_fee
            invoice.total_amount = invoice.base_amount + late_fee - invoice.discount_amount
            invoice.save(update_fields=["status", "late_fee", "total_amount"])

            # Audit trail: record the late fee exactly once per invoice.
            if late_fee > 0:
                TransactionLog.objects.get_or_create(
                    transaction_id=f"LATE-{invoice.id}",
                    defaults={
                        "school_id": invoice.student.school_id,
                        "student_id": invoice.student_id,
                        "transaction_type": TransactionLog.TransactionType.LATE_FEE,
                        "amount": late_fee,
                        "reference_number": invoice.invoice_number,
                        "description": (
                            f"Late fee of {late_fee} applied to invoice "
                            f"{invoice.invoice_number} ({days_overdue} days overdue)"
                        ),
                        "metadata": {
                            "invoice_id": str(invoice.id),
                            "days_overdue": days_overdue,
                        },
                    },
                )

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

            # Notify parents (pre-fetched to avoid per-invoice DB query)
            for sg in student.active_guardians:
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
        from django.db.models import Prefetch
        from services.students.models import Guardian

        invoices_qs = (
            FeeInvoice.objects.filter(
                status__in=["unpaid", "partial"],
                due_date=reminder_date,
            )
            .select_related("student__user", "student__school")
            .prefetch_related(
                Prefetch(
                    "student__guardians",
                    queryset=Guardian.objects.filter(user__isnull=False).select_related("user"),
                    to_attr="portal_guardians",
                )
            )
        )
        if school_id is not None:
            invoices_qs = invoices_qs.filter(student__school_id=school_id)

        # Evaluate once; subsequent operations use in-memory lists.
        invoices_list = list(invoices_qs)

        # Bulk fetch existing reminders (1 query instead of N).
        reminded_ids = set(
            Notification.objects.filter(
                reference_type="fee_invoice",
                channel="in_app",
                title="Fee Reminder",
                reference_id__in=[str(inv.id) for inv in invoices_list],
            ).values_list("reference_id", flat=True)
        )

        # Bulk fetch fee_due templates keyed by school (1 query instead of N).
        school_ids = {inv.student.school_id for inv in invoices_list}
        templates_by_school = {
            t.school_id: t
            for t in NotificationTemplate.objects.filter(school_id__in=school_ids, event_type="fee_due", is_active=True)
        }

        count = 0
        for invoice in invoices_list:
            # Never double-remind: skip if an in-app reminder already exists for this invoice.
            if str(invoice.id) in reminded_ids:
                continue

            student = invoice.student
            template = templates_by_school.get(student.school_id)
            context = {
                "student_name": student.user.full_name,
                "amount": f"{invoice.outstanding_amount:,.2f}",
                "due_date": invoice.due_date.strftime("%B %d, %Y"),
            }

            # Notify student + parents using each user's notification preferences.
            users = [student.user] + [g.user for g in student.portal_guardians]
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
            from .numbering import generate_invoice_number

            invoice_number = generate_invoice_number(structure.school)
            _, new = FeeInvoice.objects.get_or_create(
                student=enrollment.student,
                fee_structure=structure,
                academic_year_id=academic_year_id,
                defaults={
                    "invoice_number": invoice_number,
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


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_payment_receipt_notification(self, payment_id: str):
    """
    Send payment receipt notification to student and guardians after
    a successful payment. Updates receipt_sent_at on the Payment record.
    """
    from services.communication.models import NotificationTemplate
    from services.communication.services import NotificationService

    from .models import Payment

    try:
        payment = Payment.objects.select_related(
            "invoice__student__school",
            "invoice__student__user",
        ).get(id=payment_id)

        if payment.receipt_sent_at:
            logger.info("Receipt already sent for payment %s", payment_id)
            return {"skipped": True, "reason": "already_sent"}

        invoice = payment.invoice
        student = invoice.student
        school = student.school

        # Find the notification template
        template = NotificationTemplate.objects.filter(
            school=school, event_type="payment_received", is_active=True
        ).first()

        if not template:
            # Fallback: use fee_due template if payment_received not configured
            template = NotificationTemplate.objects.filter(school=school, event_type="fee_due", is_active=True).first()

        if not template:
            logger.warning("No notification template found for school %s", school.id)
            return {"skipped": True, "reason": "no_template"}

        context = {
            "student_name": student.user.full_name,
            "amount": f"{payment.amount:,.2f}",
            "receipt_number": payment.receipt_number,
            "invoice_number": invoice.invoice_number,
            "payment_method": payment.get_payment_method_display(),
            "payment_date": payment.paid_at.strftime("%B %d, %Y") if payment.paid_at else "today",
        }

        # Notify student
        NotificationService.send(
            user=student.user,
            template=template,
            context=context,
            reference_type="payment",
            reference_id=str(payment.id),
        )

        # Notify guardians with portal access
        try:
            from services.students.models import StudentGuardian

            guardians = StudentGuardian.objects.filter(
                student=student,
                portal_access=True,
            ).select_related("user")
            for guardian in guardians:
                NotificationService.send(
                    user=guardian.user,
                    template=template,
                    context=context,
                    reference_type="payment",
                    reference_id=str(payment.id),
                )
        except Exception:
            pass  # Guardian notification is best-effort

        # Send email receipt with PDF attachment
        try:
            _send_receipt_email(payment, invoice, student, school)
        except Exception as e:
            logger.warning("Failed to send receipt email for payment %s: %s", payment_id, e)

        # Mark receipt as sent
        payment.receipt_sent_at = timezone.now()
        payment.save(update_fields=["receipt_sent_at"])

        logger.info("Payment receipt notification sent for payment %s", payment_id)
        return {"sent": True, "payment_id": payment_id}

    except Payment.DoesNotExist:
        logger.error("Payment %s not found", payment_id)
        return {"sent": False, "error": "payment_not_found"}
    except Exception as exc:
        logger.error("send_payment_receipt_notification failed: %s", exc)
        raise self.retry(exc=exc)


def _send_receipt_email(payment, invoice, student, school):
    """Send payment receipt email with PDF attachment."""
    from django.core.mail import EmailMultiAlternatives

    # Collect recipient emails
    recipients = [student.user.email]
    try:
        from services.students.models import StudentGuardian

        guardians = StudentGuardian.objects.filter(
            student=student,
            portal_access=True,
        ).select_related("user")
        for g in guardians:
            if g.user.email and g.user.email not in recipients:
                recipients.append(g.user.email)
    except Exception:
        pass

    # Filter out empty emails
    recipients = [e for e in recipients if e]
    if not recipients:
        logger.info("No email recipients for payment %s", payment.id)
        return

    # Generate receipt PDF
    import io

    from django.utils import timezone as tz
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        textColor=colors.HexColor("#4f46e5"),
        fontSize=18,
        spaceAfter=6,
    )
    normal = styles["Normal"]
    small_style = ParagraphStyle(
        "Small",
        parent=normal,
        fontSize=8,
        textColor=colors.grey,
    )

    elements = []
    elements.append(Paragraph("PAYMENT RECEIPT", title_style))
    elements.append(Paragraph(f"{school.name} — {school.address}", normal))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#4f46e5"), spaceAfter=12))

    details = [
        ["Receipt No.", payment.receipt_number],
        ["Invoice No.", invoice.invoice_number],
        ["Student", student.user.full_name],
        ["Admission No.", student.admission_number],
        ["Amount", f"Rs. {payment.amount:,.2f}"],
        ["Payment Method", payment.get_payment_method_display()],
        ["Date", payment.paid_at.strftime("%B %d, %Y, %I:%M %p") if payment.paid_at else "—"],
        ["Status", "Paid"],
    ]
    detail_table = Table(details, colWidths=[5 * cm, 10 * cm])
    detail_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(detail_table)
    elements.append(Spacer(1, 1 * cm))
    elements.append(
        Paragraph(
            f"Generated by {school.name} on {tz.now().strftime('%B %d, %Y')}",
            small_style,
        )
    )

    doc.build(elements)
    buffer.seek(0)

    # Build email
    subject = f"Payment Receipt — {payment.receipt_number}"
    text_content = (
        f"Dear {student.user.full_name},\n\n"
        f"Your payment has been received successfully.\n\n"
        f"Receipt Number: {payment.receipt_number}\n"
        f"Invoice Number: {invoice.invoice_number}\n"
        f"Amount: Rs. {payment.amount:,.2f}\n"
        f"Payment Method: {payment.get_payment_method_display()}\n"
        f"Date: {payment.paid_at.strftime('%B %d, %Y') if payment.paid_at else 'N/A'}\n\n"
        f"Please find the receipt attached.\n\n"
        f" Regards,\n{school.name}"
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=None,  # Uses DEFAULT_FROM_EMAIL
        to=recipients,
    )
    msg.attach(f"receipt_{payment.receipt_number}.pdf", buffer.read(), "application/pdf")
    msg.send(fail_silently=False)
