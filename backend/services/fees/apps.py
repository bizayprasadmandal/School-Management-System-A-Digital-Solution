from django.apps import AppConfig

class FeesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.fees"
    label = "fees"
    verbose_name = "Fee Management"

    def ready(self):
        import services.fees.signals  # noqa
