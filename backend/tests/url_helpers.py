"""
Test URL helpers — centralize API URL construction to avoid hardcoded paths.
All test files should import from here instead of using literal /api/v1/ strings.
"""

API_PREFIX = "/api/v1"


def url(path: str) -> str:
    """Construct a full API URL from a relative path (without leading slash)."""
    clean = path.lstrip("/")
    return f"{API_PREFIX}/{clean}"


# ─── Auth ─────────────────────────────────────────────────────────────────────

AUTH_LOGIN = url("auth/login/")
AUTH_LOGOUT = url("auth/logout/")
AUTH_TOKEN_REFRESH = url("auth/token/refresh/")
AUTH_ME = url("auth/me/")
AUTH_PROFILE = url("auth/profile/")
AUTH_CHANGE_PASSWORD = url("auth/change-password/")
AUTH_PASSWORD_RESET = url("auth/password-reset/")
AUTH_PASSWORD_RESET_CONFIRM = url("auth/password-reset/confirm/")
AUTH_SEND_VERIFICATION = url("auth/send-verification/")
AUTH_CONFIRM_VERIFICATION = url("auth/verify-email/")

# ─── 2FA ──────────────────────────────────────────────────────────────────────

AUTH_SETUP_2FA = url("auth/setup-2fa/")
AUTH_VERIFY_2FA = url("auth/verify-2fa/")
AUTH_DISABLE_2FA = url("auth/disable-2fa/")
AUTH_VERIFY_2FA_LOGIN = url("auth/verify-2fa-login/")
AUTH_REGENERATE_BACKUP_CODES = url("auth/regenerate-backup-codes/")

# ─── Students ─────────────────────────────────────────────────────────────────

STUDENTS_LIST = url("students/")
STUDENTS_PROMOTE = url("students/promote/")


def student_detail(student_id: str) -> str:
    return url(f"students/{student_id}/")


def student_attendance_summary(student_id: str) -> str:
    return url(f"students/{student_id}/attendance-summary/")


# ─── Attendance ────────────────────────────────────────────────────────────────

ATTENDANCE_BULK_RECORD = url("attendance/bulk-record/")
ATTENDANCE_CLASSROOM_SUMMARY = url("attendance/classroom-summary/")
ATTENDANCE_STUDENT_REPORT = url("attendance/student-report/")


def attendance_leave_approve(leave_id: int) -> str:
    return url(f"attendance/leaves/{leave_id}/approve/")


# ─── Gradebook ────────────────────────────────────────────────────────────────

GRADEBOOK_EXAMS = url("gradebook/exams/")
GRADEBOOK_GRADES_BULK = url("gradebook/grades/bulk/")
GRADEBOOK_GRADES = url("gradebook/grades/")
GRADEBOOK_REPORT_CARDS = url("gradebook/report-cards/")


def gradebook_exam_leaderboard(exam_id: str) -> str:
    return url(f"gradebook/exams/{exam_id}/leaderboard/")


def gradebook_generate_report_cards(exam_id: str) -> str:
    return url(f"gradebook/exams/{exam_id}/generate-report-cards/")


# ─── Fees ──────────────────────────────────────────────────────────────────────

FEES_INVOICES = url("fees/invoices/")
FEES_PAYMENTS = url("fees/payments/")
FEES_SCHOLARSHIPS = url("fees/scholarships/")


def fees_invoice_waive(invoice_id: str) -> str:
    return url(f"fees/invoices/{invoice_id}/waive/")


# ─── Communication ─────────────────────────────────────────────────────────────

COMMUNICATION_ANNOUNCEMENTS = url("communication/announcements/")
COMMUNICATION_NOTIFICATIONS = url("communication/notifications/")
COMMUNICATION_NOTIFICATIONS_UNREAD_COUNT = url("communication/notifications/unread-count/")
COMMUNICATION_NOTIFICATIONS_MARK_ALL_READ = url("communication/notifications/mark-all-read/")
COMMUNICATION_MESSAGES = url("communication/messages/")


def communication_announcement_detail(ann_id: str) -> str:
    return url(f"communication/announcements/{ann_id}/")


def communication_announcement_mark_read(ann_id: str) -> str:
    return url(f"communication/announcements/{ann_id}/mark-read/")


def communication_announcement_publish(ann_id: str) -> str:
    return url(f"communication/announcements/{ann_id}/publish/")


# ─── Timetable ────────────────────────────────────────────────────────────────

TIMETABLE_SLOTS = url("timetable/slots/")
TIMETABLE_PERIODS = url("timetable/periods/")
TIMETABLE_EVENTS = url("timetable/events/")
TIMETABLE_WEEKLY = url("timetable/slots/weekly/")
TIMETABLE_TEACHER_SCHEDULE = url("timetable/slots/teacher-schedule/")
TIMETABLE_EVENTS_UPCOMING = url("timetable/events/upcoming/")

# ─── Reporting ────────────────────────────────────────────────────────────────

REPORTING_DASHBOARD_STATS = url("reporting/dashboard-stats/")
REPORTING_ATTENDANCE_REPORT = url("reporting/attendance-report/")
REPORTING_FEE_REPORT = url("reporting/fee-report/")
REPORTING_EXPORT_STUDENTS_CSV = url("reporting/export/students-csv/")
REPORTING_EXPORT_ATTENDANCE_PDF = url("reporting/export/attendance-pdf/")

# ─── Academics ────────────────────────────────────────────────────────────────

ACADEMICS_SUBJECTS = url("academics/subjects/")
ACADEMICS_ASSIGNMENTS = url("academics/assignments/")
ACADEMICS_MY_ASSIGNMENTS = url("academics/assignments/my-assignments/")
ACADEMICS_LESSON_PLANS = url("academics/lesson-plans/")
ACADEMICS_TEACHER_PROFILES = url("academics/teacher-profiles/")
