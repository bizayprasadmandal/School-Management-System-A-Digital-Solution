"""Behavior Management — School-scoped viewsets."""

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django.db.models import Count, Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    BehaviorAlert,
    BehaviorAnalytics,
    BehaviorAppeal,
    BehaviorCategory,
    BehaviorConsequence,
    BehaviorContract,
    BehaviorEvidence,
    BehaviorGoal,
    BehaviorMerit,
    BehaviorPoint,
    BehaviorPointBalance,
    BehaviorRubric,
    BehaviorRubricLevel,
    BehaviorStreak,
    DetentionTracking,
    DigitalHallPass,
    Incident,
    ParentNotification,
    Referral,
    SuspensionTracking,
    TardyTracking,
    WitnessStatement,
)
from .serializers import (
    BehaviorAlertSerializer,
    BehaviorAnalyticsSerializer,
    BehaviorAppealSerializer,
    BehaviorCategorySerializer,
    BehaviorConsequenceSerializer,
    BehaviorContractSerializer,
    BehaviorEvidenceSerializer,
    BehaviorGoalSerializer,
    BehaviorMeritSerializer,
    BehaviorPointBalanceSerializer,
    BehaviorPointSerializer,
    BehaviorRubricLevelSerializer,
    BehaviorRubricSerializer,
    BehaviorStreakSerializer,
    DetentionTrackingSerializer,
    DigitalHallPassSerializer,
    IncidentSerializer,
    ParentNotificationSerializer,
    ReferralSerializer,
    SuspensionTrackingSerializer,
    TardyTrackingSerializer,
    WitnessStatementSerializer,
)


