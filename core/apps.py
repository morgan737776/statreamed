from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Основное приложение (Пациенты и Пользователи)'

    def ready(self):
        # Import and register template tags when the app is ready
        from . import templatetags  # noqa
