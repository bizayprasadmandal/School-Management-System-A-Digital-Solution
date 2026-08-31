"""Behavior Management serializers."""

from rest_framework import serializers

from .models import (
    BehaviorAcademicCorrelation,
    BehaviorAlert,
    BehaviorAnalytics,
    BehaviorAppeal,
    BehaviorAttendanceLink,
    BehaviorAutoEscalation,
    BehaviorBadge,
    BehaviorBadgeAward,
    BehaviorCategory,
    BehaviorConsequence,
    BehaviorContract,
    BehaviorDataVisualization,
    BehaviorEscalationLog,
    BehaviorEvidence,
    BehaviorGoal,
    BehaviorHouse,
    BehaviorHouseMember,
    BehaviorInterventionPlan,
    BehaviorLeaderboard,
    BehaviorMerit,
    BehaviorMTSS,
    BehaviorParentPortal,
    BehaviorPoint,
    BehaviorPointBalance,
    BehaviorPointsRedemption,
    BehaviorPolicyTemplate,
    BehaviorPredictiveAnalytics,
    BehaviorReportCard,
    BehaviorReward,
    BehaviorRubric,
    BehaviorRubricLevel,
    BehaviorSMSAlert,
    BehaviorStaffDashboard,
    BehaviorStreak,
    BehaviorStreakChallenge,
    BehaviorTrainingCompletion,
    BehaviorTrainingMaterial,
    DetentionTracking,
    DigitalHallPass,
    Incident,
    ParentNotification,
    Referral,
    SELCheckIn,
    SELCheckInResponse,
    SELSurvey,
    SELSurveyResponse,
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


class BehaviorRewardSerializer(serializers.ModelSerializer):
    reward_type_display = serializers.CharField(source="get_reward_type_display", read_only=True)
    availability_display = serializers.CharField(source="get_availability_display", read_only=True)
    is_available = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorReward
        fields = [
            "id",
            "name",
            "description",
            "reward_type",
            "reward_type_display",
            "points_cost",
            "availability",
            "availability_display",
            "stock_quantity",
            "max_per_student",
            "total_redeemed",
            "image_url",
            "available_from",
            "available_until",
            "requires_approval",
            "is_active",
            "is_available",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total_redeemed", "created_at", "updated_at"]


class BehaviorPointsRedemptionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    reward_name = serializers.CharField(source="reward.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorPointsRedemption
        fields = [
            "id",
            "student",
            "student_name",
            "reward",
            "reward_name",
            "points_spent",
            "status",
            "status_display",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "rejection_reason",
            "fulfilled_at",
            "notes",
            "redeemed_at",
        ]
        read_only_fields = ["id", "approved_at", "fulfilled_at", "redeemed_at"]


class BehaviorHouseSerializer(serializers.ModelSerializer):
    captain_name = serializers.CharField(source="captain.user.full_name", read_only=True, default=None)
    vice_captain_name = serializers.CharField(source="vice_captain.user.full_name", read_only=True, default=None)
    faculty_advisor_name = serializers.CharField(source="faculty_advisor.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorHouse
        fields = [
            "id",
            "name",
            "description",
            "color",
            "mascot",
            "captain",
            "captain_name",
            "vice_captain",
            "vice_captain_name",
            "faculty_advisor",
            "faculty_advisor_name",
            "total_points",
            "member_count",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total_points", "member_count", "created_at", "updated_at"]


class BehaviorHouseMemberSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    house_name = serializers.CharField(source="house.name", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = BehaviorHouseMember
        fields = [
            "id",
            "house",
            "house_name",
            "student",
            "student_name",
            "role",
            "role_display",
            "joined_at",
            "is_active",
        ]
        read_only_fields = ["id", "joined_at"]


class BehaviorLeaderboardSerializer(serializers.ModelSerializer):
    leaderboard_type_display = serializers.CharField(source="get_leaderboard_type_display", read_only=True)
    time_period_display = serializers.CharField(source="get_time_period_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorLeaderboard
        fields = [
            "id",
            "name",
            "leaderboard_type",
            "leaderboard_type_display",
            "time_period",
            "time_period_display",
            "start_date",
            "end_date",
            "leaderboard_data",
            "is_published",
            "show_on_dashboard",
            "total_entries",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "leaderboard_data", "total_entries", "created_at", "updated_at"]


class BehaviorReportCardSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    report_period_display = serializers.CharField(source="get_report_period_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    generated_by_name = serializers.CharField(source="generated_by.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorReportCard
        fields = [
            "id",
            "student",
            "student_name",
            "report_period",
            "report_period_display",
            "start_date",
            "end_date",
            "total_incidents",
            "total_merits",
            "total_points_earned",
            "total_points_deducted",
            "net_points",
            "total_detentions",
            "total_suspensions",
            "total_tardies",
            "behavior_score",
            "behavior_trend",
            "strengths",
            "areas_for_growth",
            "teacher_comments",
            "admin_comments",
            "status",
            "status_display",
            "generated_at",
            "sent_to_parent",
            "sent_at",
            "generated_by",
            "generated_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "generated_at", "sent_at", "created_at"]


class BehaviorInterventionPlanSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    plan_type_display = serializers.CharField(source="get_plan_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    review_frequency_display = serializers.CharField(source="get_review_frequency_display", read_only=True)
    case_manager_name = serializers.CharField(source="case_manager.full_name", read_only=True, default=None)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorInterventionPlan
        fields = [
            "id",
            "student",
            "student_name",
            "plan_type",
            "plan_type_display",
            "title",
            "description",
            "target_behavior",
            "antecedents",
            "behaviors",
            "consequences",
            "function_of_behavior",
            "prevention_strategies",
            "teaching_strategies",
            "reinforcement_strategies",
            "crisis_plan",
            "team_members",
            "case_manager",
            "case_manager_name",
            "start_date",
            "end_date",
            "review_frequency",
            "review_frequency_display",
            "next_review_date",
            "goals_met",
            "goals_remaining",
            "progress_notes",
            "status",
            "status_display",
            "parent_signature_required",
            "parent_signed",
            "parent_signed_at",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "parent_signed", "parent_signed_at", "created_at", "updated_at"]


class BehaviorMTSSSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    tier_level_display = serializers.CharField(source="get_tier_level_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    referred_by_name = serializers.CharField(source="referred_by.full_name", read_only=True, default=None)
    case_manager_name = serializers.CharField(source="case_manager.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorMTSS
        fields = [
            "id",
            "student",
            "student_name",
            "tier_level",
            "tier_level_display",
            "status",
            "status_display",
            "referral_reason",
            "referral_date",
            "referred_by",
            "referred_by_name",
            "interventions",
            "supports",
            "goals",
            "progress_data",
            "baseline_date",
            "baseline_notes",
            "start_date",
            "review_date",
            "end_date",
            "case_manager",
            "case_manager_name",
            "team_members",
            "outcome_notes",
            "outcome_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SELCheckInSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    mood_display = serializers.CharField(source="get_mood_display", read_only=True)
    responded_by_name = serializers.CharField(source="responded_by.full_name", read_only=True, default=None)

    class Meta:
        model = SELCheckIn
        fields = [
            "id",
            "student",
            "student_name",
            "mood",
            "mood_display",
            "energy_level",
            "stress_level",
            "how_are_you_feeling",
            "anything_else",
            "needs_help",
            "help_type",
            "sleep_quality",
            "ate_breakfast",
            "staff_response",
            "responded_by",
            "responded_by_name",
            "responded_at",
            "follow_up_needed",
            "follow_up_completed",
            "check_in_date",
            "check_in_time",
            "created_at",
        ]
        read_only_fields = ["id", "check_in_time", "created_at"]


class SELCheckInResponseSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source="staff.full_name", read_only=True)

    class Meta:
        model = SELCheckInResponse
        fields = [
            "id",
            "check_in",
            "staff",
            "staff_name",
            "response",
            "action_taken",
            "follow_up_required",
            "follow_up_date",
            "follow_up_completed",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BehaviorStaffDashboardSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source="staff.full_name", read_only=True)

    class Meta:
        model = BehaviorStaffDashboard
        fields = [
            "id",
            "staff",
            "staff_name",
            "incidents_today",
            "points_given_today",
            "referrals_received_today",
            "hall_passes_active",
            "incidents_this_week",
            "points_given_this_week",
            "class_points_data",
            "top_students",
            "students_needing_attention",
            "pending_alerts",
            "pending_referrals",
            "recent_actions",
            "favorite_quick_actions",
            "last_refreshed",
            "created_at",
        ]
        read_only_fields = ["id", "last_refreshed", "created_at"]


class BehaviorBadgeSerializer(serializers.ModelSerializer):
    badge_type_display = serializers.CharField(source="get_badge_type_display", read_only=True)

    class Meta:
        model = BehaviorBadge
        fields = [
            "id",
            "name",
            "description",
            "badge_type",
            "badge_type_display",
            "criteria_description",
            "points_required",
            "streak_required",
            "incidents_allowed",
            "icon_url",
            "color",
            "total_earned",
            "is_active",
            "is_hidden",
            "points_value",
            "created_at",
        ]
        read_only_fields = ["id", "total_earned", "created_at"]


class BehaviorBadgeAwardSerializer(serializers.ModelSerializer):
    badge_name = serializers.CharField(source="badge.name", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    awarded_by_name = serializers.CharField(source="awarded_by.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorBadgeAward
        fields = [
            "id",
            "badge",
            "badge_name",
            "student",
            "student_name",
            "awarded_at",
            "awarded_by",
            "awarded_by_name",
            "reason",
            "notified",
            "notified_at",
            "is_public",
            "shared_to_feed",
        ]
        read_only_fields = ["id", "awarded_at"]


class BehaviorSMSAlertSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    alert_type_display = serializers.CharField(source="get_alert_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = BehaviorSMSAlert
        fields = [
            "id",
            "student",
            "student_name",
            "incident",
            "alert_type",
            "alert_type_display",
            "parent_phone",
            "parent_name",
            "message",
            "status",
            "status_display",
            "sent_at",
            "delivered_at",
            "error_message",
            "sent_by",
            "created_at",
        ]
        read_only_fields = ["id", "sent_at", "delivered_at", "created_at"]


class BehaviorAutoEscalationSerializer(serializers.ModelSerializer):
    trigger_type_display = serializers.CharField(source="get_trigger_type_display", read_only=True)
    escalation_action_display = serializers.CharField(source="get_escalation_action_display", read_only=True)

    class Meta:
        model = BehaviorAutoEscalation
        fields = [
            "id",
            "name",
            "description",
            "trigger_type",
            "trigger_type_display",
            "trigger_value",
            "trigger_window_days",
            "incident_type_filter",
            "severity_filter",
            "escalation_action",
            "escalation_action_display",
            "action_description",
            "is_active",
            "priority",
            "times_triggered",
            "last_triggered_at",
            "created_at",
        ]
        read_only_fields = ["id", "times_triggered", "last_triggered_at", "created_at"]


class BehaviorEscalationLogSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    escalation_rule_name = serializers.CharField(source="escalation_rule.name", read_only=True)
    action_taken_by_name = serializers.CharField(source="action_taken_by.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorEscalationLog
        fields = [
            "id",
            "escalation_rule",
            "escalation_rule_name",
            "student",
            "student_name",
            "triggered_at",
            "trigger_data",
            "action_taken",
            "action_taken_by",
            "action_taken_by_name",
            "resolved",
            "resolved_at",
            "notes",
        ]
        read_only_fields = ["id", "triggered_at"]


class BehaviorAttendanceLinkSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    link_type_display = serializers.CharField(source="get_link_type_display", read_only=True)

    class Meta:
        model = BehaviorAttendanceLink
        fields = [
            "id",
            "student",
            "student_name",
            "link_type",
            "link_type_display",
            "attendance_record_id",
            "incident",
            "behavior_point",
            "attendance_date",
            "points_adjusted",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BehaviorAcademicCorrelationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    correlation_type_display = serializers.CharField(source="get_correlation_type_display", read_only=True)

    class Meta:
        model = BehaviorAcademicCorrelation
        fields = [
            "id",
            "student",
            "student_name",
            "correlation_type",
            "correlation_type_display",
            "start_date",
            "end_date",
            "behavior_score",
            "total_incidents",
            "total_merits",
            "total_points",
            "gpa",
            "gpa_change",
            "grade_average",
            "assignment_completion_rate",
            "correlation_strength",
            "notes",
            "generated_at",
        ]
        read_only_fields = ["id", "generated_at"]


class BehaviorDataVisualizationSerializer(serializers.ModelSerializer):
    chart_type_display = serializers.CharField(source="get_chart_type_display", read_only=True)

    class Meta:
        model = BehaviorDataVisualization
        fields = [
            "id",
            "chart_type",
            "chart_type_display",
            "title",
            "chart_data",
            "labels",
            "datasets",
            "date_range_start",
            "date_range_end",
            "grade_filter",
            "teacher_filter",
            "is_public",
            "refresh_interval_hours",
            "last_refreshed",
            "created_at",
        ]
        read_only_fields = ["id", "last_refreshed", "created_at"]


class BehaviorPredictiveAnalyticsSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    prediction_type_display = serializers.CharField(source="get_prediction_type_display", read_only=True)
    risk_level_display = serializers.CharField(source="get_risk_level_display", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorPredictiveAnalytics
        fields = [
            "id",
            "student",
            "student_name",
            "prediction_type",
            "prediction_type_display",
            "risk_level",
            "risk_level_display",
            "risk_score",
            "risk_factors",
            "protective_factors",
            "predicted_outcome",
            "confidence_level",
            "recommended_interventions",
            "recommended_actions",
            "prediction_date",
            "valid_until",
            "reviewed",
            "reviewed_by",
            "reviewed_by_name",
            "reviewed_at",
            "action_taken",
            "created_at",
        ]
        read_only_fields = ["id", "prediction_date", "created_at"]


class SELSurveySerializer(serializers.ModelSerializer):
    survey_type_display = serializers.CharField(source="get_survey_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = SELSurvey
        fields = [
            "id",
            "title",
            "description",
            "survey_type",
            "survey_type_display",
            "status",
            "status_display",
            "questions",
            "target_grades",
            "start_date",
            "end_date",
            "total_responses",
            "average_scores",
            "is_anonymous",
            "allow_multiple_submissions",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total_responses", "created_at", "updated_at"]


class SELSurveyResponseSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    survey_title = serializers.CharField(source="survey.title", read_only=True)

    class Meta:
        model = SELSurveyResponse
        fields = [
            "id",
            "survey",
            "survey_title",
            "student",
            "student_name",
            "responses",
            "overall_score",
            "needs_follow_up",
            "follow_up_notes",
            "follow_up_completed",
            "submitted_at",
        ]
        read_only_fields = ["id", "submitted_at"]


class BehaviorTrainingMaterialSerializer(serializers.ModelSerializer):
    material_type_display = serializers.CharField(source="get_material_type_display", read_only=True)
    audience_display = serializers.CharField(source="get_audience_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorTrainingMaterial
        fields = [
            "id",
            "title",
            "description",
            "material_type",
            "material_type_display",
            "audience",
            "audience_display",
            "file_url",
            "external_url",
            "content_text",
            "duration_minutes",
            "tags",
            "views_count",
            "completions_count",
            "is_required",
            "is_active",
            "due_date",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "views_count", "completions_count", "created_at", "updated_at"]


class BehaviorTrainingCompletionSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source="staff.full_name", read_only=True)
    material_title = serializers.CharField(source="material.title", read_only=True)

    class Meta:
        model = BehaviorTrainingCompletion
        fields = [
            "id",
            "material",
            "material_title",
            "staff",
            "staff_name",
            "status",
            "started_at",
            "completed_at",
            "score",
            "notes",
        ]
        read_only_fields = ["id"]


class BehaviorPolicyTemplateSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorPolicyTemplate
        fields = [
            "id",
            "title",
            "description",
            "category",
            "category_display",
            "content",
            "version",
            "effective_date",
            "review_date",
            "downloads_count",
            "is_template",
            "is_active",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "downloads_count", "created_at", "updated_at"]


class BehaviorStreakChallengeSerializer(serializers.ModelSerializer):
    challenge_type_display = serializers.CharField(source="get_challenge_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = BehaviorStreakChallenge
        fields = [
            "id",
            "title",
            "description",
            "challenge_type",
            "challenge_type_display",
            "status",
            "status_display",
            "target_streak",
            "streak_unit",
            "start_date",
            "end_date",
            "completion_reward_points",
            "completion_reward_badge",
            "top_reward_points",
            "total_participants",
            "total_completions",
            "leaderboard",
            "is_class_competition",
            "is_house_competition",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "total_participants",
            "total_completions",
            "leaderboard",
            "created_at",
            "updated_at",
        ]


class BehaviorParentPortalSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent_user.full_name", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    access_level_display = serializers.CharField(source="get_access_level_display", read_only=True)

    class Meta:
        model = BehaviorParentPortal
        fields = [
            "id",
            "school",
            "parent_user",
            "parent_name",
            "student",
            "student_name",
            "access_level",
            "access_level_display",
            "show_incidents",
            "show_points",
            "show_consequences",
            "show_report_cards",
            "show_merits",
            "show_streaks",
            "show_goals",
            "email_notifications",
            "sms_notifications",
            "push_notifications",
            "notify_on_incident",
            "notify_on_consequence",
            "notify_on_positive",
            "is_active",
            "last_login_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "last_login_at", "created_at", "updated_at"]
