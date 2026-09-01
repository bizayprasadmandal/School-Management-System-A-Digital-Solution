import uuid

from django.db import models
from django.utils import timezone
from services.auth.models import School, User
from services.students.models import Grade, Student


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

    def __str__(self):
        return f"{self.student} — {self.book.title}"

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
    library_section = models.CharField(
        max_length=30, choices=LibrarySection.choices, blank=True, help_text="Primary library section"
    )
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


# =============================================================================
# NEW MODELS: Book Categories
# =============================================================================


class BookCategory(models.Model):
    """Organized book categories and genres."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="book_categories")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent_category = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="subcategories"
    )
    dewey_code = models.CharField(max_length=20, blank=True, help_text="Dewey Decimal Classification code")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "book_categories"
        ordering = ["name"]
        verbose_name_plural = "Book Categories"

    def __str__(self):
        return self.name


# =============================================================================
# NEW MODELS: Book Reservations
# =============================================================================


class BookReservation(models.Model):
    """Reserve books and holds."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        FULFILLED = "fulfilled", "Fulfilled"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reservations")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="book_reservations")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    reserved_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Reservation expiry date")
    notified = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "book_reservations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["book", "status"]),
            models.Index(fields=["student", "status"]),
        ]

    def __str__(self):
        return f"{self.student} reserved {self.book}"

    @property
    def is_expired(self):
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at


# =============================================================================
# NEW MODELS: Reading Lists
# =============================================================================


class ReadingList(models.Model):
    """Teacher-curated reading lists."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="reading_lists")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_reading_lists")
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True, related_name="reading_lists")
    subject = models.ForeignKey(
        "academics.Subject", on_delete=models.SET_NULL, null=True, blank=True, related_name="reading_lists"
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    is_mandatory = models.BooleanField(default=False, help_text="Required reading for students")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reading_lists"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def book_count(self):
        return self.items.count()


class ReadingListItem(models.Model):
    """Individual items in a reading list."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reading_list = models.ForeignKey(ReadingList, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reading_list_items")
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reading_list_items"
        ordering = ["order"]
        unique_together = [("reading_list", "book")]

    def __str__(self):
        return f"{self.reading_list.name} — {self.book.title}"


# =============================================================================
# NEW MODELS: Digital Resources
# =============================================================================


