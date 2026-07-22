from django.apps import AppConfig


class CafeteriaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.cafeteria"
    label = "cafeteria"
    verbose_name = "Cafeteria / Meal Management"

    def ready(self):
        import services.cafeteria.signals  # noqa: F401
