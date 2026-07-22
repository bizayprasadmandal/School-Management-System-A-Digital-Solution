from django.apps import AppConfig


class HealthClinicConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.health_clinic"
    label = "health_clinic"
    verbose_name = "Health & Clinic"

    def ready(self):
        import services.health_clinic.signals  # noqa: F401
