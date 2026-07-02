from django.apps import AppConfig

class ReportingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.reporting"
    label = "reporting"
    verbose_name = "Reporting"
