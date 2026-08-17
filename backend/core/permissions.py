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
        # Support objects with direct school FK or nested ones. Fail CLOSED:
        # an object we cannot prove belongs to the caller's school is denied.
        if hasattr(obj, "school"):
            return obj.school_id == request.user.school_id
        if hasattr(obj, "student"):
            return obj.student.school_id == request.user.school_id
        if hasattr(obj, "user") and getattr(obj.user, "school_id", None) is not None:
            return obj.user.school_id == request.user.school_id
        # Direct messages carry sender/recipient instead of school/student
        if hasattr(obj, "sender") and hasattr(obj, "recipient"):
            return obj.sender_id == request.user.id or obj.recipient_id == request.user.id
        return False


class IsSchoolAdmin(permissions.BasePermission):
    message = "Only school administrators can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in [UserRole.SCHOOL_ADMIN, UserRole.SUPER_ADMIN]
        )


class IsSchoolStaff(permissions.BasePermission):
    """
    Any school staff member: admin, accountant, librarian or teacher.
    Used for school-wide analytics that students/parents must not see.
    """

    message = "Only school staff can access this data."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role
            in [
                UserRole.SCHOOL_ADMIN,
                UserRole.SUPER_ADMIN,
                UserRole.ACCOUNTANT,
                UserRole.LIBRARIAN,
                UserRole.TEACHER,
            ]
        )


class IsSuperAdmin(permissions.BasePermission):
    message = "Only super administrators can perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == UserRole.SUPER_ADMIN)


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
        return bool(request.user and request.user.is_authenticated and request.user.role == UserRole.STUDENT)
