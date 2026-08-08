from django.db import models
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import AuditLog, School, User
from .utils import generate_secure_password


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extends JWT payload with user profile data."""

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data["user"] = {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "role": user.role,
            "avatar": user.avatar.url if user.avatar else None,
            "school": (
                {
                    "id": str(user.school.id),
                    "name": user.school.name,
                    "code": user.school.code,
                }
                if user.school
                else None
            ),
            "notify_email": user.notify_email,
            "notify_sms": user.notify_sms,
            "notify_push": user.notify_push,
        }
        return data


class SendEmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=False, help_text="Email to verify. Defaults to the authenticated user's email if omitted."
    )

    def validate_email(self, value):
        user = self.context["request"].user
        if value and value.lower() != user.email:
            raise serializers.ValidationError("You can only verify your own email address.")
        if user.email_verified:
            raise serializers.ValidationError("Email is already verified.")
        return value or user.email


class ConfirmEmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, help_text="The verification token sent to your email.")


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True, default=None)
    user_email = serializers.EmailField(source="user.email", read_only=True, default=None)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "school",
            "user",
            "user_name",
            "user_email",
            "action",
            "resource_type",
            "resource_id",
            "changes",
            "ip_address",
            "user_agent",
            "timestamp",
        ]
        read_only_fields = fields


class SchoolSerializer(serializers.ModelSerializer):
    """Serializer for multi-tenant school management (super admin)."""

    user_count = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    teacher_count = serializers.SerializerMethodField()
    admin_count = serializers.SerializerMethodField()
    total_revenue = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "code",
            "subdomain",
            "logo",
            "address",
            "phone",
            "email",
            "website",
            "timezone",
            "academic_year_start_month",
            "is_active",
            "subscription_tier",
            "user_count",
            "student_count",
            "teacher_count",
            "admin_count",
            "total_revenue",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "user_count",
            "student_count",
            "teacher_count",
            "admin_count",
            "total_revenue",
        ]

    def get_user_count(self, obj):
        return obj.users.count()

    def get_student_count(self, obj):
        return obj.users.filter(role="student").count()

    def get_teacher_count(self, obj):
        return obj.users.filter(role="teacher").count()

    def get_admin_count(self, obj):
        return obj.users.filter(role="school_admin").count()

    def get_total_revenue(self, obj):
        """Sum of all paid payments for this school (quick stat)."""
        from services.fees.models import Payment

        result = Payment.objects.filter(invoice__student__user__school=obj, status="completed").aggregate(
            total=models.Sum("amount")
        )
        return result["total"] or 0


class PlatformDashboardSerializer(serializers.Serializer):
    """Cross-school analytics for super admin platform dashboard."""

    total_schools = serializers.IntegerField()
    active_schools = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_teachers = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    schools_by_tier = serializers.DictField(child=serializers.IntegerField())
    recent_schools = SchoolSerializer(many=True)
    top_schools = serializers.ListField(child=serializers.DictField())


class SchoolAdminSerializer(serializers.ModelSerializer):
    """Serializer for creating/managing school admin users."""

    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "role",
            "is_active",
            "password",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]

    def validate_role(self, value):
        if value != "school_admin":
            raise serializers.ValidationError("Only school_admin role can be created here.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        generated = password is None
        if generated:
            password = generate_secure_password()
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        # Expose the one-time plaintext when the password was auto-generated so
        # the caller can share it with the new admin. A caller-supplied
        # password is never echoed back.
        if generated:
            user._generated_password = password
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    backup_codes_remaining = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "avatar",
            "role",
            "is_active",
            "email_verified",
            "two_factor_enabled",
            "backup_codes_remaining",
            "notify_email",
            "notify_sms",
            "notify_push",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "role", "is_active", "email_verified", "date_joined"]

    def get_backup_codes_remaining(self, obj):
        if not obj.two_factor_enabled:
            return None
        return obj.backup_codes.filter(used=False).count()
