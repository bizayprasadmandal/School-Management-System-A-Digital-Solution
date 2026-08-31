"""
Student Service — DRF Serializers
"""

from rest_framework import serializers

from .models import (
    AcademicYear,
    Classroom,
    Document,
    Enrollment,
    Grade,
    Guardian,
    SiblingTracking,
    Student,
    StudentArchive,
    StudentCategory,
    StudentCategoryMembership,
    StudentContact,
    StudentCustomField,
    StudentCustomFieldValue,
    StudentGuardian,
    StudentIDCard,
    StudentMedicalRecord,
    StudentNote,
    StudentPhoto,
    StudentPortfolio,
    StudentSocialMedia,
    StudentStatusHistory,
    StudentTag,
    StudentTagAssignment,
    StudentWellness,
)


class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "alternate_phone",
            "occupation",
            "address",
            "is_primary",
        ]


class StudentGuardianSerializer(serializers.ModelSerializer):
    guardian = GuardianSerializer(read_only=True)

    class Meta:
        model = StudentGuardian
        fields = ["guardian", "relationship", "is_primary_contact", "has_pickup_permission", "portal_access"]


class EnrollmentSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source="classroom.__str__", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "classroom",
            "classroom_name",
            "academic_year",
            "academic_year_name",
            "status",
            "enrollment_date",
        ]


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
        fields = [
            "id",
            "admission_number",
            "full_name",
            "email",
            "avatar",
            "gender",
            "current_class",
            "is_active",
        ]

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


class GradeSerializer(serializers.ModelSerializer):
    classroom_count = serializers.IntegerField(read_only=True)
    student_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Grade
        fields = ["id", "name", "level", "description", "classroom_count", "student_count"]


class ClassroomSerializer(serializers.ModelSerializer):
    grade_name = serializers.CharField(source="grade.name", read_only=True)
    teacher_name = serializers.SerializerMethodField()
    student_count = serializers.ReadOnlyField()

    class Meta:
        model = Classroom
        fields = [
            "id",
            "name",
            "grade",
            "grade_name",
            "capacity",
            "room_number",
            "class_teacher",
            "teacher_name",
            "student_count",
            "academic_year",
        ]

    def get_teacher_name(self, obj):
        return obj.class_teacher.full_name if obj.class_teacher else None


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source="uploaded_by.full_name", read_only=True)
    MAX_FILE_SIZE_MB = 10

    class Meta:
        model = Document
        fields = ["id", "document_type", "title", "file", "uploaded_by_name", "uploaded_at", "notes"]
        read_only_fields = ["uploaded_by", "uploaded_at"]

    def validate_file(self, value):
        # File size validation
        if value.size > self.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(f"File size must not exceed {self.MAX_FILE_SIZE_MB} MB.")
        # File type validation — allow common document types
        allowed_types = [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/gif",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                f"File type '{value.content_type}' is not allowed. " f"Allowed types: PDF, JPEG, PNG, GIF, DOC, DOCX."
            )
        return value

    def create(self, validated_data):
        validated_data["uploaded_by"] = self.context["request"].user
        return super().create(validated_data)


class StudentContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentContact
        fields = [
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
            "insurance_provider",
            "insurance_policy_number",
            "insurance_expiry",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentMedicalRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    record_type_display = serializers.CharField(source="get_record_type_display", read_only=True)
    severity_display = serializers.CharField(source="get_severity_display", read_only=True)

    class Meta:
        model = StudentMedicalRecord
        fields = [
            "id",
            "student",
            "student_name",
            "record_type",
            "record_type_display",
            "title",
            "description",
            "severity",
            "severity_display",
            "date_recorded",
            "date_of_visit",
            "doctor_name",
            "hospital_name",
            "treatment_notes",
            "medication_details",
            "document_url",
            "is_ongoing",
            "resolved_date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "date_recorded", "created_at", "updated_at"]


class StudentCustomFieldSerializer(serializers.ModelSerializer):
    field_type_display = serializers.CharField(source="get_field_type_display", read_only=True)

    class Meta:
        model = StudentCustomField
        fields = [
            "id",
            "name",
            "field_type",
            "field_type_display",
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
    field_name = serializers.CharField(source="field.name", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = StudentCustomFieldValue
        fields = [
            "id",
            "student",
            "student_name",
            "field",
            "field_name",
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
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    photo_type_display = serializers.CharField(source="get_photo_type_display", read_only=True)

    class Meta:
        model = StudentPhoto
        fields = [
            "id",
            "student",
            "student_name",
            "photo_type",
            "photo_type_display",
            "title",
            "description",
            "photo_url",
            "thumbnail_url",
            "taken_date",
            "photographer",
            "is_primary",
            "is_public",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "taken_date", "created_at"]


class StudentIDCardSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    is_valid = serializers.ReadOnlyField()

    class Meta:
        model = StudentIDCard
        fields = [
            "id",
            "student",
            "student_name",
            "card_number",
            "barcode",
            "rfid_number",
            "issue_date",
            "expiry_date",
            "status",
            "status_display",
            "is_valid",
            "photo_url",
            "access_level",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "issue_date", "created_at", "updated_at"]


class StudentStatusHistorySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True, default=None)

    class Meta:
        model = StudentStatusHistory
        fields = [
            "id",
            "student",
            "student_name",
            "status",
            "status_display",
            "previous_status",
            "effective_date",
            "reason",
            "document_url",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "approved_at", "created_at"]


class SiblingTrackingSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    sibling_name = serializers.CharField(source="sibling.user.full_name", read_only=True)

    class Meta:
        model = SiblingTracking
        fields = [
            "id",
            "student",
            "student_name",
            "sibling",
            "sibling_name",
            "relationship",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StudentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCategory
        fields = [
            "id",
            "name",
            "description",
            "color",
            "is_active",
            "student_count",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "student_count", "created_at"]


class StudentCategoryMembershipSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = StudentCategoryMembership
        fields = [
            "id",
            "student",
            "student_name",
            "category",
            "category_name",
            "start_date",
            "end_date",
            "is_active",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "start_date", "created_at"]


class StudentTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentTag
        fields = [
            "id",
            "name",
            "color",
            "usage_count",
            "is_active",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "usage_count", "created_at"]


class StudentTagAssignmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    tag_name = serializers.CharField(source="tag.name", read_only=True)

    class Meta:
        model = StudentTagAssignment
        fields = [
            "id",
            "student",
            "student_name",
            "tag",
            "tag_name",
            "assigned_by",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StudentNoteSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    note_type_display = serializers.CharField(source="get_note_type_display", read_only=True)
    author_name = serializers.CharField(source="author.full_name", read_only=True, default=None)

    class Meta:
        model = StudentNote
        fields = [
            "id",
            "student",
            "student_name",
            "note_type",
            "note_type_display",
            "title",
            "content",
            "author",
            "author_name",
            "is_confidential",
            "is_pinned",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentArchiveSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    grade_name = serializers.CharField(source="grade.name", read_only=True, default=None)

    class Meta:
        model = StudentArchive
        fields = [
            "id",
            "student",
            "student_name",
            "academic_year",
            "academic_year_name",
            "grade",
            "grade_name",
            "status",
            "final_grade",
            "gpa",
            "rank_in_class",
            "attendance_percentage",
            "achievements",
            "report_card_url",
            "transcript_url",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StudentSocialMediaSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    platform_display = serializers.CharField(source="get_platform_display", read_only=True)

    class Meta:
        model = StudentSocialMedia
        fields = [
            "id",
            "student",
            "student_name",
            "platform",
            "platform_display",
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
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    portfolio_type_display = serializers.CharField(source="get_portfolio_type_display", read_only=True)

    class Meta:
        model = StudentPortfolio
        fields = [
            "id",
            "student",
            "student_name",
            "portfolio_type",
            "portfolio_type_display",
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
        read_only_fields = ["id", "date_completed", "created_at"]


class StudentWellnessSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    wellness_type_display = serializers.CharField(source="get_wellness_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.full_name", read_only=True, default=None)

    class Meta:
        model = StudentWellness
        fields = [
            "id",
            "student",
            "student_name",
            "wellness_type",
            "wellness_type_display",
            "status",
            "status_display",
            "title",
            "description",
            "mood_score",
            "stress_level",
            "recorded_by",
            "recorded_by_name",
            "follow_up_required",
            "follow_up_date",
            "follow_up_notes",
            "is_confidential",
            "document_url",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
