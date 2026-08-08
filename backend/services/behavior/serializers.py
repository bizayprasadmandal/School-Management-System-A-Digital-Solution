from rest_framework import serializers

from .models import Incident, Referral


class IncidentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    reported_by_name = serializers.CharField(source="reported_by.full_name", read_only=True)

    class Meta:
        model = Incident
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "school", "reported_by"]


class ReferralSerializer(serializers.ModelSerializer):
    referred_to_name = serializers.CharField(source="referred_to.full_name", read_only=True)
    referred_by_name = serializers.CharField(source="referred_by.full_name", read_only=True)

    class Meta:
        model = Referral
        fields = "__all__"
        read_only_fields = ["id", "created_at", "referred_by"]