class IsTeacherOrSchoolAdmin(permissions.BasePermission):
    """Teachers and admins can report behavior incidents."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in (
            "school_admin",
            "super_admin",
            "teacher",
        )


class BehaviorCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorCategorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "description"]
    filterset_fields = ["category_type", "is_active"]

    def get_queryset(self):
        return BehaviorCategory.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class IncidentViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["severity", "status", "incident_type", "student", "category"]
    search_fields = ["description", "incident_type"]
    ordering_fields = ["occurred_at", "created_at"]
    ordering = ["-occurred_at"]

    def get_queryset(self):
        return Incident.objects.filter(school=self.request.user.school).select_related(
            "student__user", "reported_by", "category"
        )

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated(), IsTeacherOrSchoolAdmin()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, reported_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolAdmin])
    def resolve(self, request, pk=None):
        """Mark an incident as resolved."""
        incident = self.get_object()
        resolution = request.data.get("resolution", "")
        incident.status = Incident.Status.RESOLVED
        incident.resolution = resolution
        incident.save()
        return Response({"status": "resolved"})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolAdmin])
    def notify_parents(self, request, pk=None):
        """Notify parents about the incident."""
        incident = self.get_object()
        incident.parents_notified = True
        incident.parents_notified_at = timezone.now()
        incident.save()
        # Create parent notification
        ParentNotification.objects.create(
            school=incident.school,
            student=incident.student,
            notification_type=ParentNotification.NotificationType.INCIDENT,
            incident=incident,
            subject=f"Incident Report: {incident.incident_type}",
            message=incident.description,
            sent_by=request.user,
            status=ParentNotification.Status.SENT,
            sent_at=timezone.now(),
        )
        return Response({"status": "parents_notified"})


class ReferralViewSet(viewsets.ModelViewSet):
    serializer_class = ReferralSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status", "incident"]
    search_fields = ["reason", "action_taken"]

    def get_queryset(self):
        return Referral.objects.filter(incident__school=self.request.user.school).select_related(
            "referred_to", "referred_by", "incident"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(referred_by=self.request.user)


class BehaviorPointViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorPointSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["student__user__full_name", "reason"]
    filterset_fields = ["student", "category", "point_type", "is_redeemed"]
    ordering_fields = ["created_at", "points"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return BehaviorPoint.objects.filter(school=self.request.user.school).select_related(
            "student__user", "category", "awarded_by"
        )

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated(), IsTeacherOrSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        point = serializer.save(school=self.request.user.school, awarded_by=self.request.user)
        # Update balance
        balance, _ = BehaviorPointBalance.objects.get_or_create(student=point.student)
        balance.update_balance(point.points, point.point_type)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolMember])
    def redeem(self, request, pk=None):
        """Mark points as redeemed."""
        point = self.get_object()
        point.is_redeemed = True
        point.redeemed_at = timezone.now()
        point.save()
        return Response({"status": "redeemed"})


class BehaviorPointBalanceViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorPointBalanceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student"]

    def get_queryset(self):
        return BehaviorPointBalance.objects.filter(student__school=self.request.user.school).select_related(
            "student__user"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]


class BehaviorConsequenceViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorConsequenceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__full_name", "description"]
    filterset_fields = ["student", "consequence_type", "status"]

    def get_queryset(self):
        return BehaviorConsequence.objects.filter(school=self.request.user.school).select_related(
            "student__user", "incident", "issued_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, issued_by=self.request.user)


class BehaviorMeritViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorMeritSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__full_name", "title"]
    filterset_fields = ["student", "merit_type", "is_public"]

    def get_queryset(self):
        return BehaviorMerit.objects.filter(school=self.request.user.school).select_related(
            "student__user", "awarded_by"
        )

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated(), IsTeacherOrSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, awarded_by=self.request.user)


class DetentionTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = DetentionTrackingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "detention_type", "status"]

    def get_queryset(self):
        return DetentionTracking.objects.filter(school=self.request.user.school).select_related(
            "student__user", "supervisor"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolAdmin])
    def check_in(self, request, pk=None):
        """Mark detention as attended."""
        detention = self.get_object()
        detention.attended = True
        detention.attended_at = timezone.now()
        detention.status = DetentionTracking.Status.COMPLETED
        detention.save()
        return Response({"status": "checked_in"})


class SuspensionTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = SuspensionTrackingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "suspension_type", "status"]

    def get_queryset(self):
        return SuspensionTracking.objects.filter(school=self.request.user.school).select_related(
            "student__user", "issued_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, issued_by=self.request.user)


class BehaviorContractViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorContractSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__full_name", "title"]
    filterset_fields = ["student", "status"]

    def get_queryset(self):
        return BehaviorContract.objects.filter(school=self.request.user.school).select_related(
            "student__user", "created_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolAdmin])
    def sign_student(self, request, pk=None):
        """Mark contract as signed by student."""
        contract = self.get_object()
        contract.student_signed = True
        contract.student_signed_at = timezone.now()
        contract.save()
        return Response({"status": "student_signed"})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolAdmin])
    def sign_parent(self, request, pk=None):
        """Mark contract as signed by parent."""
        contract = self.get_object()
        contract.parent_signed = True
        contract.parent_signed_at = timezone.now()
        contract.save()
        return Response({"status": "parent_signed"})


class WitnessStatementViewSet(viewsets.ModelViewSet):
    serializer_class = WitnessStatementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["incident", "witness_type"]

    def get_queryset(self):
        return WitnessStatement.objects.filter(incident__school=self.request.user.school).select_related("collected_by")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(collected_by=self.request.user)


class BehaviorEvidenceViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorEvidenceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["incident", "evidence_type"]

    def get_queryset(self):
        return BehaviorEvidence.objects.filter(incident__school=self.request.user.school).select_related("uploaded_by")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class BehaviorRubricViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorRubricSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["is_active"]

    def get_queryset(self):
        return BehaviorRubric.objects.filter(school=self.request.user.school).select_related("created_by")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


class BehaviorRubricLevelViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorRubricLevelSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["rubric"]

    def get_queryset(self):
        return BehaviorRubricLevel.objects.filter(rubric__school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]


class DigitalHallPassViewSet(viewsets.ModelViewSet):
    serializer_class = DigitalHallPassSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__full_name", "to_destination"]
    filterset_fields = ["student", "pass_type", "status"]

    def get_queryset(self):
        return DigitalHallPass.objects.filter(school=self.request.user.school).select_related(
            "student__user", "approved_by"
        )

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated(), IsTeacherOrSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, approved_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolAdmin])
    def return_pass(self, request, pk=None):
        """Mark hall pass as returned."""
        hall_pass = self.get_object()
        hall_pass.actual_return_at = timezone.now()
        hall_pass.status = DigitalHallPass.Status.COMPLETED
        # Check if late
        if hall_pass.expected_return_at and hall_pass.actual_return_at > hall_pass.expected_return_at:
            hall_pass.is_late = True
            diff = hall_pass.actual_return_at - hall_pass.expected_return_at
            hall_pass.minutes_late = int(diff.total_seconds() / 60)
        hall_pass.save()
        return Response({"status": "returned"})


class TardyTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = TardyTrackingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__full_name", "class_name"]
    filterset_fields = ["student", "tardy_type", "status"]

    def get_queryset(self):
        return TardyTracking.objects.filter(school=self.request.user.school).select_related("student__user", "teacher")

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated(), IsTeacherOrSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, teacher=self.request.user)


class BehaviorGoalViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorGoalSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__full_name", "title"]
    filterset_fields = ["student", "goal_type", "status"]

    def get_queryset(self):
        return BehaviorGoal.objects.filter(school=self.request.user.school).select_related(
            "student__user", "created_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolAdmin])
    def update_progress(self, request, pk=None):
        """Update goal progress."""
        goal = self.get_object()
        increment = request.data.get("increment", 1)
        goal.current_value += increment
        if goal.current_value >= goal.target_value:
            goal.status = BehaviorGoal.Status.ACHIEVED
        goal.save()
        return Response({"current_value": goal.current_value, "progress_percentage": goal.progress_percentage})


class BehaviorStreakViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorStreakSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "streak_type"]

    def get_queryset(self):
        return BehaviorStreak.objects.filter(student__school=self.request.user.school).select_related("student__user")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]


class BehaviorAlertViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorAlertSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__full_name", "title"]
    filterset_fields = ["student", "alert_type", "priority", "status"]

    def get_queryset(self):
        return BehaviorAlert.objects.filter(school=self.request.user.school).select_related(
            "student__user", "acknowledged_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolAdmin])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert."""
        alert = self.get_object()
        alert.status = BehaviorAlert.Status.ACKNOWLEDGED
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        return Response({"status": "acknowledged"})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolAdmin])
    def resolve(self, request, pk=None):
        """Resolve an alert."""
        alert = self.get_object()
        alert.status = BehaviorAlert.Status.RESOLVED
        alert.resolved_at = timezone.now()
        alert.save()
        return Response({"status": "resolved"})


class BehaviorAppealViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorAppealSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__full_name", "reason"]
    filterset_fields = ["student", "appeal_type", "status"]

    def get_queryset(self):
        return BehaviorAppeal.objects.filter(school=self.request.user.school).select_related(
            "student__user", "reviewed_by"
        )

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated(), IsSchoolMember()]
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolAdmin])
    def review(self, request, pk=None):
        """Review and decide on an appeal."""
        appeal = self.get_object()
        decision = request.data.get("decision")
        notes = request.data.get("decision_notes", "")
        appeal.status = BehaviorAppeal.Status.UNDER_REVIEW
        appeal.reviewed_by = request.user
        appeal.reviewed_at = timezone.now()
        appeal.decision = decision
        appeal.decision_notes = notes
        appeal.save()
        return Response({"status": "reviewed", "decision": decision})


class ParentNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = ParentNotificationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__full_name", "subject"]
    filterset_fields = ["student", "notification_type", "status", "delivery_method"]

    def get_queryset(self):
        return ParentNotification.objects.filter(school=self.request.user.school).select_related(
            "student__user", "sent_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        notification = serializer.save(
            school=self.request.user.school,
            sent_by=self.request.user,
            status=ParentNotification.Status.SENT,
            sent_at=timezone.now(),
        )
        # Update related incident/consequence notification status
        if notification.incident:
            notification.incident.parents_notified = True
            notification.incident.parents_notified_at = timezone.now()
            notification.incident.save()
        if notification.consequence:
            notification.consequence.parents_notified = True
            notification.consequence.parents_notified_at = timezone.now()
            notification.consequence.save()


