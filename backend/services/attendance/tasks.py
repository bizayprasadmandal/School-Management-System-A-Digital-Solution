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


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
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
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_monthly_attendance_report(self, school_id: str, month: int, year: int):
    """
    Generate and cache monthly attendance report for a school.
    Scheduled via django-celery-beat on the 1st of each month.
    """
    try:
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
    except School.DoesNotExist:
        logger.error("Monthly attendance report skipped: school %s not found", school_id)
        return None
    except Exception as exc:
        logger.error("Failed to generate monthly attendance report for school %s: %s", school_id, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_teacher_reminders(self):
    """
    Send reminders to teachers who haven't recorded attendance today.
    Scheduled via django-celery-beat daily at 10:00 AM.
    """
    try:
        from datetime import date

        from services.academics.models import TeacherAssignment
        from services.auth.models import School, User
        from services.communication.models import NotificationTemplate
        from services.communication.services import NotificationService

        from .models import AttendancePolicy, AttendanceRecord

        today = date.today()

        # Skip weekends
        if today.weekday() >= 5:  # Saturday=5, Sunday=6
            return {"skipped": True, "reason": "weekend"}

        # Skip holidays
        from .models import Holiday

        schools_with_holiday = Holiday.objects.filter(date=today).values_list("school_id", flat=True)

        notified_count = 0
        for school in School.objects.filter(is_active=True):
            if school.id in schools_with_holiday:
                continue

            # Get school policy
            AttendancePolicy.objects.filter(school=school, is_active=True).first()

            # Get teachers with assignments today
            teachers_with_assignments = (
                TeacherAssignment.objects.filter(
                    subject__school=school,
                    classroom__grade__academic_year__is_current=True,
                )
                .values_list("teacher", flat=True)
                .distinct()
            )

            # Get teachers who already recorded attendance today
            teachers_recorded = (
                AttendanceRecord.objects.filter(
                    classroom__school=school,
                    date=today,
                    recorded_by__isnull=False,
                )
                .values_list("recorded_by_id", flat=True)
                .distinct()
            )

            # Find teachers who haven't recorded yet
            missing_teachers = set(teachers_with_assignments) - set(teachers_recorded)

            template = NotificationTemplate.objects.filter(
                school=school, event_type="attendance_reminder", is_active=True
            ).first()

            for teacher_id in missing_teachers:
                try:
                    teacher = User.objects.get(id=teacher_id)
                    if template:
                        NotificationService.send(
                            user=teacher,
                            template=template,
                            context={
                                "teacher_name": teacher.full_name,
                                "date": today.strftime("%B %d, %Y"),
                                "school_name": school.name,
                            },
                            channels=["in_app", "push"],
                        )
                        notified_count += 1
                except User.DoesNotExist:
                    continue

        logger.info("Teacher reminders sent: %d teachers notified", notified_count)
        return {"notified": notified_count}

    except Exception as exc:
        logger.error("Failed to send teacher reminders: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def escalate_missing_attendance(self):
    """
    Escalate to admin when attendance not recorded after reminder.
    Scheduled via django-celery-beat daily at 11:00 AM.
    """
    try:
        from datetime import date

        from services.auth.models import School, User
        from services.communication.models import NotificationTemplate
        from services.communication.services import NotificationService

        from .models import AttendancePolicy, AttendanceRecord

        today = date.today()

        if today.weekday() >= 5:
            return {"skipped": True, "reason": "weekend"}

        from .models import Holiday

        schools_with_holiday = Holiday.objects.filter(date=today).values_list("school_id", flat=True)

        escalated_count = 0
        for school in School.objects.filter(is_active=True):
            if school.id in schools_with_holiday:
                continue

            policy = AttendancePolicy.objects.filter(school=school, is_active=True).first()
            if not policy or not policy.escalation_enabled:
                continue

            # Check if any attendance recorded today
            recorded_today = AttendanceRecord.objects.filter(classroom__school=school, date=today).exists()

            if not recorded_today:
                # Escalate to school admins
                admins = User.objects.filter(school=school, role="school_admin", is_active=True)
                template = NotificationTemplate.objects.filter(
                    school=school, event_type="attendance_escalation", is_active=True
                ).first()

                for admin in admins:
                    if template:
                        NotificationService.send(
                            user=admin,
                            template=template,
                            context={
                                "admin_name": admin.full_name,
                                "date": today.strftime("%B %d, %Y"),
                                "school_name": school.name,
                            },
                            channels=["in_app", "push", "email"],
                        )
                        escalated_count += 1

        logger.info("Attendance escalation sent to %d admins", escalated_count)
        return {"escalated": escalated_count}

    except Exception as exc:
        logger.error("Failed to escalate missing attendance: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def auto_assign_substitute(self, original_teacher_id: int, date_str: str, period_number: int = None):
    """
    Auto-assign substitute teacher when original teacher is absent.
    Finds the best available teacher for the same subject/classroom.
    """
    try:
        from datetime import date

        from services.academics.models import TeacherAssignment
        from services.auth.models import User

        from .models import SubstituteTeacher

        original_teacher = User.objects.get(id=original_teacher_id)
        target_date = date.fromisoformat(date_str)

        # Get all assignments for the absent teacher on this date
        assignments = TeacherAssignment.objects.filter(
            teacher=original_teacher,
            subject__school=original_teacher.school,
        )

        for assignment in assignments:
            # Skip if already has substitute
            if SubstituteTeacher.objects.filter(
                date=target_date,
                classroom=assignment.classroom,
                period_number=period_number,
            ).exists():
                continue

            # Find available teachers (not absent, same subject preferred)
            available_teachers = (
                User.objects.filter(
                    role="teacher",
                    school=original_teacher.school,
                    is_active=True,
                )
                .exclude(id=original_teacher_id)
                .exclude(
                    # Exclude teachers who are also absent
                    substitute_original__date=target_date,
                )
            )

            # Prefer teachers who teach the same subject
            subject_teachers = available_teachers.filter(
                assignments__subject=assignment.subject,
            ).distinct()

            substitute = subject_teachers.first() or available_teachers.first()

            if substitute:
                SubstituteTeacher.objects.create(
                    original_teacher=original_teacher,
                    substitute_teacher=substitute,
                    date=target_date,
                    period_number=period_number,
                    classroom=assignment.classroom,
                    subject=assignment.subject,
                    reason="Auto-assigned: original teacher absent",
                    is_auto_assigned=True,
                )
                logger.info(
                    "Substitute assigned: %s replacing %s for %s on %s",
                    substitute.full_name,
                    original_teacher.full_name,
                    assignment.subject.name,
                    target_date,
                )

    except Exception as exc:
        logger.error("Failed to auto-assign substitute: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def archive_old_attendance(self, school_id: str, older_than_days: int = 365):
    """
    Archive attendance data older than specified days.
    Scheduled monthly for GDPR compliance.
    """
    try:
        from datetime import date, timedelta

        from services.auth.models import School

        from .models import AttendanceDataArchive, AttendanceRecord, PeriodAttendance

        school = School.objects.get(id=school_id)
        cutoff_date = date.today() - timedelta(days=older_than_days)

        # Archive daily attendance
        old_daily = AttendanceRecord.objects.filter(
            classroom__school=school,
            date__lt=cutoff_date,
        )

        if old_daily.exists():
            data = list(old_daily.values("student_id", "classroom_id", "date", "status", "remarks"))

            AttendanceDataArchive.objects.create(
                school=school,
                academic_year=None,
                archive_type="daily",
                data=data,
                record_count=len(data),
                date_from=old_daily.order_by("date").first().date,
                date_to=cutoff_date,
            )

            # Purge old records
            old_daily.delete()

        # Archive period attendance
        old_period = PeriodAttendance.objects.filter(
            assignment__subject__school=school,
            date__lt=cutoff_date,
        )

        if old_period.exists():
            data = list(old_period.values("student_id", "assignment_id", "date", "period_number", "status"))

            AttendanceDataArchive.objects.create(
                school=school,
                academic_year=None,
                archive_type="period",
                data=data,
                record_count=len(data),
                date_from=old_period.order_by("date").first().date,
                date_to=cutoff_date,
            )

            old_period.delete()

        logger.info("Archived old attendance data for school %s (older than %d days)", school.code, older_than_days)
        return {"archived": True}

    except Exception as exc:
        logger.error("Failed to archive attendance data: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_scheduled_email_reports(self, school_id: str, frequency: str = "weekly"):
    """
    Send scheduled email reports to admins/parents.
    """
    try:
        from datetime import date, timedelta

        from services.auth.models import School, User
        from services.communication.services import NotificationService

        from .models import AttendanceRecord

        school = School.objects.get(id=school_id)
        today = date.today()

        if frequency == "weekly":
            date_from = today - timedelta(days=7)
        elif frequency == "monthly":
            date_from = today - timedelta(days=30)
        else:
            date_from = today - timedelta(days=1)

        records = AttendanceRecord.objects.filter(
            classroom__school=school,
            date__gte=date_from,
            date__lte=today,
        )

        total = records.count()
        present = records.filter(status__in=["P", "L"]).count()
        absent = records.filter(status="A").count()
        percentage = round(present / total * 100, 1) if total > 0 else 0

        # Send to school admins
        admins = User.objects.filter(school=school, role="school_admin", is_active=True)
        for admin in admins:
            NotificationService.send(
                user=admin,
                template=None,
                context={
                    "report_type": f"{frequency.title()} Attendance Report",
                    "school_name": school.name,
                    "period": f"{date_from} to {today}",
                    "total_records": total,
                    "present": present,
                    "absent": absent,
                    "percentage": percentage,
                },
                channels=["email"],
            )

        logger.info("Scheduled %s report sent for school %s", frequency, school.code)
        return {"sent": True}

    except Exception as exc:
        logger.error("Failed to send scheduled report: %s", exc)
        raise self.retry(exc=exc)
