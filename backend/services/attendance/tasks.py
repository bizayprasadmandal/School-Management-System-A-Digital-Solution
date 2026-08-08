"""
Attendance async tasks — Celery workers for notifications and batch processing
"""

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_absent_guardians(self, record_id: str):
    """
    Notify parent/guardian when a student is marked absent.
    Runs after daily attendance recording.
    """
    try:
        from services.communication.models import NotificationTemplate
        from services.communication.services import NotificationService

        from .models import AttendanceRecord

        record = (
            AttendanceRecord.objects.select_related("student__user", "student__school")
            .prefetch_related("student__guardians__user")
            .get(id=record_id)
        )

        student = record.student
        school = student.school

        template = NotificationTemplate.objects.filter(
            school=school, event_type="attendance_absent", is_active=True
        ).first()

        context = {
            "student_name": student.user.full_name,
            "school_name": school.name,
            "date": record.date.strftime("%B %d, %Y"),
        }

        notified_users = []
        for guardian in student.guardians.filter(user__isnull=False):
            guard_user = guardian.user
            # Build channels based on guardian's notification preferences
            channels = []
            if guard_user.notify_push:
                channels.append("push")
            if guard_user.notify_email:
                channels.append("email")
            if guard_user.notify_sms:
                channels.append("sms")
            channels.append("in_app")

            if channels:
                NotificationService.send(
                    user=guard_user,
                    template=template,
                    context=context,
                    channels=channels,
                )
                notified_users.append(str(guard_user.id))

        record.notified_guardian = True
        record.save(update_fields=["notified_guardian"])

        logger.info(
            "Absent notification sent for student %s on %s to %d guardians",
            student.admission_number,
            record.date,
            len(notified_users),
        )

    except Exception as exc:
        logger.error("Failed to send absent notification for record %s: %s", record_id, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True)
def process_approved_leave(self, leave_id: int):
    """
    When a leave is approved, auto-update attendance records
    for the leave period to EXCUSED status.
    """
    try:
        from datetime import timedelta

        from .models import AttendanceLeave, AttendanceRecord

        leave = AttendanceLeave.objects.select_related("student").get(id=leave_id)
        student = leave.student

        # A classroom/academic_year are required on AttendanceRecord, so if the
        # student has no (active) enrollment we cannot synthesize records.
        enrollment = student.enrollments.filter(is_active=True).first()
        if enrollment is None:
            logger.warning(
                "Leave %d approved but student %s has no active enrollment; " "skipping attendance auto-update",
                leave_id,
                student.admission_number,
            )
            return {"updated": 0}

        current_date = leave.from_date

        updated_count = 0
        while current_date <= leave.to_date:
            record, created = AttendanceRecord.objects.get_or_create(
                student=student,
                date=current_date,
                defaults={
                    "classroom": enrollment.classroom,
                    "academic_year": enrollment.academic_year,
                    "status": AttendanceRecord.Status.EXCUSED,
                    "remarks": f"Approved leave: {leave.leave_type}",
                },
            )
            if not created:
                record.status = AttendanceRecord.Status.EXCUSED
                record.remarks = f"Approved leave: {leave.leave_type}"
                record.save(update_fields=["status", "remarks"])
            updated_count += 1
            current_date += timedelta(days=1)

        logger.info("Processed approved leave %d: %d attendance records updated", leave_id, updated_count)

    except Exception as exc:
        logger.error("Failed to process approved leave %d: %s", leave_id, exc)
        raise


@shared_task
def generate_monthly_attendance_report(school_id: str, month: int, year: int):
    """
    Generate and cache monthly attendance report for a school.
    Scheduled via django-celery-beat on the 1st of each month.
    """
    from django.core.cache import cache
    from services.auth.models import School

    from .models import AttendanceRecord

    school = School.objects.get(id=school_id)
    records = AttendanceRecord.objects.filter(
        student__school=school,
        date__year=year,
        date__month=month,
    )

    stats = {
        "school_id": str(school_id),
        "month": month,
        "year": year,
        "total_records": records.count(),
        "present": records.filter(status="P").count(),
        "absent": records.filter(status="A").count(),
        "late": records.filter(status="L").count(),
        "excused": records.filter(status="E").count(),
        "generated_at": timezone.now().isoformat(),
    }

    cache_key = f"monthly_attendance_{school_id}_{year}_{month}"
    cache.set(cache_key, stats, timeout=86400)  # Cache 24 hours

    logger.info("Monthly attendance report cached for school %s (%d/%d)", school.code, month, year)
    return stats
