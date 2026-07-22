"""
Counseling Service — Django AppConfig with signal registration.
"""

from django.apps import AppConfig


class CounselingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.counseling"
    label = "counseling"
    verbose_name = "Counseling & Guidance"

    def ready(self):
        """Register signal handlers."""
        import services.counseling.signals  # noqa: F401
