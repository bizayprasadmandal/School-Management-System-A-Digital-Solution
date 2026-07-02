from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from .models import User, School


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


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "phone",
            "avatar", "role", "is_active", "email_verified",
            "two_factor_enabled", "notify_email", "notify_sms", "notify_push",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "role", "is_active", "email_verified", "date_joined"]
