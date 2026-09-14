"""Serializers for admissions."""

from rest_framework import serializers

from .models import (
    AdmissionAgreement,
    AdmissionCommunicationLog,
    AdmissionDecision,
    AdmissionDocumentChecklist,
    AdmissionDocumentVerification,
    AdmissionFunnelSnapshot,
    AdmissionMarketingSource,
    AdmissionPolicy,
    AdmissionPredictionModel,
    AdmissionReminder,
    AdmissionsEmailNotification,
    AdmissionsPipeline,
    AdmissionsReport,
    AdmissionsSMSNotification,
    AdmissionTrendAnalysis,
    AgreementSignature,
    Application,
    ApplicationDocument,
    ApplicationFee,
    ApplicationReview,
    ApplicationTemplate,
    ApplicationTimelineEvent,
    BulkApplicationImport,
    CampusVisit,
    EnrollmentConfirmation,
    EnrollmentIntake,
    EntranceAssessment,
    GradeLevelCapacity,
    InterviewSchedule,
    MeritList,
    MeritListEntry,
    OpenHouseEvent,
    OpenHouseRegistration,
    ReEnrollment,
    Scholarship,
    ScholarshipApplication,
    SiblingGroup,
    SiblingRecord,
    TransferStudent,
    WaitlistManagement,
)


class EnrollmentIntakeSerializer(serializers.ModelSerializer):
    application_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = EnrollmentIntake
        fields = [
            "id",
            "school",
            "id",
            "name",
            "academic_year",
            "application_start",
            "application_end",
            "enrollment_date",
            "status",
            "max_applications",
            "description",
            "application_count",
            "created_at",
        ]
        read_only_fields = ["id", "school", "created_at"]


class ApplicationSerializer(serializers.ModelSerializer):
    timeline = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            "id",
            "school",
            "id",
            "intake",
            "application_number",
            "status",
            "first_name",
            "last_name",
            "middle_name",
            "date_of_birth",
            "gender",
            "nationality",
            "email",
            "phone",
            # CRM pipeline fields (populated by submit / tour / offer / enroll actions)
            "submitted_at",
            "reviewed_by",
            "review_notes",
            "tour_date",
            "toured_at",
            "offer_sent_at",
            "offer_deadline",
            "offer_accepted_at",
            "linked_student",
            "timeline",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "school",
            "application_number",
            "submitted_at",
            "reviewed_by",
            "review_notes",
            "tour_date",
            "toured_at",
            "offer_sent_at",
            "offer_deadline",
            "offer_accepted_at",
            "linked_student",
            "created_at",
            "updated_at",
        ]

    def get_timeline(self, obj):
        events = obj.timeline.select_related("created_by").all()[:50]
        return [
            {
                "id": str(e.id),
                "stage": e.stage,
                "note": e.note,
                "created_by_name": e.created_by.full_name if e.created_by else None,
                "created_at": e.created_at,
            }
            for e in events
        ]


class ApplicationTimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationTimelineEvent
        fields = [
            "id",
            "id",
            "application",
            "stage",
            "note",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ApplicationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDocument
        fields = [
            "id",
            "id",
            "application",
            "document_type",
            "file_url",
            "file_name",
            "uploaded_at",
            "is_verified",
            "notes",
        ]
        read_only_fields = ["id"]


class EntranceAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntranceAssessment
        fields = [
            "id",
            "id",
            "application",
            "assessment_type",
            "scheduled_date",
            "completed_date",
            "status",
            "score",
            "max_score",
            "notes",
            "assessor_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ApplicationReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source="reviewer.full_name", read_only=True)

    class Meta:
        model = ApplicationReview
        fields = [
            "id",
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


class ApplicationFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationFee
        fields = [
            "id",
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
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InterviewScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewSchedule
        fields = [
            "id",
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
            "panel_members",
            "feedback",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MeritListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeritList
        fields = [
            "id",
            "school",
            "id",
            "intake",
            "name",
            "description",
            "grade",
            "status",
            "total_applicants",
            "total_selected",
            "total_waitlisted",
            "published_at",
            "published_by",
        ]
        read_only_fields = ["school", "id", "created_at", "updated_at"]


class MeritListEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MeritListEntry
        fields = [
            "id",
            "id",
            "merit_list",
            "application",
            "rank",
            "total_score",
            "status",
            "academic_score",
            "assessment_score",
            "interview_score",
            "extracurricular_score",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WaitlistManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitlistManagement
        fields = [
            "id",
            "id",
            "application",
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
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EnrollmentConfirmationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrollmentConfirmation
        fields = [
            "id",
            "id",
            "application",
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
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AdmissionsReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionsReport
        fields = [
            "id",
            "school",
            "id",
            "intake",
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
        ]
        read_only_fields = ["school", "id", "created_at"]


class AdmissionsEmailNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionsEmailNotification
        fields = [
            "id",
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
        read_only_fields = ["id", "created_at"]


class AdmissionsSMSNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionsSMSNotification
        fields = [
            "id",
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
        read_only_fields = ["id", "created_at"]


class ReEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReEnrollment
        fields = [
            "id",
            "school",
            "id",
            "student",
            "intake",
            "status",
            "current_grade",
            "next_grade",
            "invited_at",
            "deadline",
            "started_at",
            "completed_at",
            "decline_reason",
        ]
        read_only_fields = ["school", "id", "updated_at"]


class AdmissionsPipelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionsPipeline
        fields = [
            "id",
            "school",
            "id",
            "application",
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
        ]
        read_only_fields = ["school", "id", "created_at", "updated_at"]


class ApplicationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationTemplate
        fields = [
            "id",
            "school",
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
        ]
        read_only_fields = ["school", "id", "created_at", "updated_at"]


class BulkApplicationImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkApplicationImport
        fields = [
            "id",
            "school",
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
            "initiated_at",
            "completed_at",
        ]
        read_only_fields = ["school", "id"]


class CampusVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusVisit
        fields = [
            "id",
            "school",
            "id",
            "visitor_name",
            "visitor_email",
            "visitor_phone",
            "prospective_student",
            "visit_type",
            "status",
            "scheduled_date",
            "scheduled_time",
            "duration_minutes",
            "tour_guide",
        ]
        read_only_fields = ["school", "id", "created_at", "updated_at"]


class OpenHouseEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenHouseEvent
        fields = [
            "id",
            "school",
            "id",
            "title",
            "description",
            "status",
            "event_date",
            "start_time",
            "end_time",
            "location",
            "max_attendees",
            "current_attendees",
            "registration_required",
            "registration_deadline",
            "registration_url",
        ]
        read_only_fields = ["school", "id", "created_at", "updated_at"]


class OpenHouseRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenHouseRegistration
        fields = [
            "id",
            "id",
            "event",
            "registrant_name",
            "registrant_email",
            "registrant_phone",
            "child_name",
            "child_dob",
            "current_grade",
            "current_school",
            "status",
            "num_attendees",
            "application_created",
            "notes",
            "registered_at",
        ]
        read_only_fields = ["id"]


class ScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scholarship
        fields = [
            "id",
            "school",
            "id",
            "name",
            "description",
            "scholarship_type",
            "status",
            "amount_type",
            "amount_fixed",
            "amount_percentage",
            "max_recipients",
            "current_recipients",
            "min_gpa",
            "eligible_grades",
            "eligible_intakes",
        ]
        read_only_fields = ["school", "id", "created_at", "updated_at"]


class ScholarshipApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholarshipApplication
        fields = [
            "id",
            "id",
            "scholarship",
            "application",
            "status",
            "essay",
            "recommendation_letter",
            "transcript",
            "family_income",
            "financial_need_score",
            "merit_score",
            "gpa_at_application",
            "decision_notes",
            "amount_awarded",
        ]
        read_only_fields = ["id", "updated_at"]


class AdmissionPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionPolicy
        fields = [
            "id",
            "school",
            "id",
            "name",
            "policy_type",
            "description",
            "min_age_years",
            "max_age_years",
            "priority_weight",
            "max_students_per_grade",
            "effective_date",
            "expiry_date",
            "is_active",
            "policy_document",
            "created_by",
        ]
        read_only_fields = ["school", "id", "created_at", "updated_at"]


class AdmissionAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionAgreement
        fields = [
            "id",
            "school",
            "id",
            "name",
            "description",
            "content",
            "status",
            "version",
            "effective_date",
            "expiry_date",
            "requires_parent_signature",
            "requires_student_signature",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["school", "id", "created_at", "updated_at"]


class AgreementSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgreementSignature
        fields = [
            "id",
            "id",
            "agreement",
            "application",
            "signer_type",
            "signer_name",
            "signature",
            "signed_at",
            "ip_address",
        ]
        read_only_fields = ["id"]


class AdmissionCommunicationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionCommunicationLog
        fields = [
            "id",
            "school",
            "id",
            "application",
            "channel",
            "direction",
            "subject",
            "content",
            "sent_by",
            "sent_to_name",
            "sent_to_email",
            "delivered",
            "opened",
        ]
        read_only_fields = ["school", "id", "created_at"]


class AdmissionReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionReminder
        fields = [
            "id",
            "school",
            "id",
            "application",
            "reminder_type",
            "status",
            "subject",
            "message",
            "scheduled_date",
            "sent_date",
            "channel",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["school", "id", "created_at"]


class GradeLevelCapacitySerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeLevelCapacity
        fields = [
            "id",
            "id",
            "intake",
            "grade_level",
            "max_capacity",
            "current_enrollment",
            "waitlist_count",
            "boys_count",
            "girls_count",
            "tuition_fee",
            "registration_fee",
            "is_accepting",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AdmissionDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionDecision
        fields = [
            "id",
            "id",
            "application",
            "decision",
            "decision_reason",
            "rationale",
            "conditions",
            "recommended_grade",
            "recommended_class",
            "scholarship_amount",
            "financial_aid_amount",
            "decided_by",
            "decided_at",
            "parent_notified",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TransferStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferStudent
        fields = [
            "id",
            "school",
            "id",
            "application",
            "previous_school_name",
            "previous_school_address",
            "previous_school_phone",
            "previous_school_email",
            "previous_school_type",
            "years_attended",
            "last_grade_completed",
            "graduation_date",
            "previous_gpa",
            "class_rank",
        ]
        read_only_fields = ["school", "id", "created_at", "updated_at"]


class SiblingGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiblingGroup
        fields = [
            "id",
            "school",
            "id",
            "family_name",
            "parent_name",
            "parent_email",
            "parent_phone",
            "total_siblings",
            "currently_enrolled",
            "sibling_priority",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["school", "id", "created_at", "updated_at"]


class SiblingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiblingRecord
        fields = [
            "id",
            "id",
            "sibling_group",
            "student",
            "application",
            "is_currently_enrolled",
            "grade_level",
            "enrollment_date",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AdmissionFunnelSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionFunnelSnapshot
        fields = [
            "id",
            "id",
            "intake",
            "snapshot_date",
            "inquiries",
            "campus_visits",
            "applications_started",
            "applications_submitted",
            "documents_complete",
            "under_review",
            "interviews_scheduled",
            "interviews_completed",
            "decisions_made",
            "admitted",
            "enrolled",
        ]
        read_only_fields = ["id", "created_at"]


class AdmissionDocumentChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionDocumentChecklist
        fields = [
            "id",
            "id",
            "intake",
            "grade_level",
            "document_name",
            "description",
            "is_mandatory",
            "accepted_formats",
            "max_file_size_mb",
            "sort_order",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AdmissionDocumentVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionDocumentVerification
        fields = [
            "id",
            "id",
            "application",
            "checklist_item",
            "status",
            "file",
            "original_filename",
            "file_size",
            "verified_by",
            "verified_at",
            "rejection_reason",
            "uploaded_at",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


class AdmissionPredictionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionPredictionModel
        fields = [
            "id",
            "id",
            "intake",
            "prediction_type",
            "prediction_date",
            "predicted_value",
            "confidence_score",
            "factors",
            "model_version",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AdmissionMarketingSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionMarketingSource
        fields = [
            "id",
            "school",
            "id",
            "name",
            "source_type",
            "total_inquiries",
            "total_applications",
            "total_enrolled",
            "conversion_rate",
            "cost",
            "cost_per_enrollment",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["school", "id", "created_at", "updated_at"]


class AdmissionTrendAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionTrendAnalysis
        fields = [
            "id",
            "school",
            "id",
            "academic_year",
            "intake",
            "total_applications",
            "applications_male",
            "applications_female",
            "total_enrolled",
            "enrollment_male",
            "enrollment_female",
            "yield_rate",
            "total_tuition_revenue",
            "total_scholarships_awarded",
        ]
        read_only_fields = ["school", "id", "created_at"]


# ── Serializers restored from original module (expansion regression fix) ──


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
