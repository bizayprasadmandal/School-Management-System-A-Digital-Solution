from django.apps import AppConfig


class InfrastructureConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.infrastructure"
    label = "infrastructure"
    verbose_name = "Infrastructure (backups, maintenance)"
