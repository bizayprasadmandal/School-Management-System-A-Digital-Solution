from django.apps import AppConfig


class StudentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.students"
    label = "students"
    verbose_name = "Students"

    def ready(self):
        """Register signal handlers for the students app."""
        import services.students.signals  # noqa: F401 — imported for signal registration
