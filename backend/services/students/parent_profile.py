"""
Parent Profile — self-service profile editing for parent/guardian users.
Provides GET/PATCH endpoint at /students/parent-profile/ for authenticated parents.
"""

from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from .models import ParentProfile


class ParentProfileSerializer(serializers.ModelSerializer):
    """Full parent profile — for admin view."""
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = ParentProfile
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ParentSelfProfileSerializer(serializers.ModelSerializer):
    """Limited fields that parents can edit themselves."""

    class Meta:
        model = ParentProfile
        fields = ["occupation", "alternate_phone", "address", "emergency_contact_name", "emergency_contact_phone", "bio"]


class ParentProfileView(generics.RetrieveUpdateAPIView):
    """Get/update the authenticated parent's own profile."""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return ParentSelfProfileSerializer
        return ParentProfileSerializer

    def get_object(self):
        profile, _ = ParentProfile.objects.get_or_create(
            user=self.request.user,
            school=self.request.user.school,
        )
        return profile
