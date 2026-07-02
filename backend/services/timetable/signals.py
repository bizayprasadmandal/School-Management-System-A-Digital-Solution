"""Timetable signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender="timetable.TimetableSlot")
def handle_slot_created(sender, instance, created, **kwargs):
    if created:
        logger.info("Timetable slot created: %s %s period %s day %s",
                    instance.classroom, instance.assignment.subject.name,
                    instance.period.name, instance.day_of_week)
