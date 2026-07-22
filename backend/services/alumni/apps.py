from django.apps import AppConfig


class AlumniConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.alumni"
    label = "alumni"
    verbose_name = "Alumni Management"

    def ready(self):
        import services.alumni.signals  # noqa: F401
