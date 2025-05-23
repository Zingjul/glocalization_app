from django.apps import AppConfig

class PersonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "person"

    def ready(self):
        import person.signals  # Ensures signals are registered
