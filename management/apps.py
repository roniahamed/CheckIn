from django.apps import AppConfig


class ManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'management'
    
    def ready(self):
        # Import signal handlers
        from . import signals  # noqa: F401
