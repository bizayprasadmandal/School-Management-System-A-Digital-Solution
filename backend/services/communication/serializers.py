"""
Communication Service — DRF Serializers
"""

from rest_framework import serializers
from .models import Announcement, DirectMessage, Notification


class AnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = [
            "id", "title", "content", "priority", "audience",
            "send_email", "send_sms", "send_push",
            "target_grades", "target_classrooms",
            "published_at", "expires_at", "is_draft",
            "view_count", "created_by_name", "created_at", "is_read",
            "attachment",
        ]
        read_only_fields = ["id", "created_by", "created_at", "published_at", "view_count"]

    MAX_FILE_SIZE_MB = 10

    def validate_attachment(self, value):
        if value and value.size > self.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(
                f"File size must not exceed {self.MAX_FILE_SIZE_MB} MB."
            )
        if value:
            allowed_types = [
                "application/pdf",
                "image/jpeg", "image/png", "image/gif",
                "text/plain",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ]
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    f"File type '{value.content_type}' is not allowed. "
                    f"Allowed types: PDF, JPEG, PNG, GIF, TXT, DOC, DOCX."
                )
        return value

    def get_is_read(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.reads.filter(user=request.user).exists()


class DirectMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.full_name", read_only=True)
    sender_avatar = serializers.ImageField(source="sender.avatar", read_only=True)
    sender_role = serializers.CharField(source="sender.role", read_only=True)
    recipient_name = serializers.CharField(source="recipient.full_name", read_only=True)
    recipient_avatar = serializers.ImageField(source="recipient.avatar", read_only=True)

    class Meta:
        model = DirectMessage
        fields = [
            "id", "sender", "sender_name", "sender_avatar", "sender_role",
            "recipient", "recipient_name", "recipient_avatar",
            "content", "attachment", "status", "sent_at", "read_at",
            "parent_message",
        ]
        read_only_fields = ["id", "sender", "status", "sent_at", "read_at"]

    def validate_recipient(self, value):
        request = self.context["request"]
        if value == request.user:
            raise serializers.ValidationError("You cannot message yourself.")
        if value.school != request.user.school:
            raise serializers.ValidationError("Recipient must be in the same school.")
        return value

    MAX_FILE_SIZE_MB = 10

    def validate_attachment(self, value):
        if value and value.size > self.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(
                f"File size must not exceed {self.MAX_FILE_SIZE_MB} MB."
            )
        if value:
            allowed_types = [
                "application/pdf",
                "image/jpeg", "image/png", "image/gif",
                "text/plain",
            ]
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    f"File type '{value.content_type}' is not allowed. "
                    f"Allowed types: PDF, JPEG, PNG, GIF, TXT."
                )
        return value

    def create(self, validated_data):
        return DirectMessage.objects.create(**validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id", "title", "body", "channel", "status",
            "reference_type", "reference_id",
            "created_at", "sent_at", "read_at",
        ]
        read_only_fields = fields
