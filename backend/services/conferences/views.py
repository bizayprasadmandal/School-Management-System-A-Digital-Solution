"""Conference Scheduler — CRUD for parent-teacher conference slots."""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ConferenceSlot
from .serializers import ConferenceSlotSerializer, ConferenceSlotCreateUpdateSerializer


class IsAdminOrTeacherOrReadStudentParent(permissions.BasePermission):
    """Admins and teachers can CRUD; students/parents read-only for their own school."""
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role in ("admin", "teacher"):
            return True
        if request.user.role == "parent":
            return obj.student and obj.student.guardians.filter(email=request.user.email).exists()
        if request.user.role == "student":
            return obj.student and obj.student.user == request.user
        return False


class ConferenceSlotViewSet(viewsets.ModelViewSet):
    """Manage parent-teacher conference time slots."""
    serializer_class = ConferenceSlotSerializer
    permission_classes = [IsAdminOrTeacherOrReadStudentParent]
    filterset_fields = ["teacher", "student", "is_booked", "date"]
    ordering_fields = ["date", "start_time"]
    ordering = ["date", "start_time"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ConferenceSlotCreateUpdateSerializer
        return ConferenceSlotSerializer

    def get_queryset(self):
        user = self.request.user
        qs = ConferenceSlot.objects.select_related(
            "teacher", "student__user"
        )
        if user.role == "admin":
            return qs.filter(school=user.school)
        elif user.role == "teacher":
            return qs.filter(teacher=user)
        elif user.role == "parent":
            return qs.filter(student__guardians__email=user.email)
        elif user.role == "student":
            return qs.filter(student__user=user)
        return qs.none()

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

    @action(detail=True, methods=["post"])
    def book(self, request, pk=None):
        """Student/parent books an available slot."""
        slot = self.get_object()
        if slot.is_booked:
            return Response({"detail": "Slot is already booked."}, status=status.HTTP_400_BAD_REQUEST)
        student_id = request.data.get("student_id")
        if not student_id:
            return Response({"detail": "student_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        from services.students.models import Student
        try:
            student = Student.objects.get(id=student_id, school=request.user.school)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
        slot.student = student
        slot.is_booked = True
        slot.booked_by = request.user
        slot.save()
        return Response(ConferenceSlotSerializer(slot).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a booked slot."""
        slot = self.get_object()
        if not slot.is_booked:
            return Response({"detail": "Slot is not booked."}, status=status.HTTP_400_BAD_REQUEST)
        slot.student = None
        slot.is_booked = False
        slot.booked_by = None
        slot.save()
        return Response(ConferenceSlotSerializer(slot).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Teacher marks a conference as completed."""
        slot = self.get_object()
        if not slot.is_booked:
            return Response({"detail": "Slot must be booked first."}, status=status.HTTP_400_BAD_REQUEST)
        slot.delete()
        return Response({"detail": "Conference completed and slot released."})
