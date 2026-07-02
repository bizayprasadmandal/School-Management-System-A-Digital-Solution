"""Auth Service — Custom managers for multi-tenant user queries."""
from django.contrib.auth.models import BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Handles user creation with email as primary identifier."""

    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("role", "super_admin")
        return self.create_user(email, password, **extra)

    def for_school(self, school):
        return self.filter(school=school, is_active=True)

    def admins(self, school):
        return self.for_school(school).filter(role__in=["school_admin", "super_admin"])

    def teachers(self, school):
        return self.for_school(school).filter(role="teacher")

    def students(self, school):
        return self.for_school(school).filter(role="student")

    def parents(self, school):
        return self.for_school(school).filter(role="parent")


class ActiveSchoolManager(models.Manager):
    """Filters to active schools only."""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
