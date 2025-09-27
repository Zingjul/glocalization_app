from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = "notifications"

    def ready(self):
        """
        Ensure signals are imported when Django starts so they register.
        """
        try:
            import notifications.signals  # noqa: F401
        except Exception:
            # In case of circular imports while running tests or migrations, ignore.
            pass
