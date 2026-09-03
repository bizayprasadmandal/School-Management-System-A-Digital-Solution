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
        # Direct messages carry sender/recipient instead of school/student
        if hasattr(obj, "sender") and hasattr(obj, "recipient"):
            return obj.sender_id == request.user.id or obj.recipient_id == request.user.id
        # Support objects with direct school FK or nested ones. Fail CLOSED:
        # an object we cannot prove belongs to the caller's school is denied.
        school_id = self._resolve_school_id(obj)
        return school_id is not None and school_id == request.user.school_id

    @staticmethod
    def _resolve_school_id(obj, _depth=0, _seen=None):
        """Resolve the owning school id through common FK paths (max 4 hops)."""
        if obj is None or _depth > 4:
            return None
        if _seen is None:
            _seen = set()
        marker = (id(obj), _depth)
        if marker in _seen:
            return None
        _seen.add(marker)

        # Direct school FK
        school = getattr(obj, "school", None)
        if school is not None:
            school_id = getattr(school, "id", None) or getattr(school, "school_id", None)
            if school_id is not None:
                return school_id
        # User-owner objects
        user = getattr(obj, "user", None)
        if user is not None:
            user_school_id = getattr(user, "school_id", None)
            if user_school_id is not None:
                return user_school_id
        # Common relation names that lead to a school
        for attr in (
            "subject",
            "student",
            "syllabus",
            "classroom",
            "assignment",
            "course",
            "grade",
            "teacher",
            "template",
            "created_by",
            "generated_by",
            "verified_by",
        ):
            related = getattr(obj, attr, None)
            if related is not None:
                resolved = IsSchoolMember._resolve_school_id(related, _depth + 1, _seen)
                if resolved is not None:
                    return resolved
        return None


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
