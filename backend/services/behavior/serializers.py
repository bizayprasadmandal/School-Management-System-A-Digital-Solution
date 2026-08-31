"""Behavior Management serializers."""

from rest_framework import serializers

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


class BehaviorCategorySerializer(serializers.ModelSerializer):
    category_type_display = serializers.CharField(source="get_category_type_display", read_only=True)

    class Meta:
        model = BehaviorCategory
        fields = [
            "id",
            "name",
            "description",
            "category_type",
            "category_type_display",
            "points_value",
            "is_active",
            "requires_incident",
            "color",
            "icon",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class IncidentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    reported_by_name = serializers.CharField(source="reported_by.full_name", read_only=True)
    severity_display = serializers.CharField(source="get_severity_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)

    class Meta:
        model = Incident
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "school",
            "reported_by",
            "parents_notified",
            "parents_notified_at",
        ]

    def validate_student(self, value):
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Student not found in your school.")
        return value


class ReferralSerializer(serializers.ModelSerializer):
    referred_to_name = serializers.CharField(source="referred_to.full_name", read_only=True)
    referred_by_name = serializers.CharField(source="referred_by.full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Referral
        fields = "__all__"
        read_only_fields = ["id", "created_at", "referred_by"]

    def validate_incident(self, value):
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Incident not found in your school.")
        return value

    def validate_referred_to(self, value):
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Referred-to user must be in your school.")
        return value


class BehaviorPointSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)
    awarded_by_name = serializers.CharField(source="awarded_by.full_name", read_only=True, default=None)
    point_type_display = serializers.CharField(source="get_point_type_display", read_only=True)

    class Meta:
        model = BehaviorPoint
        fields = [
            "id",
            "student",
            "student_name",
            "category",
            "category_name",
            "points",
            "point_type",
            "point_type_display",
            "reason",
            "awarded_by",
            "awarded_by_name",
            "incident",
            "is_redeemed",
            "redeemed_at",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "is_redeemed", "redeemed_at", "created_at"]


class BehaviorPointBalanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = BehaviorPointBalance
        fields = [
            "id",
            "student",
            "student_name",
            "total_earned",
            "total_deducted",
            "current_balance",
            "lifetime_earned",
            "lifetime_deducted",
            "last_activity_at",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


class BehaviorConsequenceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    consequence_type_display = serializers.CharField(source="get_consequence_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    issued_by_name = serializers.CharField(source="issued_by.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorConsequence
        fields = [
            "id",
            "student",
            "student_name",
            "incident",
            "consequence_type",
            "consequence_type_display",
            "description",
            "status",
            "status_display",
            "issued_date",
            "start_date",
            "end_date",
            "issued_by",
            "issued_by_name",
            "duration_hours",
            "duration_days",
            "location",
            "conditions",
            "notes",
            "parents_notified",
            "parents_notified_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "parents_notified", "parents_notified_at", "created_at", "updated_at"]


class BehaviorMeritSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    merit_type_display = serializers.CharField(source="get_merit_type_display", read_only=True)
    awarded_by_name = serializers.CharField(source="awarded_by.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorMerit
        fields = [
            "id",
            "student",
            "student_name",
            "merit_type",
            "merit_type_display",
            "title",
            "description",
            "points",
            "awarded_by",
            "awarded_by_name",
            "incident",
            "is_public",
            "certificate_generated",
            "awarded_date",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class DetentionTrackingSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    detention_type_display = serializers.CharField(source="get_detention_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    supervisor_name = serializers.CharField(source="supervisor.full_name", read_only=True, default=None)

    class Meta:
        model = DetentionTracking
        fields = [
            "id",
            "student",
            "student_name",
            "detention_type",
            "detention_type_display",
            "consequence",
            "scheduled_date",
            "start_time",
            "end_time",
            "location",
            "status",
            "status_display",
            "supervisor",
            "supervisor_name",
            "attended",
            "attended_at",
            "notes",
            "parents_notified",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SuspensionTrackingSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    suspension_type_display = serializers.CharField(source="get_suspension_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    issued_by_name = serializers.CharField(source="issued_by.full_name", read_only=True, default=None)
    duration_days_computed = serializers.IntegerField(source="duration_days", read_only=True)

    class Meta:
        model = SuspensionTracking
        fields = [
            "id",
            "student",
            "student_name",
            "suspension_type",
            "suspension_type_display",
            "consequence",
            "incident",
            "start_date",
            "end_date",
            "actual_return_date",
            "status",
            "status_display",
            "conditions_for_return",
            "meeting_required",
            "meeting_date",
            "meeting_notes",
            "issued_by",
            "issued_by_name",
            "duration_days_computed",
            "parents_notified",
            "parents_notified_at",
            "parent_signature_required",
            "parent_signature_obtained",
            "make_up_work_required",
            "make_up_work_notes",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "parents_notified", "parents_notified_at", "created_at", "updated_at"]


class BehaviorContractSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorContract
        fields = [
            "id",
            "student",
            "student_name",
            "incident",
            "title",
            "description",
            "goals",
            "consequences_for_violation",
            "rewards_for_compliance",
            "start_date",
            "end_date",
            "review_dates",
            "student_signed",
            "student_signed_at",
            "parent_signed",
            "parent_signed_at",
            "administrator_signed",
            "administrator_signed_at",
            "status",
            "status_display",
            "progress_notes",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student_signed",
            "student_signed_at",
            "parent_signed",
            "parent_signed_at",
            "administrator_signed",
            "administrator_signed_at",
            "created_at",
            "updated_at",
        ]


class WitnessStatementSerializer(serializers.ModelSerializer):
    collected_by_name = serializers.CharField(source="collected_by.full_name", read_only=True, default=None)

    class Meta:
        model = WitnessStatement
        fields = [
            "id",
            "incident",
            "witness_type",
            "witness_name",
            "witness_student",
            "witness_contact",
            "statement",
            "statement_date",
            "collected_by",
            "collected_by_name",
            "is_confidential",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BehaviorEvidenceSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source="uploaded_by.full_name", read_only=True, default=None)
    evidence_type_display = serializers.CharField(source="get_evidence_type_display", read_only=True)

    class Meta:
        model = BehaviorEvidence
        fields = [
            "id",
            "incident",
            "evidence_type",
            "evidence_type_display",
            "title",
            "description",
            "file_url",
            "file_size",
            "uploaded_by",
            "uploaded_by_name",
            "is_confidential",
            "uploaded_at",
        ]
        read_only_fields = ["id", "uploaded_at"]


class BehaviorRubricSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)
    levels = serializers.SerializerMethodField()

    class Meta:
        model = BehaviorRubric
        fields = [
            "id",
            "name",
            "description",
            "min_score",
            "max_score",
            "applies_to",
            "is_active",
            "created_by",
            "created_by_name",
            "levels",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_levels(self, obj):
        return BehaviorRubricLevelSerializer(obj.levels.all(), many=True).data


class BehaviorRubricLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BehaviorRubricLevel
        fields = [
            "id",
            "rubric",
            "score",
            "label",
            "description",
            "color",
        ]
        read_only_fields = ["id"]


class DigitalHallPassSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    pass_type_display = serializers.CharField(source="get_pass_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True, default=None)

    class Meta:
        model = DigitalHallPass
        fields = [
            "id",
            "student",
            "student_name",
            "pass_type",
            "pass_type_display",
            "from_class",
            "to_destination",
            "approved_by",
            "approved_by_name",
            "issued_at",
            "expected_return_at",
            "actual_return_at",
            "status",
            "status_display",
            "is_late",
            "minutes_late",
            "reason",
            "notes",
        ]
        read_only_fields = ["id", "issued_at"]


class TardyTrackingSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    tardy_type_display = serializers.CharField(source="get_tardy_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True, default=None)

    class Meta:
        model = TardyTracking
        fields = [
            "id",
            "student",
            "student_name",
            "tardy_type",
            "tardy_type_display",
            "date",
            "scheduled_time",
            "arrival_time",
            "minutes_late",
            "class_name",
            "teacher",
            "teacher_name",
            "status",
            "status_display",
            "reason",
            "parent_contacted",
            "is_part_of_pattern",
            "pattern_notes",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BehaviorGoalSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    goal_type_display = serializers.CharField(source="get_goal_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model = BehaviorGoal
        fields = [
            "id",
            "student",
            "student_name",
            "goal_type",
            "goal_type_display",
            "title",
            "description",
            "target_value",
            "current_value",
            "progress_percentage",
            "start_date",
            "end_date",
            "status",
            "status_display",
            "created_by",
            "created_by_name",
            "support_plan",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BehaviorStreakSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    streak_type_display = serializers.CharField(source="get_streak_type_display", read_only=True)

    class Meta:
        model = BehaviorStreak
        fields = [
            "id",
            "student",
            "student_name",
            "streak_type",
            "streak_type_display",
            "current_streak",
            "longest_streak",
            "streak_unit",
            "streak_started_at",
            "last_activity_at",
            "milestone_7",
            "milestone_30",
            "milestone_90",
            "milestone_180",
            "milestone_365",
            "reward_earned",
            "reward_description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BehaviorAlertSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    alert_type_display = serializers.CharField(source="get_alert_type_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    acknowledged_by_name = serializers.CharField(source="acknowledged_by.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorAlert
        fields = [
            "id",
            "student",
            "student_name",
            "alert_type",
            "alert_type_display",
            "priority",
            "priority_display",
            "title",
            "message",
            "incident",
            "status",
            "status_display",
            "acknowledged_by",
            "acknowledged_by_name",
            "acknowledged_at",
            "resolved_at",
            "notification_sent",
            "notification_sent_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "acknowledged_at",
            "resolved_at",
            "notification_sent",
            "notification_sent_at",
            "created_at",
        ]


class BehaviorAppealSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    appeal_type_display = serializers.CharField(source="get_appeal_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    decision_display = serializers.CharField(source="get_decision_display", read_only=True, default=None)
    reviewed_by_name = serializers.CharField(source="reviewed_by.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorAppeal
        fields = [
            "id",
            "student",
            "student_name",
            "appeal_type",
            "appeal_type_display",
            "incident",
            "consequence",
            "suspension",
            "reason",
            "supporting_evidence",
            "requested_outcome",
            "status",
            "status_display",
            "reviewed_by",
            "reviewed_by_name",
            "reviewed_at",
            "decision",
            "decision_display",
            "decision_notes",
            "parent_notified",
            "parent_statement",
            "submitted_at",
            "hearing_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "reviewed_at", "submitted_at", "created_at", "updated_at"]


class ParentNotificationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    notification_type_display = serializers.CharField(source="get_notification_type_display", read_only=True)
    delivery_method_display = serializers.CharField(source="get_delivery_method_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    sent_by_name = serializers.CharField(source="sent_by.full_name", read_only=True, default=None)

    class Meta:
        model = ParentNotification
        fields = [
            "id",
            "student",
            "student_name",
            "notification_type",
            "notification_type_display",
            "delivery_method",
            "delivery_method_display",
            "incident",
            "consequence",
            "subject",
            "message",
            "parent_email",
            "parent_phone",
            "status",
            "status_display",
            "sent_at",
            "delivered_at",
            "acknowledged_at",
            "parent_response",
            "response_received_at",
            "sent_by",
            "sent_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "sent_at", "delivered_at", "acknowledged_at", "response_received_at", "created_at"]


class BehaviorAnalyticsSerializer(serializers.ModelSerializer):
    report_type_display = serializers.CharField(source="get_report_type_display", read_only=True)
    generated_by_name = serializers.CharField(source="generated_by.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorAnalytics
        fields = [
            "id",
            "report_type",
            "report_type_display",
            "start_date",
            "end_date",
            "total_incidents",
            "incidents_by_severity",
            "incidents_by_type",
            "incidents_by_grade",
            "incidents_by_day",
            "total_points_awarded",
            "total_points_deducted",
            "average_points_per_student",
            "total_consequences",
            "consequences_by_type",
            "total_suspension_days",
            "total_detention_hours",
            "top_earners",
            "students_needing_support",
            "comparison_to_previous",
            "generated_by",
            "generated_by_name",
            "generated_at",
            "notes",
        ]
        read_only_fields = ["id", "generated_at"]
