"""AcademicYear viewset and serializer."""

from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AcademicYear
from core.permissions import IsSchoolMember, IsSchoolAdmin


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model  = AcademicYear
        fields = ["id", "name", "start_date", "end_date", "is_current"]

    def validate(self, attrs):
        school  = self.context["request"].user.school
        name    = attrs.get("name", getattr(self.instance, "name", ""))
        qs = AcademicYear.objects.filter(school=school, name=name)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError({"name": "An academic year with this name already exists."})
        return attrs


class AcademicYearViewSet(viewsets.ModelViewSet):
    """
    CRUD for academic years. Only one can be current.
    Admin: full CRUD. Others: read-only.
    """
    serializer_class   = AcademicYearSerializer

    def get_queryset(self):
        return AcademicYear.objects.filter(
            school=self.request.user.school
        ).order_by("-start_date")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "set_current"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

    @action(detail=True, methods=["post"], url_path="set-current")
    def set_current(self, request, pk=None):
        """Mark this academic year as the current one (unsets all others)."""
        year = self.get_object()
        AcademicYear.objects.filter(school=request.user.school).update(is_current=False)
        year.is_current = True
        year.save(update_fields=["is_current"])
        return Response({"detail": f"{year.name} is now the current academic year."})

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request):
        """Shortcut: return just the current academic year."""
        year = AcademicYear.objects.filter(
            school=request.user.school, is_current=True
        ).first()
        if not year:
            return Response({"detail": "No current academic year set."}, status=404)
        return Response(AcademicYearSerializer(year).data)