class DigitalResource(models.Model):
    """E-books, audiobooks, digital media."""

    class ResourceType(models.TextChoices):
        EBOOK = "ebook", "E-Book"
        AUDIOBOOK = "audiobook", "Audiobook"
        VIDEO = "video", "Video"
        ARTICLE = "article", "Article"
        DATABASE = "database", "Database"
        PODCAST = "podcast", "Podcast"
        INTERACTIVE = "interactive", "Interactive"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="digital_resources")
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=15, choices=ResourceType.choices, default=ResourceType.EBOOK)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True, help_text="Link to digital resource")
    file = models.FileField(upload_to="digital_resources/", null=True, blank=True)
    category = models.ForeignKey(BookCategory, on_delete=models.SET_NULL, null=True, blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Duration for audio/video")
    page_count = models.PositiveIntegerField(null=True, blank=True)
    file_size_mb = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    language = models.CharField(max_length=50, default="English")
    max_concurrent_users = models.PositiveIntegerField(default=1)
    current_users = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    access_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "digital_resources"
        ordering = ["title"]
        indexes = [
            models.Index(fields=["school", "resource_type"]),
            models.Index(fields=["school", "is_active"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"

    @property
    def is_available(self):
        return self.current_users < self.max_concurrent_users


# =============================================================================
# NEW MODELS: Inventory Management
# =============================================================================


class InventoryManagement(models.Model):
    """Stock management and auditing."""

    class AuditType(models.TextChoices):
        FULL = "full", "Full Audit"
        PARTIAL = "partial", "Partial Audit"
        SPOT_CHECK = "spot_check", "Spot Check"
        ANNUAL = "annual", "Annual Audit"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="inventory_audits")
    name = models.CharField(max_length=200)
    audit_type = models.CharField(max_length=15, choices=AuditType.choices, default=AuditType.PARTIAL)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    conducted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="conducted_audits")
    total_books_expected = models.PositiveIntegerField(default=0)
    total_books_found = models.PositiveIntegerField(default=0)
    total_missing = models.PositiveIntegerField(default=0)
    total_damaged = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inventory_audits"
        ordering = ["-scheduled_date"]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    @property
    def accuracy_percentage(self):
        if self.total_books_expected == 0:
            return 0
        return round((self.total_books_found / self.total_books_expected) * 100, 2)


class InventoryAuditItem(models.Model):
    """Individual audit items."""

    class Condition(models.TextChoices):
        GOOD = "good", "Good"
        FAIR = "fair", "Fair"
        POOR = "poor", "Poor"
        DAMAGED = "damaged", "Damaged"
        LOST = "lost", "Lost"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audit = models.ForeignKey(InventoryManagement, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="audit_items")
    expected_copies = models.PositiveIntegerField(default=0)
    found_copies = models.PositiveIntegerField(default=0)
    condition = models.CharField(max_length=10, choices=Condition.choices, default=Condition.GOOD)
    shelf_location = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inventory_audit_items"
        unique_together = [("audit", "book")]

    def __str__(self):
        return f"{self.book.title} — {self.found_copies}/{self.expected_copies}"

    @property
    def discrepancy(self):
        return self.expected_copies - self.found_copies


# =============================================================================
# NEW MODELS: Barcode Tracking
# =============================================================================


class BarcodeTracking(models.Model):
    """Barcode/RFID tracking for books."""

    class TrackingType(models.TextChoices):
        BARCODE = "barcode", "Barcode"
        RFID = "rfid", "RFID"
        QR_CODE = "qr_code", "QR Code"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        DAMAGED = "damaged", "Damaged"
        LOST = "lost", "Lost"
        DEACTIVATED = "deactivated", "Deactivated"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="barcode_records")
    tracking_type = models.CharField(max_length=10, choices=TrackingType.choices, default=TrackingType.BARCODE)
    barcode_value = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    copy_number = models.PositiveIntegerField(default=1, help_text="Copy number for multi-copy books")
    assigned_at = models.DateTimeField(auto_now_add=True)
    last_scanned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "barcode_tracking"
        indexes = [
            models.Index(fields=["barcode_value"]),
            models.Index(fields=["book", "status"]),
        ]

    def __str__(self):
        return f"{self.barcode_value} — {self.book.title}"


# =============================================================================
# NEW MODELS: Fine Management
# =============================================================================


class FineManagement(models.Model):
    """Fine calculation and payment."""

    class FineType(models.TextChoices):
        OVERDUE = "overdue", "Overdue Fine"
        LOST_BOOK = "lost_book", "Lost Book"
        DAMAGED_BOOK = "damaged_book", "Damaged Book"
        LATE_RETURN = "late_return", "Late Return"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PARTIAL = "partial", "Partially Paid"
        PAID = "paid", "Paid"
        WAIVED = "waived", "Waived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="library_fines")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="library_fines")
    checkout = models.ForeignKey(Checkout, on_delete=models.SET_NULL, null=True, blank=True, related_name="fines")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="fines")
    fine_type = models.CharField(max_length=15, choices=FineType.choices, default=FineType.OVERDUE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    days_overdue = models.PositiveIntegerField(default=0)
    reason = models.TextField(blank=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="issued_fines")
    waived_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="waived_fines")
    waive_reason = models.TextField(blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "library_fines"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["student", "status"]),
            models.Index(fields=["school", "status"]),
        ]

    def __str__(self):
        return f"{self.student} — {self.get_fine_type_display()}: {self.amount}"

    @property
    def outstanding_amount(self):
        return self.amount - self.amount_paid


class FinePayment(models.Model):
    """Track fine payments."""

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        CARD = "card", "Card"
        ONLINE = "online", "Online"
        CHECK = "check", "Check"
        WAIVED = "waived", "Waived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fine = models.ForeignKey(FineManagement, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="received_payments")
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "fine_payments"
        ordering = ["-paid_at"]

    def __str__(self):
        return f"Payment of {self.amount} for {self.fine}"


# =============================================================================
# NEW MODELS: Library Analytics
# =============================================================================


