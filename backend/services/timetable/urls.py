from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "timetable_v1"
router = DefaultRouter()
router.register("slots", views.TimetableSlotViewSet, basename="slot")
router.register("periods", views.PeriodViewSet, basename="period")
router.register("events", views.SchoolEventViewSet, basename="event")
router.register("teacher-timetables", views.TeacherTimetableViewSet, basename="teacher-timetable")
router.register("substitutes", views.SubstituteTeacherViewSet, basename="substitute")
router.register("conflicts", views.ConflictDetectionViewSet, basename="conflict")
router.register("exam-schedules", views.ExamScheduleViewSet, basename="exam-schedule")
router.register("exam-entries", views.ExamScheduleEntryViewSet, basename="exam-entry")
router.register("academic-calendar", views.AcademicCalendarViewSet, basename="academic-calendar")
router.register("room-bookings", views.RoomBookingViewSet, basename="room-booking")
router.register("templates", views.TimetableTemplateViewSet, basename="template")
router.register("template-slots", views.TimetableTemplateSlotViewSet, basename="template-slot")
router.register("preferences", views.TeacherPreferenceViewSet, basename="preference")
router.register("approvals", views.TimetableApprovalViewSet, basename="approval")
router.register("changes", views.TimetableChangeViewSet, basename="change")
router.register("co-curricular", views.CoCurricularScheduleViewSet, basename="co-curricular")
router.register("reports", views.TimetableReportViewSet, basename="report")
router.register("closures", views.SchoolClosureViewSet, basename="closure")

urlpatterns = [path("", include(router.urls))]
