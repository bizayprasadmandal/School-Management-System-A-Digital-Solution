from django.apps import AppConfig


class BehaviorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.behavior"
    label = "behavior"
    verbose_name = "Behavior & Discipline Tracking"
