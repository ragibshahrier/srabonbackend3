from django.apps import AppConfig

class OrchestratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orchestrator'

    def ready(self):
        import orchestrator.signals
        # Ensure that the signals are imported and connected when the app is ready