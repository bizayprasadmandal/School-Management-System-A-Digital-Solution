import uuid
from django.db import models
from django.utils import timezone
from services.auth.models import User, School
from services.students.models import Student, Grade


class Book(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="books")
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=50, blank=True)
    shelf_location = models.CharField(max_length=50, blank=True)
    total_copies = models.PositiveSmallIntegerField(default=1)
    available_copies = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "books"
        indexes = [models.Index(fields=["school", "is_active"])]

    def __str__(self):
        return f"{self.title} by {self.author}"


class Checkout(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="checkouts")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="book_checkouts")
    checked_out_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    checked_out_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fine_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "checkouts"

    @property
    def is_overdue(self):
        if self.returned_at:
            return False
        return timezone.now().date() > self.due_date

    @property
    def days_overdue(self):
        if not self.is_overdue:
            return 0
        return (timezone.now().date() - self.due_date).days


class LibrarianProfile(models.Model):
    """Extended librarian profile — professional information for self-service editing."""

    class LibrarySection(models.TextChoices):
        CIRCULATION = "circulation", "Circulation"
        REFERENCE = "reference", "Reference"
        CATALOGING = "cataloging", "Cataloging"
        PERIODICALS = "periodicals", "Periodicals"
        DIGITAL = "digital", "Digital Library"
        ARCHIVES = "archives", "Archives"
        CHILDREN = "children", "Children's Section"
        GENERAL = "general", "General"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="librarian_profile")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="librarian_profiles")
    library_section = models.CharField(max_length=30, choices=LibrarySection.choices, blank=True, help_text="Primary library section")
    qualification = models.CharField(max_length=100, blank=True, help_text="Library science or relevant qualification")
    experience_years = models.PositiveSmallIntegerField(default=0, help_text="Years of library experience")
    certifications = models.TextField(blank=True, help_text="Professional certifications")
    bio = models.TextField(blank=True, help_text="Professional biography")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "librarian_profiles"
        verbose_name = "Librarian Profile"
        verbose_name_plural = "Librarian Profiles"

    def __str__(self):
        return f"{self.user.full_name} — Librarian Profile"
