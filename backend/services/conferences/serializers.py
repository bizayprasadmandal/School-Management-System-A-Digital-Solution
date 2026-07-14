from rest_framework import serializers
from .models import ConferenceSlot


class ConferenceSlotSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True, allow_null=True)

    class Meta:
        model = ConferenceSlot
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class ConferenceSlotCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceSlot
        fields = ["teacher", "student", "date", "start_time", "end_time", "notes"]
