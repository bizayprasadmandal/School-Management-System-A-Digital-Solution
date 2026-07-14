from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from .models import User, School, AuditLog


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
            "school": {
                "id": str(user.school.id),
                "name": user.school.name,
                "code": user.school.code,
            } if user.school else None,
            "notify_email": user.notify_email,
            "notify_sms": user.notify_sms,
            "notify_push": user.notify_push,
        }
        return data


class SendEmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, help_text="Email to verify. Defaults to the authenticated user's email if omitted.")

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
            "id", "school", "user", "user_name", "user_email",
            "action", "resource_type", "resource_id", "changes",
            "ip_address", "user_agent", "timestamp",
        ]
        read_only_fields = fields


class UserProfileSerializer(serializers.ModelSerializer):
    backup_codes_remaining = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "phone",
            "avatar", "role", "is_active", "email_verified",
            "two_factor_enabled", "backup_codes_remaining",
            "notify_email", "notify_sms", "notify_push",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "role", "is_active", "email_verified", "date_joined"]

    def get_backup_codes_remaining(self, obj):
        if not obj.two_factor_enabled:
            return None
        return obj.backup_codes.filter(used=False).count()