class LibraryAnalytics(models.Model):
    """Usage statistics and reports."""

    class AnalyticsType(models.TextChoices):
        DAILY = "daily", "Daily Report"
        WEEKLY = "weekly", "Weekly Report"
        MONTHLY = "monthly", "Monthly Report"
        TERM = "term", "Term Report"
        ANNUAL = "annual", "Annual Report"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="library_analytics")
    report_type = models.CharField(max_length=10, choices=AnalyticsType.choices, default=AnalyticsType.MONTHLY)
    period_start = models.DateField()
    period_end = models.DateField()
    # Circulation stats
    total_checkouts = models.PositiveIntegerField(default=0)
    total_returns = models.PositiveIntegerField(default=0)
    total_renewals = models.PositiveIntegerField(default=0)
    total_reservations = models.PositiveIntegerField(default=0)
    # Book stats
    total_books = models.PositiveIntegerField(default=0)
    new_books_added = models.PositiveIntegerField(default=0)
    books_lost = models.PositiveIntegerField(default=0)
    books_damaged = models.PositiveIntegerField(default=0)
    # User stats
    active_users = models.PositiveIntegerField(default=0)
    new_users = models.PositiveIntegerField(default=0)
    # Popular books
    popular_books = models.JSONField(default=list, blank=True)
    # Fine stats
    total_fines = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fines_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Digital resource stats
    digital_resource_access = models.PositiveIntegerField(default=0)
    # Metadata
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    report_data = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "library_analytics"
        ordering = ["-period_start"]
        indexes = [
            models.Index(fields=["school", "report_type"]),
            models.Index(fields=["period_start", "period_end"]),
        ]

    def __str__(self):
        return f"{self.get_report_type_display()} ({self.period_start} to {self.period_end})"

    @property
    def turnover_rate(self):
        if self.total_books == 0:
            return 0
        return round(self.total_checkouts / self.total_books, 2)


# =============================================================================
# NEW MODELS: Library Events
# =============================================================================


class LibraryEvent(models.Model):
    """Book fairs, author visits, reading programs."""

    class EventType(models.TextChoices):
        BOOK_FAIR = "book_fair", "Book Fair"
        AUTHOR_VISIT = "author_visit", "Author Visit"
        READING_PROGRAM = "reading_program", "Reading Program"
        STORY_TIME = "story_time", "Story Time"
        BOOK_CLUB = "book_club", "Book Club"
        WORKSHOP = "workshop", "Workshop"
        EXHIBITION = "exhibition", "Exhibition"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        UPCOMING = "upcoming", "Upcoming"
        ONGOING = "ongoing", "Ongoing"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="library_events")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=15, choices=EventType.choices, default=EventType.OTHER)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UPCOMING)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    max_participants = models.PositiveIntegerField(default=50)
    current_participants = models.PositiveIntegerField(default=0)
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="organized_library_events")
    is_mandatory = models.BooleanField(default=False)
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True, related_name="library_events")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "library_events"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} ({self.get_event_type_display()})"

    @property
    def is_full(self):
        return self.current_participants >= self.max_participants

    @property
    def available_spots(self):
        return max(0, self.max_participants - self.current_participants)


class EventRegistration(models.Model):
    """Event registrations."""

    class Status(models.TextChoices):
        REGISTERED = "registered", "Registered"
        ATTENDED = "attended", "Attended"
        CANCELLED = "cancelled", "Cancelled"
        WAITLISTED = "waitlisted", "Waitlisted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(LibraryEvent, on_delete=models.CASCADE, related_name="registrations")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="event_registrations")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.REGISTERED)
    registered_at = models.DateTimeField(auto_now_add=True)
    attended_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "event_registrations"
        unique_together = [("event", "student")]
        ordering = ["-registered_at"]

    def __str__(self):
        return f"{self.student} — {self.event}"


# =============================================================================
# NEW MODELS: Book Reviews
# =============================================================================


