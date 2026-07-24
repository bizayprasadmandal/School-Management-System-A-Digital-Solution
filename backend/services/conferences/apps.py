from django.apps import AppConfig


class ConferencesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.conferences"
    label = "conferences"
    verbose_name = "Parent-Teacher Conferences"

    def ready(self):
        import services.conferences.signals  # noqa: F401 — imported for signal registration
