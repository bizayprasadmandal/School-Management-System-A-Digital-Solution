"""
Student Service — DRF Serializers
"""

from rest_framework import serializers
from .models import Student, Guardian, StudentGuardian, Enrollment, Classroom, AcademicYear, Grade, Document


class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = [
            "id", "first_name", "last_name", "email", "phone",
            "alternate_phone", "occupation", "address", "is_primary",
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
        fields = ["id", "classroom", "classroom_name", "academic_year", "academic_year_name", "status", "enrollment_date"]


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
            "id", "admission_number", "full_name", "email", "avatar",
            "gender", "current_class", "is_active",
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
            "id", "admission_number", "roll_number", "full_name", "email",
            "phone", "avatar", "date_of_birth", "gender", "blood_group",
            "nationality", "religion", "address", "city", "state", "country",
            "postal_code", "admission_date", "medical_conditions",
            "emergency_contact_name", "emergency_contact_phone",
            "previous_school", "is_active", "age", "guardians", "enrollments",
            "created_at", "updated_at",
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
    """Handles student creation including user account creation."""
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    classroom_id = serializers.IntegerField(write_only=True)
    MAX_BULK_SIZE = 200

    class Meta:
        model = Student
        fields = [
            "first_name", "last_name", "email", "password",
            "admission_number", "date_of_birth", "gender", "blood_group",
            "nationality", "address", "city", "state", "country",
            "admission_date", "classroom_id", "medical_conditions",
            "emergency_contact_name", "emergency_contact_phone",
        ]

    def validate_email(self, value):
        from services.auth.models import User
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_admission_number(self, value):
        school = self.context["request"].user.school
        if Student.objects.filter(school=school, admission_number=value).exists():
            raise serializers.ValidationError("This admission number is already in use.")
        return value

    def create(self, validated_data):
        from services.auth.models import User, UserRole
        from django.db import transaction

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
            classroom = Classroom.objects.get(id=classroom_id)

            student = Student.objects.create(
                user=user,
                school=self.context["request"].user.school,
                **validated_data,
            )

            academic_year = AcademicYear.objects.filter(
                school=student.school, is_current=True
            ).first()
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
            "id", "name", "grade", "grade_name", "capacity",
            "room_number", "class_teacher", "teacher_name",
            "student_count", "academic_year",
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
            raise serializers.ValidationError(
                f"File size must not exceed {self.MAX_FILE_SIZE_MB} MB."
            )
        # File type validation — allow common document types
        allowed_types = [
            "application/pdf",
            "image/jpeg", "image/png", "image/gif",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                f"File type '{value.content_type}' is not allowed. "
                f"Allowed types: PDF, JPEG, PNG, GIF, DOC, DOCX."
            )
        return value

    def create(self, validated_data):
        validated_data["uploaded_by"] = self.context["request"].user
        return super().create(validated_data)
