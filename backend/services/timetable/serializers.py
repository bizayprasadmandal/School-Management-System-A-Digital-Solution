"""Timetable serializers — moved inline to views.py; re-exported here for import compatibility."""
from services.timetable.views import PeriodSerializer, TimetableSlotSerializer, SchoolEventSerializer
__all__ = ["PeriodSerializer", "TimetableSlotSerializer", "SchoolEventSerializer"]
