"""URL Configuration for timetable."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AcademicCalendarViewSet,
    AcademicSessionViewSet,
    BellScheduleEntryViewSet,
    BellScheduleViewSet,
    ClassGroupEnrollmentViewSet,
    ClassGroupViewSet,
    ClassScheduleViewSet,
    CoCurricularScheduleViewSet,
    ConflictDetectionViewSet,
    DailyScheduleViewSet,
    ExamAttendanceViewSet,
    ExamRoomAllocationViewSet,
    ExamScheduleEntryViewSet,
    ExamScheduleViewSet,
    LessonPlanViewSet,
    PeriodViewSet,
    RoomBookingViewSet,
    RoomUtilizationViewSet,
    SchoolClosureViewSet,
    SchoolEventViewSet,
    SeatingArrangementViewSet,
    SubjectTeacherAssignmentViewSet,
    SubstituteScheduleViewSet,
    SubstituteTeacherViewSet,
    TeacherPreferenceViewSet,
    TeacherTimetableViewSet,
    TeacherWorkloadViewSet,
    TimetableAnalyticsViewSet,
    TimetableApprovalViewSet,
    TimetableChangeRequestViewSet,
    TimetableChangeViewSet,
    TimetableReportViewSet,
    TimetableResourceBookingViewSet,
    TimetableResourceViewSet,
    TimetableSlotViewSet,
    TimetableTemplateSlotViewSet,
    TimetableTemplateViewSet,
    TimetableValidationErrorViewSet,
    TimetableValidationRuleViewSet,
    TimetableVersionViewSet,
)

app_name = "timetable_v1"

router = DefaultRouter()
router.register(r"period", PeriodViewSet, basename="period")
router.register(r"timetable-slot", TimetableSlotViewSet, basename="timetable-slot")
router.register(r"school-event", SchoolEventViewSet, basename="school-event")
router.register(r"teacher-timetable", TeacherTimetableViewSet, basename="teacher-timetable")
router.register(r"substitute-teacher", SubstituteTeacherViewSet, basename="substitute-teacher")
router.register(r"conflict-detection", ConflictDetectionViewSet, basename="conflict-detection")
router.register(r"exam-schedule", ExamScheduleViewSet, basename="exam-schedule")
router.register(r"exam-schedule-entry", ExamScheduleEntryViewSet, basename="exam-schedule-entry")
router.register(r"academic-calendar", AcademicCalendarViewSet, basename="academic-calendar")
router.register(r"room-booking", RoomBookingViewSet, basename="room-booking")
router.register(r"timetable-template", TimetableTemplateViewSet, basename="timetable-template")
router.register(r"timetable-template-slot", TimetableTemplateSlotViewSet, basename="timetable-template-slot")
router.register(r"teacher-preference", TeacherPreferenceViewSet, basename="teacher-preference")
router.register(r"timetable-approval", TimetableApprovalViewSet, basename="timetable-approval")
router.register(r"timetable-change", TimetableChangeViewSet, basename="timetable-change")
router.register(r"co-curricular-schedule", CoCurricularScheduleViewSet, basename="co-curricular-schedule")
router.register(r"timetable-report", TimetableReportViewSet, basename="timetable-report")
router.register(r"school-closure", SchoolClosureViewSet, basename="school-closure")
router.register(r"bell-schedule", BellScheduleViewSet, basename="bell-schedule")
router.register(r"bell-schedule-entry", BellScheduleEntryViewSet, basename="bell-schedule-entry")
router.register(r"class-group", ClassGroupViewSet, basename="class-group")
router.register(r"class-group-enrollment", ClassGroupEnrollmentViewSet, basename="class-group-enrollment")
router.register(r"subject-teacher-assignment", SubjectTeacherAssignmentViewSet, basename="subject-teacher-assignment")
router.register(r"lesson-plan", LessonPlanViewSet, basename="lesson-plan")
router.register(r"exam-room-allocation", ExamRoomAllocationViewSet, basename="exam-room-allocation")
router.register(r"seating-arrangement", SeatingArrangementViewSet, basename="seating-arrangement")
router.register(r"exam-attendance", ExamAttendanceViewSet, basename="exam-attendance")
router.register(r"academic-session", AcademicSessionViewSet, basename="academic-session")
router.register(r"substitute-schedule", SubstituteScheduleViewSet, basename="substitute-schedule")
router.register(r"room-utilization", RoomUtilizationViewSet, basename="room-utilization")
router.register(r"timetable-validation-rule", TimetableValidationRuleViewSet, basename="timetable-validation-rule")
router.register(r"timetable-validation-error", TimetableValidationErrorViewSet, basename="timetable-validation-error")
router.register(r"timetable-resource", TimetableResourceViewSet, basename="timetable-resource")
router.register(r"timetable-resource-booking", TimetableResourceBookingViewSet, basename="timetable-resource-booking")
router.register(r"timetable-analytics", TimetableAnalyticsViewSet, basename="timetable-analytics")
router.register(r"timetable-change-request", TimetableChangeRequestViewSet, basename="timetable-change-request")
router.register(r"daily-schedule", DailyScheduleViewSet, basename="daily-schedule")
router.register(r"teacher-workload", TeacherWorkloadViewSet, basename="teacher-workload")
router.register(r"class-schedule", ClassScheduleViewSet, basename="class-schedule")
router.register(r"timetable-version", TimetableVersionViewSet, basename="timetable-version")

urlpatterns = [
    path("", include(router.urls)),
]