class BehaviorAnalyticsViewSet(viewsets.ModelViewSet):
    serializer_class = BehaviorAnalyticsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["report_type"]

    def get_queryset(self):
        return BehaviorAnalytics.objects.filter(school=self.request.user.school).select_related("generated_by")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, generated_by=self.request.user)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolAdmin])
    def generate_report(self, request):
        """Generate a behavior analytics report."""
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        report_type = request.data.get("report_type", "custom")

        if not start_date or not end_date:
            return Response({"error": "start_date and end_date required"}, status=status.HTTP_400_BAD_REQUEST)

        from datetime import date

        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)

        # Gather stats
        incidents = Incident.objects.filter(
            school=request.user.school,
            occurred_at__date__gte=start,
            occurred_at__date__lte=end,
        )

        total_incidents = incidents.count()
        incidents_by_severity = dict(
            incidents.values_list("severity").annotate(count=Count("id")).values_list("severity", "count")
        )
        incidents_by_type = dict(
            incidents.values_list("incident_type").annotate(count=Count("id")).values_list("incident_type", "count")
        )

        # Points stats
        points = BehaviorPoint.objects.filter(
            school=request.user.school,
            created_at__date__gte=start,
            created_at__date__lte=end,
        )
        total_awarded = (
            points.filter(point_type=BehaviorPoint.PointType.EARNED).aggregate(total=Sum("points"))["total"] or 0
        )
        total_deducted = (
            points.filter(point_type=BehaviorPoint.PointType.DEDUCTED).aggregate(total=Sum("points"))["total"] or 0
        )

        # Consequences
        consequences = BehaviorConsequence.objects.filter(
            school=request.user.school,
            created_at__date__gte=start,
            created_at__date__lte=end,
        )
        total_consequences = consequences.count()
        consequences_by_type = dict(
            consequences.values_list("consequence_type")
            .annotate(count=Count("id"))
            .values_list("consequence_type", "count")
        )

        # Suspension days
        suspensions = SuspensionTracking.objects.filter(
            school=request.user.school,
            start_date__gte=start,
            start_date__lte=end,
        )
        total_suspension_days = sum(s.duration_days for s in suspensions)

        # Detention hours
        detentions = DetentionTracking.objects.filter(
            school=request.user.school,
            scheduled_date__gte=start,
            scheduled_date__lte=end,
            status=DetentionTracking.Status.COMPLETED,
        )
        total_detention_hours = sum(
            (d.end_time.hour * 60 + d.end_time.minute - d.start_time.hour * 60 - d.start_time.minute) / 60
            for d in detentions
        )

        analytics = BehaviorAnalytics.objects.create(
            school=request.user.school,
            report_type=report_type,
            start_date=start,
            end_date=end,
            total_incidents=total_incidents,
            incidents_by_severity=incidents_by_severity,
            incidents_by_type=incidents_by_type,
            total_points_awarded=total_awarded,
            total_points_deducted=total_deducted,
            total_consequences=total_consequences,
            consequences_by_type=consequences_by_type,
            total_suspension_days=total_suspension_days,
            total_detention_hours=int(total_detention_hours),
            generated_by=request.user,
        )

        serializer = self.get_serializer(analytics)
        return Response(serializer.data)
