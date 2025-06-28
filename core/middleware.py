from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
from core.models import SystemSettings

class MaintenanceModeMiddleware:
    """
    Middleware для вывода страницы "Техническое обслуживание" для всех пользователей, кроме суперпользователей,
    если maintenance_mode включён в SystemSettings.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            maintenance = SystemSettings.objects.get(pk=1).maintenance_mode
        except Exception:
            maintenance = False
        # Не блокируем админку и медиа, и разрешаем суперпользователям
        if maintenance:
            if request.user.is_authenticated and request.user.is_superuser:
                return self.get_response(request)
            allowed_paths = [reverse('admin:login'), reverse('core:settings')]
            if any(request.path.startswith(p) for p in allowed_paths) or request.path.startswith(settings.STATIC_URL) or request.path.startswith(settings.MEDIA_URL):
                return self.get_response(request)
            return render(request, 'core/maintenance.html', status=503)
        return self.get_response(request)
