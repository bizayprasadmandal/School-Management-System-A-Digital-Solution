from django.apps import AppConfig

class GradebookConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.gradebook"
    label = "gradebook"
    verbose_name = "Gradebook"

    def ready(self):
        import services.gradebook.signals  # noqa: F401 — imported for signal registration
