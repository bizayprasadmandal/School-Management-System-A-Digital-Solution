"""
GraphQL Schema — Unified schema combining all service schemas
"""

import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from services.students.models import Student, Classroom, Grade as GradeLevel
from services.academics.models import Subject, TeacherAssignment
from services.attendance.models import AttendanceRecord
from services.gradebook.models import Grade, ReportCard, Exam
from services.communication.models import Announcement, Notification


# ─── Object Types ─────────────────────────────────────────────────────────────

class StudentType(DjangoObjectType):
    full_name = graphene.String()
    age = graphene.Int()

    class Meta:
        model = Student
        fields = [
            "id", "admission_number", "roll_number", "date_of_birth",
            "gender", "blood_group", "is_active", "admission_date",
        ]
        filter_fields = {
            "admission_number": ["exact", "icontains"],
            "is_active": ["exact"],
            "gender": ["exact"],
        }

    def resolve_full_name(self, info):
        return self.user.full_name

    def resolve_age(self, info):
        return self.age


class ClassroomType(DjangoObjectType):
    student_count = graphene.Int()

    class Meta:
        model = Classroom
        fields = ["id", "name", "capacity", "room_number"]

    def resolve_student_count(self, info):
        return self.student_count


class SubjectType(DjangoObjectType):
    class Meta:
        model = Subject
        fields = ["id", "name", "code", "max_marks", "pass_marks", "credit_hours", "is_core"]


class AttendanceRecordType(DjangoObjectType):
    class Meta:
        model = AttendanceRecord
        fields = ["id", "date", "status", "remarks", "recorded_at"]


class GradeType(DjangoObjectType):
    percentage = graphene.Float()
    is_pass = graphene.Boolean()

    class Meta:
        model = Grade
        fields = ["id", "marks_obtained", "is_absent", "remarks", "graded_at"]

    def resolve_percentage(self, info):
        return float(self.percentage) if self.percentage else None

    def resolve_is_pass(self, info):
        return self.is_pass


class AnnouncementType(DjangoObjectType):
    class Meta:
        model = Announcement
        fields = ["id", "title", "content", "priority", "audience", "created_at", "published_at"]


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = ["id", "title", "body", "channel", "status", "created_at", "read_at"]


# ─── Queries ──────────────────────────────────────────────────────────────────

class Query(graphene.ObjectType):
    # Student queries
    student = graphene.Field(StudentType, id=graphene.UUID(required=True))
    students = graphene.List(
        StudentType,
        is_active=graphene.Boolean(),
        gender=graphene.String(),
        search=graphene.String(),
    )

    # My profile
    my_profile = graphene.Field(StudentType)

    # Attendance
    my_attendance = graphene.List(
        AttendanceRecordType,
        month=graphene.Int(),
        year=graphene.Int(),
    )

    # Grades
    my_grades = graphene.List(GradeType, exam_id=graphene.UUID())

    # Announcements
    announcements = graphene.List(AnnouncementType, limit=graphene.Int(default_value=10))

    # Notifications
    my_notifications = graphene.List(
        NotificationType,
        unread_only=graphene.Boolean(default_value=False),
    )

    @login_required
    def resolve_student(self, info, id):
        user = info.context.user
        try:
            student = Student.objects.get(id=id, school=user.school)
            # Permission check
            if user.role == "student" and student.user != user:
                return None
            if user.role == "parent" and not student.guardians.filter(user=user).exists():
                return None
            return student
        except Student.DoesNotExist:
            return None

    @login_required
    def resolve_students(self, info, is_active=None, gender=None, search=None):
        user = info.context.user
        if user.role not in ["school_admin", "super_admin", "teacher"]:
            return Student.objects.none()
        qs = Student.objects.filter(school=user.school)
        if is_active is not None:
            qs = qs.filter(is_active=is_active)
        if gender:
            qs = qs.filter(gender=gender)
        if search:
            qs = qs.filter(
                user__first_name__icontains=search
            ) | qs.filter(user__last_name__icontains=search) | qs.filter(
                admission_number__icontains=search
            )
        return qs.select_related("user")[:100]

    @login_required
    def resolve_my_profile(self, info):
        user = info.context.user
        if user.role == "student":
            return Student.objects.filter(user=user).first()
        return None

    @login_required
    def resolve_my_attendance(self, info, month=None, year=None):
        from datetime import date
        user = info.context.user
        if user.role != "student":
            return AttendanceRecord.objects.none()
        qs = AttendanceRecord.objects.filter(student__user=user)
        if month:
            qs = qs.filter(date__month=month)
        if year:
            qs = qs.filter(date__year=year)
        return qs.order_by("-date")

    @login_required
    def resolve_my_grades(self, info, exam_id=None):
        user = info.context.user
        if user.role != "student":
            return Grade.objects.none()
        qs = Grade.objects.filter(student__user=user)
        if exam_id:
            qs = qs.filter(exam_schedule__exam_id=exam_id)
        return qs.select_related("exam_schedule__subject", "exam_schedule__exam")

    @login_required
    def resolve_announcements(self, info, limit):
        from django.utils import timezone
        user = info.context.user
        qs = Announcement.objects.filter(
            school=user.school,
            is_draft=False,
        ).filter(
            graphene.Q(expires_at__isnull=True) | graphene.Q(expires_at__gt=timezone.now())
        )
        if user.role == "student":
            qs = qs.filter(audience__in=["all", "students"])
        elif user.role == "parent":
            qs = qs.filter(audience__in=["all", "parents"])
        elif user.role == "teacher":
            qs = qs.filter(audience__in=["all", "teachers", "staff"])
        return qs.order_by("-published_at")[:limit]

    @login_required
    def resolve_my_notifications(self, info, unread_only):
        user = info.context.user
        qs = Notification.objects.filter(user=user, channel="in_app")
        if unread_only:
            qs = qs.filter(read_at__isnull=True)
        return qs.order_by("-created_at")[:50]


# ─── Mutations ────────────────────────────────────────────────────────────────

class MarkNotificationRead(graphene.Mutation):
    class Arguments:
        notification_id = graphene.UUID(required=True)

    success = graphene.Boolean()

    @login_required
    def mutate(self, info, notification_id):
        from django.utils import timezone
        try:
            notif = Notification.objects.get(id=notification_id, user=info.context.user)
            notif.status = "read"
            notif.read_at = timezone.now()
            notif.save(update_fields=["status", "read_at"])
            return MarkNotificationRead(success=True)
        except Notification.DoesNotExist:
            return MarkNotificationRead(success=False)


class MarkAllNotificationsRead(graphene.Mutation):
    count = graphene.Int()

    @login_required
    def mutate(self, info):
        from django.utils import timezone
        count = Notification.objects.filter(
            user=info.context.user, read_at__isnull=True, channel="in_app"
        ).update(status="read", read_at=timezone.now())
        return MarkAllNotificationsRead(count=count)


class Mutation(graphene.ObjectType):
    mark_notification_read = MarkNotificationRead.Field()
    mark_all_notifications_read = MarkAllNotificationsRead.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
