from django.apps import AppConfig


class LearningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'learning'
    verbose_name = 'Learning Content'

    def ready(self):
        import learning.signals  # noqa