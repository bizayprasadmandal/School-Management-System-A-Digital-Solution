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

    def validate_incident(self, value):
        # Referral has no school FK of its own — it inherits tenant scope from
        # the incident. Reject incidents outside the caller's school so a school
        # admin can't attach a referral to another tenant's incident.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Incident not found in your school.")
        return value

    def validate_referred_to(self, value):
        # Referrals must stay within the tenant — the target user has to belong
        # to the same school as the referring admin.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Referred-to user must be in your school.")
        return value
