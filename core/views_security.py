"""
Представления для мониторинга безопасности системы
"""
import os
from datetime import datetime, timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.db.models import Count
from auditlog.models import LogEntry
from .models import Staff, Patient, Appointment
import json


def is_admin(user):
    """Проверка что пользователь является администратором"""
    return user.is_superuser or user.is_staff


@login_required
@user_passes_test(is_admin)
def security_dashboard(request):
    """Дашборд безопасности"""
    context = {
        'title': 'Мониторинг безопасности',
        'active_sessions': get_active_sessions_count(),
        'recent_logins': get_recent_logins(),
        'security_warnings': get_security_warnings(),
        'audit_logs': get_recent_audit_logs(),
        'failed_logins': get_failed_login_attempts(),
        'system_health': get_system_health(),
    }
    return render(request, 'core/security/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def security_api_stats(request):
    """API для получения статистики безопасности"""
    data = {
        'active_sessions': get_active_sessions_count(),
        'recent_logins_count': get_recent_logins_count(),
        'security_warnings_count': len(get_security_warnings()),
        'audit_logs_count': get_recent_audit_logs_count(),
        'failed_logins_count': get_failed_login_attempts_count(),
        'system_health': get_system_health(),
        'last_updated': datetime.now().isoformat(),
    }
    return JsonResponse(data)


def get_active_sessions_count():
    """Получить количество активных сессий"""
    try:
        return Session.objects.filter(expire_date__gte=datetime.now()).count()
    except Exception:
        return 0


def get_recent_logins():
    """Получить последние входы в систему"""
    try:
        # Получаем последние записи аудита о входах
        recent_entries = LogEntry.objects.filter(
            action=LogEntry.Action.CREATE,
            content_type__model='user',
            timestamp__gte=datetime.now() - timedelta(days=7)
        ).order_by('-timestamp')[:10]
        
        logins = []
        for entry in recent_entries:
            logins.append({
                'user': entry.actor.username if entry.actor else 'Unknown',
                'timestamp': entry.timestamp,
                'ip_address': entry.remote_addr or 'Unknown',
                'user_agent': entry.additional_data.get('user_agent', 'Unknown') if entry.additional_data else 'Unknown'
            })
        
        return logins
    except Exception:
        return []


def get_recent_logins_count():
    """Получить количество последних входов"""
    try:
        return LogEntry.objects.filter(
            action=LogEntry.Action.CREATE,
            content_type__model='user',
            timestamp__gte=datetime.now() - timedelta(days=7)
        ).count()
    except Exception:
        return 0


def get_security_warnings():
    """Получить предупреждения безопасности"""
    warnings = []
    
    # Проверяем DEBUG режим
    if settings.DEBUG:
        warnings.append({
            'level': 'high',
            'message': 'DEBUG режим включен в продакшн среде',
            'recommendation': 'Установите DEBUG = False'
        })
    
    # Проверяем HTTPS настройки
    if not getattr(settings, 'SECURE_SSL_REDIRECT', False):
        warnings.append({
            'level': 'medium',
            'message': 'HTTPS перенаправление отключено',
            'recommendation': 'Включите SECURE_SSL_REDIRECT = True'
        })
    
    if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
        warnings.append({
            'level': 'medium',
            'message': 'Защищенные cookies отключены',
            'recommendation': 'Включите SESSION_COOKIE_SECURE = True'
        })
    
    # Проверяем SECRET_KEY
    if settings.SECRET_KEY.startswith('django-insecure-'):
        warnings.append({
            'level': 'critical',
            'message': 'Используется небезопасный SECRET_KEY',
            'recommendation': 'Сгенерируйте новый SECRET_KEY'
        })
    
    # Проверяем ALLOWED_HOSTS
    if '*' in settings.ALLOWED_HOSTS:
        warnings.append({
            'level': 'high',
            'message': 'ALLOWED_HOSTS содержит "*"',
            'recommendation': 'Укажите конкретные домены'
        })
    
    return warnings


def get_recent_audit_logs():
    """Получить последние записи аудита"""
    try:
        logs = LogEntry.objects.select_related('actor', 'content_type').order_by('-timestamp')[:20]
        
        result = []
        for log in logs:
            result.append({
                'timestamp': log.timestamp,
                'actor': log.actor.username if log.actor else 'System',
                'action': log.get_action_display(),
                'object': str(log.object_repr),
                'model': log.content_type.model if log.content_type else 'Unknown',
                'ip_address': log.remote_addr or 'Unknown'
            })
        
        return result
    except Exception:
        return []


def get_recent_audit_logs_count():
    """Получить количество записей аудита за последние 24 часа"""
    try:
        return LogEntry.objects.filter(
            timestamp__gte=datetime.now() - timedelta(days=1)
        ).count()
    except Exception:
        return 0


def get_failed_login_attempts():
    """Получить неудачные попытки входа (заглушка)"""
    # В реальном приложении здесь должна быть логика отслеживания неудачных входов
    return []


def get_failed_login_attempts_count():
    """Получить количество неудачных попыток входа"""
    return 0


def get_system_health():
    """Получить состояние системы"""
    health = {
        'status': 'healthy',
        'checks': []
    }
    
    # Проверяем подключение к базе данных
    try:
        User.objects.count()
        health['checks'].append({
            'name': 'База данных',
            'status': 'ok',
            'message': 'Подключение установлено'
        })
    except Exception as e:
        health['status'] = 'unhealthy'
        health['checks'].append({
            'name': 'База данных',
            'status': 'error',
            'message': f'Ошибка подключения: {str(e)}'
        })
    
    # Проверяем кэш
    try:
        cache.set('health_check', 'ok', 60)
        cache.get('health_check')
        health['checks'].append({
            'name': 'Кэш',
            'status': 'ok',
            'message': 'Работает корректно'
        })
    except Exception as e:
        health['checks'].append({
            'name': 'Кэш',
            'status': 'warning',
            'message': f'Проблемы с кэшем: {str(e)}'
        })
    
    # Проверяем доступность статических файлов
    try:
        static_root = getattr(settings, 'STATICFILES_DIRS', [])
        if static_root:
            health['checks'].append({
                'name': 'Статические файлы',
                'status': 'ok',
                'message': 'Путь настроен'
            })
        else:
            health['checks'].append({
                'name': 'Статические файлы',
                'status': 'warning',
                'message': 'STATICFILES_DIRS не настроен'
            })
    except Exception as e:
        health['checks'].append({
            'name': 'Статические файлы',
            'status': 'error',
            'message': f'Ошибка: {str(e)}'
        })
    
    return health


@login_required
@user_passes_test(is_admin)
def export_audit_logs(request):
    """Экспорт логов аудита"""
    try:
        logs = LogEntry.objects.select_related('actor', 'content_type').order_by('-timestamp')
        
        # Формируем данные для экспорта
        data = []
        for log in logs:
            data.append({
                'timestamp': log.timestamp.isoformat(),
                'actor': log.actor.username if log.actor else 'System',
                'action': log.get_action_display(),
                'object': str(log.object_repr),
                'model': log.content_type.model if log.content_type else 'Unknown',
                'ip_address': log.remote_addr or 'Unknown',
                'additional_data': log.additional_data or {}
            })
        
        response = JsonResponse({'logs': data})
        response['Content-Disposition'] = f'attachment; filename="audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
