from django.apps import AppConfig


class HostelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.hostel"
    label = "hostel"
    verbose_name = "Hostel / Accommodation"
