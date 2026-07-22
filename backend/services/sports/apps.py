from django.apps import AppConfig


class SportsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.sports"
    label = "sports"
    verbose_name = "Sports & Extracurriculars"

    def ready(self):
        import services.sports.signals  # noqa: F401
