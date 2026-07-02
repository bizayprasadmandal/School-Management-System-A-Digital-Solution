"""
Core permission classes for the School Management System.
Implements role-based access control (RBAC) with tenant isolation.
"""

from rest_framework import permissions
from services.auth.models import UserRole


class IsSchoolMember(permissions.BasePermission):
    """User belongs to the same school as the requested resource."""

    message = "You do not have access to this school's resources."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.school)

    def has_object_permission(self, request, view, obj):
        # Support objects with direct school FK or nested ones
        if hasattr(obj, "school"):
            return obj.school == request.user.school
        if hasattr(obj, "student"):
            return obj.student.school == request.user.school
        return True


class IsSchoolAdmin(permissions.BasePermission):
    message = "Only school administrators can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in [UserRole.SCHOOL_ADMIN, UserRole.SUPER_ADMIN]
        )


class IsSuperAdmin(permissions.BasePermission):
    message = "Only super administrators can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.SUPER_ADMIN
        )


class IsTeacher(permissions.BasePermission):
    message = "Only teachers can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in [UserRole.TEACHER, UserRole.SCHOOL_ADMIN, UserRole.SUPER_ADMIN]
        )


class IsStudent(permissions.BasePermission):
    message = "Only students can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.STUDENT
        )


class IsParent(permissions.BasePermission):
    message = "Only parents/guardians can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.PARENT
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """The requesting user owns the object, or is an admin."""

    def has_object_permission(self, request, view, obj):
        if request.user.role in [UserRole.SCHOOL_ADMIN, UserRole.SUPER_ADMIN]:
            return True
        if hasattr(obj, "user"):
            return obj.user == request.user
        if hasattr(obj, "student") and hasattr(obj.student, "user"):
            return obj.student.user == request.user
        return False


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsTeacherOfClass(permissions.BasePermission):
    """Teacher is assigned to the relevant classroom."""

    def has_object_permission(self, request, view, obj):
        if request.user.role in [UserRole.SCHOOL_ADMIN, UserRole.SUPER_ADMIN]:
            return True
        if request.user.role != UserRole.TEACHER:
            return False
        classroom = getattr(obj, "classroom", None)
        if classroom is None:
            return False
        return classroom.assignments.filter(teacher=request.user).exists()
