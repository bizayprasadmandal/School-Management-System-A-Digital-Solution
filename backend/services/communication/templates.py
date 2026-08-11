"""
Standard notification templates.

Every school gets the same set of event templates (absent alerts, fee
reminders/overdue, report cards, announcements) so operational notifications
work out of the box — not just for the demo school. Schools can still override
individual templates afterwards; ``ensure_school_notification_templates`` only
creates missing rows (get_or_create) and never clobbers edits.
"""

DEFAULT_NOTIFICATION_TEMPLATES = [
    {
        "event_type": "attendance_absent",
        "name": "Attendance Alert",
        "email_subject": "Attendance Alert — {{student_name}}",
        "email_body": (
            "Dear Parent, {{student_name}} was absent on {{date}}. "
            "Please contact the school office if this was unexpected."
        ),
        "sms_body": "{{student_name}} absent on {{date}}",
        "push_title": "Attendance Alert",
        "push_body": "{{student_name}} was absent today.",
    },
    {
        "event_type": "fee_due",
        "name": "Fee Reminder",
        "email_subject": "Fee due: ${{amount}} by {{due_date}}",
        "email_body": (
            "Dear Parent, the fee payment of ${{amount}} for {{student_name}} "
            "is due on {{due_date}}. Please arrange payment before the due date."
        ),
        "sms_body": "Fee due: ${{amount}} by {{due_date}}",
        "push_title": "Fee Reminder",
        "push_body": "Payment of ${{amount}} due on {{due_date}}.",
    },
    {
        "event_type": "fee_overdue",
        "name": "Fee Overdue Alert",
        "email_subject": "Fee payment overdue — {{student_name}}",
        "email_body": (
            "The fee payment of ${{amount}} (Invoice #{{invoice_number}}) is "
            "overdue by {{days_overdue}} day(s). A late fee has been applied."
        ),
        "sms_body": "Fee payment of ${{amount}} overdue by {{days_overdue}} day(s).",
        "push_title": "Fee Payment Overdue",
        "push_body": "Your fee payment of ${{amount}} is overdue.",
    },
    {
        "event_type": "report_card_published",
        "name": "Report Card Available",
        "email_subject": "{{exam_name}} results available",
        "email_body": ("{{student_name}}'s {{exam_name}} results are now available on the portal."),
        "sms_body": "{{exam_name}} results available",
        "push_title": "Results Available",
        "push_body": "Your {{exam_name}} report card is ready.",
    },
    {
        "event_type": "announcement",
        "name": "Announcement",
        "email_subject": "{{title}}",
        "email_body": "{{content}}",
        "sms_body": "{{content}}",
        "push_title": "{{title}}",
        "push_body": "{{content}}",
    },
]


def ensure_school_notification_templates(school):
    """Idempotently create the standard templates for a school. Returns count created."""
    from .models import NotificationTemplate

    created = 0
    for tpl in DEFAULT_NOTIFICATION_TEMPLATES:
        _, was_created = NotificationTemplate.objects.get_or_create(
            school=school,
            event_type=tpl["event_type"],
            defaults={**tpl, "is_active": True},
        )
        if was_created:
            created += 1
    return created
