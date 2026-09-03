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


# ── Additional registrations (module expansion) ──
router.register(r"bell-schedule", views.BellScheduleViewSet, basename="bell-schedule")
router.register(r"bell-schedule-entry", views.BellScheduleEntryViewSet, basename="bell-schedule-entry")
router.register(r"class-group", views.ClassGroupViewSet, basename="class-group")
router.register(r"class-group-enrollment", views.ClassGroupEnrollmentViewSet, basename="class-group-enrollment")
router.register(
    r"subject-teacher-assignment", views.SubjectTeacherAssignmentViewSet, basename="subject-teacher-assignment"
)
router.register(r"lesson-plan", views.LessonPlanViewSet, basename="lesson-plan")
router.register(r"exam-room-allocation", views.ExamRoomAllocationViewSet, basename="exam-room-allocation")
router.register(r"seating-arrangement", views.SeatingArrangementViewSet, basename="seating-arrangement")
router.register(r"exam-attendance", views.ExamAttendanceViewSet, basename="exam-attendance")
router.register(r"academic-session", views.AcademicSessionViewSet, basename="academic-session")
router.register(r"substitute-schedule", views.SubstituteScheduleViewSet, basename="substitute-schedule")
router.register(r"room-utilization", views.RoomUtilizationViewSet, basename="room-utilization")
router.register(
    r"timetable-validation-rule", views.TimetableValidationRuleViewSet, basename="timetable-validation-rule"
)
router.register(
    r"timetable-validation-error", views.TimetableValidationErrorViewSet, basename="timetable-validation-error"
)
router.register(r"timetable-resource", views.TimetableResourceViewSet, basename="timetable-resource")
router.register(
    r"timetable-resource-booking", views.TimetableResourceBookingViewSet, basename="timetable-resource-booking"
)
router.register(r"timetable-analytics", views.TimetableAnalyticsViewSet, basename="timetable-analytics")
router.register(r"timetable-change-request", views.TimetableChangeRequestViewSet, basename="timetable-change-request")
router.register(r"daily-schedule", views.DailyScheduleViewSet, basename="daily-schedule")
router.register(r"teacher-workload", views.TeacherWorkloadViewSet, basename="teacher-workload")
router.register(r"class-schedule", views.ClassScheduleViewSet, basename="class-schedule")
router.register(r"timetable-version", views.TimetableVersionViewSet, basename="timetable-version")

urlpatterns = [path("", include(router.urls))]
