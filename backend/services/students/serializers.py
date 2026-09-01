"""Serializers for students."""

from rest_framework import serializers

from .models import (
    AcademicYear,
    Classroom,
    Document,
    Enrollment,
    Grade,
    Guardian,
    ParentProfile,
    SiblingTracking,
    Student,
    StudentAcademicAdvisor,
    StudentAchievement,
    StudentActivity,
    StudentArchive,
    StudentAward,
    StudentCareerGuidance,
    StudentCategory,
    StudentCategoryMembership,
    StudentClub,
    StudentContact,
    StudentCustomField,
    StudentCustomFieldValue,
    StudentDiscipline,
    StudentFeedback,
    StudentFinancialAid,
    StudentGraduation,
    StudentGuardian,
    StudentIDActivity,
    StudentIDCard,
    StudentInternship,
    StudentLearningStyle,
    StudentMealPlan,
    StudentMedicalRecord,
    StudentMentor,
    StudentNote,
    StudentParentCommunication,
    StudentParking,
    StudentPhoto,
    StudentPortfolio,
    StudentScholarship,
    StudentSocialMedia,
    StudentStatusHistory,
    StudentTag,
    StudentTagAssignment,
    StudentTransfer,
    StudentTransportAssignment,
    StudentTutoring,
    StudentVolunteer,
    StudentWellness,
)


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ["id", "school", "on_delete", "name", "start_date", "end_date", "is_current"]
        read_only_fields = ["id"]


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ["id", "school", "on_delete", "name", "level", "description"]
        read_only_fields = ["id"]


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = [
            "id",
            "school",
            "on_delete",
            "grade",
            "on_delete",
            "name",
            "capacity",
            "room_number",
            "class_teacher",
            "on_delete",
            "academic_year",
            "on_delete",
        ]
        read_only_fields = ["id"]


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "id",
            "school",
            "id",
            "user",
            "on_delete",
            "on_delete",
            "admission_number",
            "roll_number",
            "date_of_birth",
            "gender",
            "blood_group",
            "nationality",
            "religion",
            "address",
            "city",
            "state",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = [
            "id",
            "user",
            "on_delete",
            "students",
            "first_name",
            "last_name",
            "email",
            "phone",
            "alternate_phone",
            "occupation",
            "annual_income",
            "address",
            "is_primary",
        ]
        read_only_fields = ["id"]


class StudentGuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGuardian
        fields = [
            "id",
            "student",
            "on_delete",
            "guardian",
            "on_delete",
            "relationship",
            "is_primary_contact",
            "has_pickup_permission",
            "portal_access",
        ]
        read_only_fields = ["id"]


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student",
            "on_delete",
            "classroom",
            "on_delete",
            "academic_year",
            "on_delete",
            "status",
            "enrollment_date",
            "promoted_from",
            "on_delete",
            "is_active",
            "notes",
        ]
        read_only_fields = ["id"]


class ParentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentProfile
        fields = [
            "id",
            "school",
            "id",
            "user",
            "on_delete",
            "on_delete",
            "occupation",
            "alternate_phone",
            "address",
            "emergency_contact_name",
            "emergency_contact_phone",
            "bio",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "student",
            "on_delete",
            "document_type",
            "title",
            "file",
            "uploaded_by",
            "on_delete",
            "uploaded_at",
            "notes",
        ]
        read_only_fields = ["id"]


class StudentContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentContact
        fields = [
            "id",
            "id",
            "student",
            "on_delete",
            "personal_phone",
            "personal_email",
            "emergency_contact_1_name",
            "emergency_contact_1_phone",
            "emergency_contact_1_relationship",
            "emergency_contact_2_name",
            "emergency_contact_2_phone",
            "emergency_contact_2_relationship",
            "medical_emergency_contact",
            "medical_emergency_phone",
            "doctor_name",
            "doctor_phone",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentMedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentMedicalRecord
        fields = [
            "id",
            "id",
            "student",
            "on_delete",
            "record_type",
            "title",
            "description",
            "severity",
            "date_recorded",
            "date_of_visit",
            "doctor_name",
            "hospital_name",
            "treatment_notes",
            "medication_details",
            "document_url",
            "is_ongoing",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentCustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCustomField
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "field_type",
            "description",
            "options",
            "is_required",
            "is_visible",
            "order",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentCustomFieldValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCustomFieldValue
        fields = [
            "id",
            "id",
            "student",
            "on_delete",
            "field",
            "on_delete",
            "text_value",
            "number_value",
            "date_value",
            "boolean_value",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPhoto
        fields = [
            "id",
            "id",
            "student",
            "on_delete",
            "photo_type",
            "title",
            "description",
            "photo_url",
            "thumbnail_url",
            "taken_date",
            "photographer",
            "is_primary",
            "is_public",
            "notes",
            "uploaded_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at"]


class StudentIDCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentIDCard
        fields = [
            "id",
            "id",
            "student",
            "on_delete",
            "card_number",
            "barcode",
            "rfid_number",
            "issue_date",
            "expiry_date",
            "status",
            "photo_url",
            "access_level",
            "notes",
            "issued_by",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentStatusHistory
        fields = [
            "id",
            "id",
            "student",
            "on_delete",
            "status",
            "previous_status",
            "effective_date",
            "reason",
            "document_url",
            "approved_by",
            "on_delete",
            "approved_at",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SiblingTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiblingTracking
        fields = ["id", "id", "student", "on_delete", "sibling", "on_delete", "relationship", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class StudentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCategory
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "description",
            "color",
            "is_active",
            "student_count",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StudentCategoryMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCategoryMembership
        fields = [
            "id",
            "id",
            "student",
            "on_delete",
            "category",
            "on_delete",
            "start_date",
            "end_date",
            "is_active",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StudentTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentTag
        fields = ["id", "school", "id", "on_delete", "name", "color", "usage_count", "is_active", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class StudentTagAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentTagAssignment
        fields = [
            "id",
            "id",
            "student",
            "on_delete",
            "tag",
            "on_delete",
            "assigned_by",
            "on_delete",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StudentNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentNote
        fields = [
            "id",
            "id",
            "student",
            "on_delete",
            "note_type",
            "title",
            "content",
            "author",
            "on_delete",
            "is_confidential",
            "is_pinned",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentArchiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentArchive
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "academic_year",
            "on_delete",
            "grade",
            "on_delete",
            "classroom",
            "on_delete",
            "status",
            "final_grade",
            "gpa",
            "rank_in_class",
        ]
        read_only_fields = ["id", "created_at"]


class StudentSocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSocialMedia
        fields = [
            "id",
            "id",
            "student",
            "on_delete",
            "platform",
            "username",
            "profile_url",
            "is_verified",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentPortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPortfolio
        fields = [
            "id",
            "id",
            "student",
            "on_delete",
            "portfolio_type",
            "title",
            "description",
            "file_url",
            "thumbnail_url",
            "subject",
            "date_completed",
            "grade_received",
            "is_featured",
            "is_public",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StudentWellnessSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentWellness
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "wellness_type",
            "status",
            "title",
            "description",
            "mood_score",
            "stress_level",
            "recorded_by",
            "on_delete",
            "follow_up_required",
            "follow_up_date",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentLearningStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentLearningStyle
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "primary_style",
            "secondary_style",
            "assessment_tool",
            "score_visual",
            "score_auditory",
            "score_kinesthetic",
            "score_reading",
            "recommendations",
            "assessed_date",
            "assessed_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAchievement
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "achievement_type",
            "title",
            "description",
            "date_earned",
            "awarded_by",
            "certificate_url",
            "is_public",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StudentClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClub
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "club_name",
            "club_type",
            "role",
            "join_date",
            "end_date",
            "is_active",
            "advisor",
            "on_delete",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StudentActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentActivity
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "activity_name",
            "activity_type",
            "start_date",
            "end_date",
            "hours_per_week",
            "total_hours",
            "is_active",
            "instructor",
            "on_delete",
            "notes",
        ]
        read_only_fields = ["id", "created_at"]


class StudentAwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAward
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "award_name",
            "award_level",
            "category",
            "date_awarded",
            "awarded_by",
            "description",
            "certificate_url",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StudentDisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDiscipline
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "action_type",
            "severity",
            "incident_date",
            "description",
            "location",
            "witnesses",
            "action_taken",
            "follow_up_required",
            "follow_up_date",
            "parent_notified",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentTutoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentTutoring
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "subject",
            "on_delete",
            "tutor",
            "on_delete",
            "session_date",
            "start_time",
            "end_time",
            "status",
            "topics_covered",
            "homework_assigned",
        ]
        read_only_fields = ["id", "created_at"]


class StudentMentorSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentMentor
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "mentor",
            "on_delete",
            "program_name",
            "start_date",
            "end_date",
            "status",
            "goals",
            "meeting_frequency",
            "progress_notes",
            "outcome",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentCareerGuidanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCareerGuidance
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "career_interest",
            "career_goals",
            "strengths",
            "areas_for_development",
            "recommended_courses",
            "recommended_activities",
            "college_preferences",
            "scholarship_eligibility",
            "guidance_date",
            "guided_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentParentCommunicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentParentCommunication
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "communication_type",
            "subject",
            "description",
            "communication_date",
            "parent_name",
            "parent_phone",
            "parent_email",
            "teacher",
            "on_delete",
            "follow_up_required",
        ]
        read_only_fields = ["id", "created_at"]


class StudentAcademicAdvisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAcademicAdvisor
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "advisor",
            "on_delete",
            "advising_date",
            "status",
            "academic_goals",
            "course_recommendations",
            "academic_concerns",
            "action_items",
            "next_advising_date",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentTransfer
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "transfer_type",
            "from_school",
            "to_school",
            "from_classroom",
            "on_delete",
            "to_classroom",
            "on_delete",
            "transfer_date",
            "reason",
            "status",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentGraduationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGraduation
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "expected_graduation_year",
            "actual_graduation_year",
            "status",
            "credits_earned",
            "credits_required",
            "gpa",
            "class_rank",
            "diploma_type",
            "honors",
            "college_acceptance",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentVolunteerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentVolunteer
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "organization",
            "activity",
            "hours",
            "date_performed",
            "supervisor_name",
            "supervisor_phone",
            "supervisor_email",
            "certificate_url",
            "verified",
            "verified_by",
        ]
        read_only_fields = ["id", "created_at"]


class StudentInternshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentInternship
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "company_name",
            "position",
            "department",
            "supervisor_name",
            "supervisor_email",
            "start_date",
            "end_date",
            "status",
            "hours_per_week",
            "is_paid",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentScholarship
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "scholarship_name",
            "provider",
            "amount",
            "scholarship_type",
            "application_date",
            "deadline_date",
            "status",
            "award_date",
            "renewal_required",
            "renewal_date",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentFinancialAidSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFinancialAid
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "aid_type",
            "aid_name",
            "amount",
            "provider",
            "application_date",
            "status",
            "disbursement_date",
            "renewal_required",
            "academic_requirement",
            "documents",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentTransportAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentTransportAssignment
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "route",
            "on_delete",
            "vehicle",
            "on_delete",
            "service_type",
            "pickup_address",
            "pickup_latitude",
            "pickup_longitude",
            "effective_from",
            "effective_to",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentMealPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentMealPlan
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "plan_type",
            "plan_name",
            "start_date",
            "end_date",
            "status",
            "meals_per_day",
            "total_meals",
            "meals_consumed",
            "cost",
            "dietary_restrictions",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentParkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentParking
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "permit_number",
            "permit_type",
            "vehicle_make",
            "vehicle_model",
            "vehicle_color",
            "license_plate",
            "parking_zone",
            "start_date",
            "end_date",
            "status",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentIDActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentIDActivity
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "id_card",
            "on_delete",
            "activity_type",
            "location",
            "timestamp",
            "device",
            "notes",
        ]
        read_only_fields = ["id"]


class StudentFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeedback
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "feedback_type",
            "subject",
            "rating",
            "comments",
            "suggestions",
            "is_anonymous",
            "response",
            "responded_by",
            "on_delete",
            "responded_at",
        ]
        read_only_fields = ["id", "created_at"]
