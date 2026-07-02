from django.apps import AppConfig

class AuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.auth"
    label = "auth_service"
    verbose_name = "Authentication"
