from django.apps import AppConfig

class StudentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.students"
    label = "students"
    verbose_name = "Students"

    def ready(self):
        import services.students.signals  # noqa
