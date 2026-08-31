"""Admissions serializers."""

from rest_framework import serializers

from .models import (
    AdmissionsEmailNotification,
    AdmissionsPipeline,
    AdmissionsReport,
    AdmissionsSMSNotification,
    Application,
    ApplicationDocument,
    ApplicationFee,
    ApplicationReview,
    ApplicationTemplate,
    ApplicationTimelineEvent,
    BulkApplicationImport,
    EnrollmentConfirmation,
    EnrollmentIntake,
    InterviewSchedule,
    MeritList,
    MeritListEntry,
    ReEnrollment,
    WaitlistManagement,
)


class ApplicationTimelineSerializer(serializers.ModelSerializer):
    stage_display = serializers.CharField(source="get_stage_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default="")

    class Meta:
        model = ApplicationTimelineEvent
        fields = [
            "id",
            "stage",
            "stage_display",
            "note",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = fields


class EnrollmentIntakeSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = EnrollmentIntake
        fields = [
            "id",
            "name",
            "academic_year",
            "application_start",
            "application_end",
            "enrollment_date",
            "status",
            "status_display",
            "max_applications",
            "description",
            "application_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_application_count(self, obj):
        return getattr(obj, "application_count", obj.applications.count())


class ApplicationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDocument
        fields = [
            "id",
            "application",
            "document_type",
            "file_url",
            "file_name",
            "uploaded_at",
            "is_verified",
            "notes",
        ]
        read_only_fields = ["id", "uploaded_at"]


class ApplicationReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source="reviewer.full_name", read_only=True)

    class Meta:
        model = ApplicationReview
        fields = [
            "id",
            "application",
            "reviewer",
            "reviewer_name",
            "score",
            "strengths",
            "weaknesses",
            "recommendation",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "reviewer", "created_at"]


class ApplicationSerializer(serializers.ModelSerializer):
    intake_name = serializers.CharField(source="intake.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    full_name = serializers.SerializerMethodField()
    documents = ApplicationDocumentSerializer(many=True, read_only=True)
    reviews = ApplicationReviewSerializer(many=True, read_only=True)
    timeline = ApplicationTimelineSerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "intake",
            "intake_name",
            "application_number",
            "status",
            "status_display",
            "first_name",
            "last_name",
            "middle_name",
            "full_name",
            "date_of_birth",
            "gender",
            "nationality",
            "email",
            "phone",
            "address",
            "city",
            "state",
            "postal_code",
            "previous_school",
            "previous_grade",
            "applying_for_grade",
            "gpa",
            "guardian_name",
            "guardian_phone",
            "guardian_email",
            "guardian_relation",
            "source",
            "submitted_at",
            "reviewed_by",
            "review_notes",
            "tour_date",
            "toured_at",
            "offer_sent_at",
            "offer_deadline",
            "offer_accepted_at",
            "linked_student",
            "documents",
            "reviews",
            "timeline",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "application_number", "created_at", "updated_at"]

    def get_full_name(self, obj):
        parts = [obj.first_name, obj.middle_name, obj.last_name]
        return " ".join(p for p in parts if p)


class ApplicationListSerializer(serializers.ModelSerializer):
    """Lightweight list serializer without nested docs/reviews."""

    intake_name = serializers.CharField(source="intake.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            "id",
            "intake",
            "intake_name",
            "application_number",
            "status",
            "status_display",
            "full_name",
            "email",
            "phone",
            "applying_for_grade",
            "previous_school",
            "submitted_at",
            "created_at",
        ]
        read_only_fields = ["id", "application_number", "created_at"]

    def get_full_name(self, obj):
        parts = [obj.first_name, obj.middle_name, obj.last_name]
        return " ".join(p for p in parts if p)


# =============================================================================
# Application Fees Serializers
# =============================================================================


class ApplicationFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationFee
        fields = [
            "id",
            "application",
            "amount",
            "currency",
            "status",
            "payment_method",
            "transaction_id",
            "payment_date",
            "receipt_number",
            "waiver_reason",
            "waived_by",
            "gateway_response",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Interview Schedule Serializers
# =============================================================================


class InterviewScheduleSerializer(serializers.ModelSerializer):
    interviewer_name = serializers.CharField(source="interviewer.full_name", read_only=True, default=None)

    class Meta:
        model = InterviewSchedule
        fields = [
            "id",
            "application",
            "interview_type",
            "status",
            "scheduled_date",
            "scheduled_time",
            "duration_minutes",
            "location",
            "meeting_link",
            "meeting_id",
            "interviewer",
            "interviewer_name",
            "panel_members",
            "feedback",
            "rating",
            "recommendation",
            "notes",
            "completed_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "completed_at"]


# =============================================================================
# Merit List Serializers
# =============================================================================


class MeritListEntrySerializer(serializers.ModelSerializer):
    application_number = serializers.CharField(source="application.application_number", read_only=True)
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = MeritListEntry
        fields = [
            "id",
            "merit_list",
            "application",
            "application_number",
            "student_name",
            "rank",
            "total_score",
            "status",
            "academic_score",
            "assessment_score",
            "interview_score",
            "extracurricular_score",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_student_name(self, obj):
        app = obj.application
        return f"{app.first_name} {app.last_name}"


class MeritListSerializer(serializers.ModelSerializer):
    entries = MeritListEntrySerializer(many=True, read_only=True)
    published_by_name = serializers.CharField(source="published_by.full_name", read_only=True, default=None)

    class Meta:
        model = MeritList
        fields = [
            "id",
            "name",
            "description",
            "grade",
            "status",
            "total_applicants",
            "total_selected",
            "total_waitlisted",
            "published_at",
            "published_by",
            "published_by_name",
            "entries",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "published_at"]


# =============================================================================
# Waitlist Management Serializers
# =============================================================================


class WaitlistManagementSerializer(serializers.ModelSerializer):
    application_number = serializers.CharField(source="application.application_number", read_only=True)
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = WaitlistManagement
        fields = [
            "id",
            "application",
            "application_number",
            "student_name",
            "position",
            "status",
            "offer_extended_at",
            "offer_expires_at",
            "offer_accepted_at",
            "offer_declined_at",
            "decline_reason",
            "last_notified_at",
            "notification_count",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_student_name(self, obj):
        app = obj.application
        return f"{app.first_name} {app.last_name}"


# =============================================================================
# Enrollment Confirmation Serializers
# =============================================================================


class EnrollmentConfirmationSerializer(serializers.ModelSerializer):
    application_number = serializers.CharField(source="application.application_number", read_only=True)

    class Meta:
        model = EnrollmentConfirmation
        fields = [
            "id",
            "application",
            "application_number",
            "status",
            "confirmation_sent_at",
            "confirmation_deadline",
            "confirmed_at",
            "declined_at",
            "deposit_amount",
            "payment_status",
            "deposit_paid_at",
            "deposit_transaction_id",
            "decline_reason",
            "enrollment_documents",
            "documents_completed",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Admissions Reports Serializers
# =============================================================================


class AdmissionsReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source="generated_by.full_name", read_only=True, default=None)

    class Meta:
        model = AdmissionsReport
        fields = [
            "id",
            "title",
            "report_type",
            "status",
            "period_start",
            "period_end",
            "summary",
            "findings",
            "recommendations",
            "total_applications",
            "total_enrolled",
            "total_rejected",
            "conversion_rate",
            "by_status",
            "by_grade",
            "by_source",
            "by_demographic",
            "generated_by",
            "generated_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Email Notifications Serializers
# =============================================================================


class AdmissionsEmailNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionsEmailNotification
        fields = [
            "id",
            "application",
            "notification_type",
            "status",
            "subject",
            "message",
            "recipient_email",
            "recipient_name",
            "sent_at",
            "opened_at",
            "created_at",
        ]
        read_only_fields = ["id", "sent_at", "opened_at", "created_at"]


# =============================================================================
# SMS Notifications Serializers
# =============================================================================


class AdmissionsSMSNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionsSMSNotification
        fields = [
            "id",
            "application",
            "notification_type",
            "status",
            "message",
            "phone_number",
            "sent_at",
            "delivered_at",
            "created_at",
        ]
        read_only_fields = ["id", "sent_at", "delivered_at", "created_at"]


# =============================================================================
# Re-enrollment Serializers
# =============================================================================


class ReEnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = ReEnrollment
        fields = [
            "id",
            "student",
            "student_name",
            "intake",
            "status",
            "current_grade",
            "next_grade",
            "invited_at",
            "deadline",
            "started_at",
            "completed_at",
            "decline_reason",
            "re_enrollment_fee",
            "fee_paid",
            "notes",
        ]
        read_only_fields = ["id", "invited_at"]


# =============================================================================
# Admissions Pipeline Serializers
# =============================================================================


class AdmissionsPipelineSerializer(serializers.ModelSerializer):
    application_number = serializers.CharField(source="application.application_number", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True, default=None)

    class Meta:
        model = AdmissionsPipeline
        fields = [
            "id",
            "application",
            "application_number",
            "current_stage",
            "inquiry_date",
            "application_date",
            "documentation_date",
            "assessment_date",
            "interview_date",
            "review_date",
            "decision_date",
            "enrollment_date",
            "onboarded_date",
            "assigned_to",
            "assigned_to_name",
            "is_priority",
            "is_hot_lead",
            "lead_source",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Application Templates Serializers
# =============================================================================


class ApplicationTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = ApplicationTemplate
        fields = [
            "id",
            "name",
            "description",
            "intake",
            "required_fields",
            "optional_fields",
            "required_documents",
            "application_fee",
            "currency",
            "allow_late_applications",
            "late_fee_deadline_days",
            "max_applications_per_student",
            "is_active",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Bulk Application Import Serializers
# =============================================================================


class BulkApplicationImportSerializer(serializers.ModelSerializer):
    initiated_by_name = serializers.CharField(source="initiated_by.full_name", read_only=True, default=None)

    class Meta:
        model = BulkApplicationImport
        fields = [
            "id",
            "batch_name",
            "description",
            "status",
            "total_rows",
            "imported_count",
            "failed_count",
            "errors",
            "error_file_url",
            "initiated_by",
            "initiated_by_name",
            "initiated_at",
            "completed_at",
            "notes",
        ]
        read_only_fields = ["id", "initiated_at", "completed_at"]
