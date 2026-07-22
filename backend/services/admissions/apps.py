from django.apps import AppConfig


class AdmissionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.admissions"
    label = "admissions"
    verbose_name = "Admissions / Enrollment"

    def ready(self):
        import services.admissions.signals  # noqa: F401
