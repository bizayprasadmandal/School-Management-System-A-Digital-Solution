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
        fields = ["id", "school", "name", "start_date", "end_date", "is_current"]
        read_only_fields = ["id"]


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ["id", "school", "name", "level", "description"]
        read_only_fields = ["id"]


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ["id", "school", "grade", "name", "capacity", "room_number", "class_teacher", "academic_year"]
        read_only_fields = ["id"]


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "id",
            "school",
            "id",
            "user",
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
            "guardian",
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
            "classroom",
            "academic_year",
            "status",
            "enrollment_date",
            "promoted_from",
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
        fields = ["id", "student", "document_type", "title", "file", "uploaded_by", "uploaded_at", "notes"]
        read_only_fields = ["id", "student", "uploaded_by", "uploaded_at"]


class StudentContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentContact
        fields = [
            "id",
            "id",
            "student",
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
            "field",
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
        ]
        read_only_fields = ["id", "created_at"]


class StudentIDCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentIDCard
        fields = [
            "id",
            "id",
            "student",
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
            "status",
            "previous_status",
            "effective_date",
            "reason",
            "document_url",
            "approved_by",
            "approved_at",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SiblingTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiblingTracking
        fields = ["id", "id", "student", "sibling", "relationship", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class StudentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCategory
        fields = [
            "id",
            "school",
            "id",
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
        fields = ["id", "id", "student", "category", "start_date", "end_date", "is_active", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class StudentTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentTag
        fields = ["id", "school", "id", "name", "color", "usage_count", "is_active", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class StudentTagAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentTagAssignment
        fields = ["id", "id", "student", "tag", "assigned_by", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class StudentNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentNote
        fields = [
            "id",
            "id",
            "student",
            "note_type",
            "title",
            "content",
            "author",
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
            "academic_year",
            "grade",
            "classroom",
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
            "wellness_type",
            "status",
            "title",
            "description",
            "mood_score",
            "stress_level",
            "recorded_by",
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
            "club_name",
            "club_type",
            "role",
            "join_date",
            "end_date",
            "is_active",
            "advisor",
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
            "activity_name",
            "activity_type",
            "start_date",
            "end_date",
            "hours_per_week",
            "total_hours",
            "is_active",
            "instructor",
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
            "subject",
            "tutor",
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
            "mentor",
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
            "communication_type",
            "subject",
            "description",
            "communication_date",
            "parent_name",
            "parent_phone",
            "parent_email",
            "teacher",
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
            "advisor",
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
            "transfer_type",
            "from_school",
            "to_school",
            "from_classroom",
            "to_classroom",
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
            "route",
            "vehicle",
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
            "id_card",
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
            "feedback_type",
            "subject",
            "rating",
            "comments",
            "suggestions",
            "is_anonymous",
            "response",
            "responded_by",
            "responded_at",
        ]
        read_only_fields = ["id", "created_at"]


# ── Serializers restored from original module (expansion regression fix) ──


class StudentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views.

    Uses the annotated `current_class_name` field from the ViewSet's
    prefetch/annotate to avoid N+1 queries per student.
    """

    full_name = serializers.SerializerMethodField()
    current_class = serializers.CharField(source="current_class_name", read_only=True, default=None)
    email = serializers.EmailField(source="user.email", read_only=True)
    avatar = serializers.ImageField(source="user.avatar", read_only=True)

    class Meta:
        model = Student
        fields = ["id", "admission_number", "full_name", "email", "avatar", "gender", "current_class", "is_active"]

    def get_full_name(self, obj):
        return obj.user.full_name


class StudentDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)
    avatar = serializers.ImageField(source="user.avatar", read_only=True)
    guardians = StudentGuardianSerializer(source="studentguardian_set", many=True, read_only=True)
    enrollments = EnrollmentSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "admission_number",
            "roll_number",
            "full_name",
            "email",
            "phone",
            "avatar",
            "date_of_birth",
            "gender",
            "blood_group",
            "nationality",
            "religion",
            "address",
            "city",
            "state",
            "country",
            "postal_code",
            "admission_date",
            "medical_conditions",
            "emergency_contact_name",
            "emergency_contact_phone",
            "previous_school",
            "is_active",
            "age",
            "guardians",
            "enrollments",
            "created_at",
            "updated_at",
        ]

    def get_full_name(self, obj):
        return obj.user.full_name


class StudentSelfProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for students to update their own profile fields.
    Only exposes non-sensitive self-service fields (bio, interests, learning_goals).
    """

    class Meta:
        model = Student
        fields = ["bio", "interests", "learning_goals"]


class StudentCreateSerializer(serializers.ModelSerializer):
    """Handles student creation including user account creation.

    admission_number is optional — if left blank or omitted the system
    auto-generates one using the format ADM-YYYY-NNNN (e.g. ADM-2026-0001).
    Admins can still supply a custom number (e.g. for transfers).
    """

    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    classroom_id = serializers.IntegerField(write_only=True)
    admission_number = serializers.CharField(required=False, allow_blank=True)
    MAX_BULK_SIZE = 200

    class Meta:
        model = Student
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "admission_number",
            "date_of_birth",
            "gender",
            "blood_group",
            "nationality",
            "address",
            "city",
            "state",
            "country",
            "admission_date",
            "classroom_id",
            "medical_conditions",
            "emergency_contact_name",
            "emergency_contact_phone",
        ]

    def _generate_admission_number(self, school):
        """Auto-generate admission number: ADM-YYYY-NNNN.

        Queries the highest existing sequence number for the current year
        and increments it.  Uses ``select_for_update`` so concurrent
        creates within the same transaction cannot collide.
        """
        from datetime import datetime

        year = datetime.now().year
        prefix = f"ADM-{year}-"

        last_student = (
            Student.objects.select_for_update()
            .filter(school=school, admission_number__startswith=prefix)
            .order_by("-admission_number")
            .first()
        )

        if last_student:
            last_seq = int(last_student.admission_number.split("-")[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1

        return f"{prefix}{new_seq:04d}"

    def validate_email(self, value):
        from services.auth.models import User

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_admission_number(self, value):
        school = self.context["request"].user.school

        # Auto-generate when blank or omitted
        if not value:
            return self._generate_admission_number(school)

        # Manual override — just enforce uniqueness within the school
        if Student.objects.filter(school=school, admission_number=value).exists():
            raise serializers.ValidationError("This admission number is already in use.")
        return value

    def create(self, validated_data):
        from django.db import transaction
        from services.auth.models import User, UserRole

        with transaction.atomic():
            user = User.objects.create_user(
                email=validated_data.pop("email"),
                password=validated_data.pop("password"),
                first_name=validated_data.pop("first_name"),
                last_name=validated_data.pop("last_name"),
                role=UserRole.STUDENT,
                school=self.context["request"].user.school,
            )
            classroom_id = validated_data.pop("classroom_id")
            # Tenant isolation: classroom must belong to the caller's school.
            try:
                classroom = Classroom.objects.get(id=classroom_id, school=self.context["request"].user.school)
            except Classroom.DoesNotExist:
                raise serializers.ValidationError({"classroom_id": "Classroom not found in your school."})

            student = Student.objects.create(
                user=user,
                school=self.context["request"].user.school,
                **validated_data,
            )

            academic_year = AcademicYear.objects.filter(school=student.school, is_current=True).first()
            if academic_year:
                Enrollment.objects.create(
                    student=student,
                    classroom=classroom,
                    academic_year=academic_year,
                )
            return student
