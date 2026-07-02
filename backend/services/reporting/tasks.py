"""Reporting Celery tasks — scheduled analytics caching."""
from celery import shared_task
import logging
logger = logging.getLogger(__name__)

@shared_task
def cache_school_analytics(school_id: str):
    """Pre-compute and cache school analytics for the dashboard."""
    from django.core.cache import cache
    from django.utils import timezone
    from services.auth.models import School
    from services.students.models import Student
    from services.attendance.models import AttendanceRecord
    from django.db.models import Count, Q
    try:
        school = School.objects.get(id=school_id)
        today = timezone.now().date()
        stats = {
            "total_students": Student.objects.filter(school=school, is_active=True).count(),
            "today_attendance": AttendanceRecord.objects.filter(
                student__school=school, date=today
            ).aggregate(
                total=Count("id"),
                present=Count("id", filter=Q(status__in=["P","L"])),
            ),
            "cached_at": today.isoformat(),
        }
        cache.set(f"school_analytics_{school_id}", stats, timeout=3600)
        logger.info("Analytics cached for school %s", school.code)
    except Exception as e:
        logger.error("Analytics caching failed for %s: %s", school_id, e)
