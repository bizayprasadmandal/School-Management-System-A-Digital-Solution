from django.apps import AppConfig

class AttendanceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "services.attendance"
    label = "attendance"
    verbose_name = "Attendance"

    def ready(self):
        import services.attendance.signals  # noqa