class BookReview(models.Model):
    """Student reviews and ratings."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="book_reviews")
    rating = models.PositiveSmallIntegerField(help_text="Rating from 1 to 5")
    title = models.CharField(max_length=200, blank=True)
    review_text = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    helpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "book_reviews"
        unique_together = [("book", "student")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} — {self.book.title} ({self.rating}/5)"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.rating < 1 or self.rating > 5:
            raise ValidationError("Rating must be between 1 and 5")


# =============================================================================
# NEW MODELS: Inter-Library Loan
# =============================================================================


class InterLibraryLoan(models.Model):
    """Borrow from other libraries."""

    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        APPROVED = "approved", "Approved"
        IN_TRANSIT = "in_transit", "In Transit"
        RECEIVED = "received", "Received"
        RETURNED = "returned", "Returned"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="inter_library_loans")
    requesting_student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="inter_library_requests")
    book_title = models.CharField(max_length=255)
    book_author = models.CharField(max_length=255, blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    lending_library = models.CharField(max_length=200, help_text="Name of lending library")
    lending_library_contact = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.REQUESTED)
    requested_date = models.DateField(auto_now_add=True)
    expected_arrival = models.DateField(null=True, blank=True)
    actual_arrival = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    returned_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inter_library_loans"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.book_title} — {self.requesting_student}"


# =============================================================================
# NEW MODELS: Book Recommendations
# =============================================================================


class BookRecommendation(models.Model):
    """AI-powered book recommendations."""

    class RecommendationType(models.TextChoices):
        POPULAR = "popular", "Popular in School"
        SIMILAR = "similar", "Similar to Read"
        CURATED = "curated", "Librarian Curated"
        TRENDING = "trending", "Trending Now"
        NEW_ARRIVAL = "new_arrival", "New Arrival"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="book_recommendations")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="recommendations")
    recommendation_type = models.CharField(
        max_length=15, choices=RecommendationType.choices, default=RecommendationType.POPULAR
    )
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Relevance score 0-100")
    reason = models.TextField(blank=True, help_text="Why this book was recommended")
    is_dismissed = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "book_recommendations"
        ordering = ["-score", "-created_at"]
        indexes = [
            models.Index(fields=["student", "is_dismissed"]),
            models.Index(fields=["student", "recommendation_type"]),
        ]

    def __str__(self):
        return f"{self.student} — {self.book.title} ({self.score})"


# =============================================================================
# NEW MODELS: Library Notifications
# =============================================================================


class LibraryNotification(models.Model):
    """Overdue reminders, new arrivals."""

    class NotificationType(models.TextChoices):
        OVERDUE_REMINDER = "overdue_reminder", "Overdue Reminder"
        BOOK_DUE_SOON = "book_due_soon", "Book Due Soon"
        BOOK_AVAILABLE = "book_available", "Reserved Book Available"
        NEW_ARRIVAL = "new_arrival", "New Arrival"
        FINE_NOTICE = "fine_notice", "Fine Notice"
        EVENT_REMINDER = "event_reminder", "Event Reminder"
        RECOMMENDATION = "recommendation", "Book Recommendation"

    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        PUSH = "push", "Push Notification"
        IN_APP = "in_app", "In-App"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="library_notifications")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="library_notifications")
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.IN_APP)
    title = models.CharField(max_length=200)
    message = models.TextField()
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True)
    checkout = models.ForeignKey(Checkout, on_delete=models.SET_NULL, null=True, blank=True)
    event = models.ForeignKey(LibraryEvent, on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "library_notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["student", "is_read"]),
            models.Index(fields=["school", "notification_type"]),
        ]

    def __str__(self):
        return f"{self.student} — {self.get_notification_type_display()}"


class BookCopy(models.Model):
    """Individual book copies."""

    class Condition(models.TextChoices):
        NEW = "new", "New"
        GOOD = "good", "Good"
        FAIR = "fair", "Fair"
        POOR = "poor", "Poor"
        DAMAGED = "damaged", "Damaged"
        LOST = "lost", "Lost"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="copies")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="book_copies")
    copy_number = models.CharField(max_length=50)
    barcode = models.CharField(max_length=100, unique=True)
    condition = models.CharField(max_length=20, choices=Condition.choices, default=Condition.GOOD)
    location = models.CharField(max_length=100, blank=True)
    shelf_number = models.CharField(max_length=20, blank=True)
    is_available = models.BooleanField(default=True)
    is_reference_only = models.BooleanField(default=False)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "library_book_copies"
        unique_together = [("book", "copy_number")]
        ordering = ["copy_number"]

    def __str__(self):
        return f"{self.book.title} - Copy {self.copy_number}"


class BookConditionLog(models.Model):
    """Book condition tracking."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE, related_name="condition_logs")
    previous_condition = models.CharField(max_length=20, choices=BookCopy.Condition.choices)
    new_condition = models.CharField(max_length=20, choices=BookCopy.Condition.choices)
    reason = models.TextField(blank=True)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "library_book_condition_logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.book_copy} - {self.previous_condition} to {self.new_condition}"


