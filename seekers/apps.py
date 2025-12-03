from django.apps import AppConfig

class SeekersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "seekers"

    def ready(self):
        import seekers.signals