class BookRepair(models.Model):
    """Book repair records."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE, related_name="repairs")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="book_repairs")
    issue = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vendor = models.CharField(max_length=200, blank=True)
    scheduled_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "library_book_repairs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Repair: {self.book_copy} - {self.issue}"


class BookDonation(models.Model):
    """Book donations."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RECEIVED = "received", "Received"
        CATALOGED = "cataloged", "Cataloged"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="book_donations")
    donor_name = models.CharField(max_length=200)
    donor_email = models.EmailField(blank=True)
    donor_phone = models.CharField(max_length=20, blank=True)
    book_title = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    condition = models.CharField(max_length=20, choices=BookCopy.Condition.choices, default=BookCopy.Condition.GOOD)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    received_date = models.DateField(null=True, blank=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "library_book_donations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Donation: {self.book_title} by {self.donor_name}"


class BookPurchase(models.Model):
    """Book purchases."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ORDERED = "ordered", "Ordered"
        RECEIVED = "received", "Received"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="book_purchases")
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vendor = models.CharField(max_length=200, blank=True)
    order_date = models.DateField(null=True, blank=True)
    expected_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="book_purchase_approvals"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "library_book_purchases"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Purchase: {self.title} (Qty: {self.quantity})"


class LibraryCard(models.Model):
    """Library card management."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        LOST = "lost", "Lost"
        BLOCKED = "blocked", "Blocked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="library_cards")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="library_cards")
    card_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    max_checkouts = models.PositiveIntegerField(default=5)
    current_checkouts = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "library_cards"
        ordering = ["-issue_date"]

    def __str__(self):
        return f"Card {self.card_number} - {self.student}"


class AcquisitionRequest(models.Model):
    """Book acquisition requests."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        ORDERED = "ordered", "Ordered"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="acquisition_requests")
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="acquisition_requests")
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reason = models.TextField()
    priority = models.CharField(
        max_length=20, choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")], default="medium"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "library_acquisition_requests"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Request: {self.title} by {self.requested_by.full_name}"


class BookClub(models.Model):
    """Book club management."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="book_clubs")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    advisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    meeting_day = models.CharField(max_length=20, blank=True)
    meeting_time = models.TimeField(null=True, blank=True)
    meeting_location = models.CharField(max_length=200, blank=True)
    max_members = models.PositiveIntegerField(default=20)
    current_book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "library_book_clubs"
        ordering = ["name"]

    def __str__(self):
        return self.name


class BookClubMembership(models.Model):
    """Book club membership."""

    class Role(models.TextChoices):
        MEMBER = "member", "Member"
        PRESIDENT = "president", "President"
        SECRETARY = "secretary", "Secretary"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_club = models.ForeignKey(BookClub, on_delete=models.CASCADE, related_name="members")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="book_club_memberships")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    join_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "library_book_club_memberships"
        unique_together = [("book_club", "student")]
        ordering = ["-join_date"]

    def __str__(self):
        return f"{self.student} - {self.book_club.name}"


class StudentReadingLog(models.Model):
    """Student reading logs."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="reading_logs")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_reading_logs")
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True)
    book_title = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True)
    pages_read = models.PositiveIntegerField(default=0)
    total_pages = models.PositiveIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True, help_text="1-5 rating")
    review = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "library_student_reading_logs"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.student} - {self.book_title}"


class ReadingChallenge(models.Model):
    """Reading challenges."""

    class Status(models.TextChoices):
        UPCOMING = "upcoming", "Upcoming"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="reading_challenges")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    goal_books = models.PositiveIntegerField(default=5)
    goal_pages = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPCOMING)
    prize = models.CharField(max_length=200, blank=True)
    participants_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "library_reading_challenges"
        ordering = ["-start_date"]

    def __str__(self):
        return self.name


class ReadingChallengeProgress(models.Model):
    """Reading challenge progress."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    challenge = models.ForeignKey(ReadingChallenge, on_delete=models.CASCADE, related_name="progress")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="reading_challenge_progress")
    books_read = models.PositiveIntegerField(default=0)
    pages_read = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "library_reading_challenge_progress"
        unique_together = [("challenge", "student")]
        ordering = ["-books_read"]

    def __str__(self):
        return f"{self.student} - {self.challenge.name} ({self.books_read} books)"


class LibraryFeedback(models.Model):
    """Library feedback surveys."""

    class FeedbackType(models.TextChoices):
        SERVICE = "service", "Service"
        COLLECTION = "collection", "Collection"
        FACILITY = "facility", "Facility"
        STAFF = "staff", "Staff"
        GENERAL = "general", "General"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="library_feedback")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="library_feedback")
    feedback_type = models.CharField(max_length=20, choices=FeedbackType.choices)
    rating = models.PositiveSmallIntegerField(help_text="1-5 rating")
    comments = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    response = models.TextField(blank=True)
    responded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "library_feedback"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Feedback: {self.student} - {self.get_feedback_type_display()}"
