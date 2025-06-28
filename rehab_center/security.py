# -*- coding: utf-8 -*-
"""
Модуль для настроек безопасности Django-приложения
Включает конфигурацию для защиты от различных атак и уязвимостей
"""

import os
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils import timezone
import logging
import hashlib
import json
from datetime import timedelta

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Класс для управления настройками безопасности"""
    
    # Настройки для брутфорс защиты
    BRUTE_FORCE_PROTECTION = {
        'MAX_LOGIN_ATTEMPTS': 5,
        'LOCKOUT_DURATION': 900,  # 15 минут в секундах
        'RESET_TIME': 3600,  # 1 час в секундах
        'TRACK_BY_IP': True,
        'TRACK_BY_USERNAME': True,
    }
    
    # Настройки для защиты паролей
    PASSWORD_SECURITY = {
        'MIN_LENGTH': 8,
        'REQUIRE_UPPERCASE': True,
        'REQUIRE_LOWERCASE': True,
        'REQUIRE_NUMBERS': True,
        'REQUIRE_SPECIAL_CHARS': True,
        'FORBIDDEN_PASSWORDS': [
            'password', 'password123', '123456', 'qwerty',
            'admin', 'administrator', 'root', 'user'
        ]
    }
    
    # Настройки для сессий
    SESSION_SECURITY = {
        'SESSION_TIMEOUT': 3600,  # 1 час
        'ABSOLUTE_TIMEOUT': 28800,  # 8 часов
        'WARN_BEFORE_EXPIRY': 300,  # 5 минут
        'REQUIRE_FRESH_LOGIN': ['password_change', 'user_delete']
    }
    
    # Настройки для IP ограничений
    IP_RESTRICTIONS = {
        'WHITELIST': [],
        'BLACKLIST': [],
        'ADMIN_IP_WHITELIST': [],
        'MAX_REQUESTS_PER_MINUTE': 60,
        'MAX_REQUESTS_PER_HOUR': 1000
    }


class BruteForceProtection:
    """Класс для защиты от брутфорс атак"""
    
    @staticmethod
    def get_cache_key(identifier, attempt_type='login'):
        """
        Генерирует ключ кэша для отслеживания попыток
        
        Args:
            identifier: IP адрес или имя пользователя
            attempt_type: тип попытки (login, password_reset, etc.)
        
        Returns:
            str: ключ кэша
        """
        hash_input = f"{attempt_type}:{identifier}".encode('utf-8')
        return f"security:attempts:{hashlib.md5(hash_input).hexdigest()}"
    
    @staticmethod
    def record_failed_attempt(identifier, attempt_type='login'):
        """
        Записывает неудачную попытку входа
        
        Args:
            identifier: IP адрес или имя пользователя
            attempt_type: тип попытки
        
        Returns:
            dict: информация о попытках
        """
        cache_key = BruteForceProtection.get_cache_key(identifier, attempt_type)
        
        # Получаем текущие данные из кэша
        attempts_data = cache.get(cache_key, {
            'count': 0,
            'first_attempt': timezone.now().isoformat(),
            'last_attempt': None,
            'blocked_until': None
        })
        
        # Увеличиваем счетчик попыток
        attempts_data['count'] += 1
        attempts_data['last_attempt'] = timezone.now().isoformat()
        
        # Проверяем, нужно ли заблокировать
        max_attempts = SecurityConfig.BRUTE_FORCE_PROTECTION['MAX_LOGIN_ATTEMPTS']
        if attempts_data['count'] >= max_attempts:
            lockout_duration = SecurityConfig.BRUTE_FORCE_PROTECTION['LOCKOUT_DURATION']
            blocked_until = timezone.now() + timedelta(seconds=lockout_duration)
            attempts_data['blocked_until'] = blocked_until.isoformat()
            
            logger.warning(f"Заблокирован {attempt_type} для {identifier} до {blocked_until}")
        
        # Сохраняем данные в кэше
        reset_time = SecurityConfig.BRUTE_FORCE_PROTECTION['RESET_TIME']
        cache.set(cache_key, attempts_data, reset_time)
        
        return attempts_data
    
    @staticmethod
    def is_blocked(identifier, attempt_type='login'):
        """
        Проверяет, заблокирован ли идентификатор
        
        Args:
            identifier: IP адрес или имя пользователя
            attempt_type: тип попытки
        
        Returns:
            bool: True если заблокирован
        """
        cache_key = BruteForceProtection.get_cache_key(identifier, attempt_type)
        attempts_data = cache.get(cache_key, {})
        
        if not attempts_data.get('blocked_until'):
            return False
        
        blocked_until = timezone.datetime.fromisoformat(attempts_data['blocked_until'])
        
        # Проверяем, истекла ли блокировка
        if timezone.now() >= blocked_until:
            # Сбрасываем блокировку
            BruteForceProtection.reset_attempts(identifier, attempt_type)
            return False
        
        return True
    
    @staticmethod
    def reset_attempts(identifier, attempt_type='login'):
        """
        Сбрасывает счетчик попыток
        
        Args:
            identifier: IP адрес или имя пользователя
            attempt_type: тип попытки
        """
        cache_key = BruteForceProtection.get_cache_key(identifier, attempt_type)
        cache.delete(cache_key)
    
    @staticmethod
    def get_attempts_info(identifier, attempt_type='login'):
        """
        Получает информацию о попытках
        
        Args:
            identifier: IP адрес или имя пользователя
            attempt_type: тип попытки
        
        Returns:
            dict: информация о попытках
        """
        cache_key = BruteForceProtection.get_cache_key(identifier, attempt_type)
        return cache.get(cache_key, {})


class PasswordValidator:
    """Класс для валидации паролей"""
    
    @staticmethod
    def validate_password_strength(password):
        """
        Проверяет силу пароля
        
        Args:
            password: пароль для проверки
        
        Returns:
            dict: результат валидации
        """
        errors = []
        config = SecurityConfig.PASSWORD_SECURITY
        
        # Проверка длины
        if len(password) < config['MIN_LENGTH']:
            errors.append(f"Пароль должен содержать минимум {config['MIN_LENGTH']} символов")
        
        # Проверка на заглавные буквы
        if config['REQUIRE_UPPERCASE'] and not any(c.isupper() for c in password):
            errors.append("Пароль должен содержать заглавные буквы")
        
        # Проверка на строчные буквы
        if config['REQUIRE_LOWERCASE'] and not any(c.islower() for c in password):
            errors.append("Пароль должен содержать строчные буквы")
        
        # Проверка на цифры
        if config['REQUIRE_NUMBERS'] and not any(c.isdigit() for c in password):
            errors.append("Пароль должен содержать цифры")
        
        # Проверка на специальные символы
        if config['REQUIRE_SPECIAL_CHARS']:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                errors.append("Пароль должен содержать специальные символы")
        
        # Проверка на запрещенные пароли
        if password.lower() in [p.lower() for p in config['FORBIDDEN_PASSWORDS']]:
            errors.append("Пароль слишком простой или часто используемый")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'strength_score': PasswordValidator._calculate_strength_score(password)
        }
    
    @staticmethod
    def _calculate_strength_score(password):
        """
        Рассчитывает силу пароля от 0 до 100
        
        Args:
            password: пароль для оценки
        
        Returns:
            int: оценка силы пароля
        """
        score = 0
        
        # Базовые очки за длину
        score += min(len(password) * 4, 40)
        
        # Очки за разнообразие символов
        if any(c.isupper() for c in password):
            score += 10
        if any(c.islower() for c in password):
            score += 10
        if any(c.isdigit() for c in password):
            score += 10
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 10
        
        # Очки за длину свыше минимума
        if len(password) > 12:
            score += 10
        if len(password) > 16:
            score += 10
        
        return min(score, 100)


class IPRestrictionMiddleware:
    """Middleware для ограничения доступа по IP"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Получаем IP адрес клиента
        client_ip = self._get_client_ip(request)
        
        # Проверяем ограничения
        if not self._is_ip_allowed(client_ip, request):
            logger.warning(f"Доступ запрещен для IP {client_ip}")
            return HttpResponseForbidden("Доступ запрещен")
        
        # Проверяем ограничения по количеству запросов
        if not self._check_rate_limit(client_ip):
            logger.warning(f"Превышен лимит запросов для IP {client_ip}")
            return HttpResponseForbidden("Превышен лимит запросов")
        
        response = self.get_response(request)
        return response
    
    def _get_client_ip(self, request):
        """Получает IP адрес клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _is_ip_allowed(self, client_ip, request):
        """Проверяет, разрешен ли доступ для IP"""
        config = SecurityConfig.IP_RESTRICTIONS
        
        # Проверяем черный список
        if client_ip in config['BLACKLIST']:
            return False
        
        # Если есть белый список, проверяем его
        if config['WHITELIST'] and client_ip not in config['WHITELIST']:
            return False
        
        # Для админки проверяем отдельный белый список
        if request.path.startswith('/admin/'):
            admin_whitelist = config['ADMIN_IP_WHITELIST']
            if admin_whitelist and client_ip not in admin_whitelist:
                return False
        
        return True
    
    def _check_rate_limit(self, client_ip):
        """Проверяет ограничения по количеству запросов"""
        config = SecurityConfig.IP_RESTRICTIONS
        
        # Проверяем лимит в минуту
        minute_key = f"rate_limit:minute:{client_ip}:{timezone.now().strftime('%Y%m%d%H%M')}"
        minute_count = cache.get(minute_key, 0)
        
        if minute_count >= config['MAX_REQUESTS_PER_MINUTE']:
            return False
        
        # Проверяем лимит в час
        hour_key = f"rate_limit:hour:{client_ip}:{timezone.now().strftime('%Y%m%d%H')}"
        hour_count = cache.get(hour_key, 0)
        
        if hour_count >= config['MAX_REQUESTS_PER_HOUR']:
            return False
        
        # Увеличиваем счетчики
        cache.set(minute_key, minute_count + 1, 60)
        cache.set(hour_key, hour_count + 1, 3600)
        
        return True


class SecurityAuditLogger:
    """Класс для логирования событий безопасности"""
    
    @staticmethod
    def log_failed_login(username, ip_address, user_agent=None):
        """Логирует неудачную попытку входа"""
        logger.warning(
            f"Неудачная попытка входа - Пользователь: {username}, "
            f"IP: {ip_address}, User-Agent: {user_agent}"
        )
    
    @staticmethod
    def log_successful_login(username, ip_address, user_agent=None):
        """Логирует успешный вход"""
        logger.info(
            f"Успешный вход - Пользователь: {username}, "
            f"IP: {ip_address}, User-Agent: {user_agent}"
        )
    
    @staticmethod
    def log_password_change(username, ip_address):
        """Логирует смену пароля"""
        logger.info(
            f"Смена пароля - Пользователь: {username}, IP: {ip_address}"
        )
    
    @staticmethod
    def log_permission_denied(username, action, resource, ip_address):
        """Логирует отказ в доступе"""
        logger.warning(
            f"Отказ в доступе - Пользователь: {username}, "
            f"Действие: {action}, Ресурс: {resource}, IP: {ip_address}"
        )
    
    @staticmethod
    def log_security_event(event_type, description, username=None, ip_address=None):
        """Логирует произвольное событие безопасности"""
        logger.warning(
            f"Событие безопасности - Тип: {event_type}, "
            f"Описание: {description}, Пользователь: {username}, IP: {ip_address}"
        )


class SessionSecurityManager:
    """Класс для управления безопасностью сессий"""
    
    @staticmethod
    def check_session_security(request):
        """
        Проверяет безопасность сессии
        
        Args:
            request: HTTP запрос
        
        Returns:
            dict: результат проверки
        """
        if not request.user.is_authenticated:
            return {'valid': True, 'action': None}
        
        current_time = timezone.now()
        session = request.session
        
        # Проверяем таймаут сессии
        last_activity = session.get('last_activity')
        if last_activity:
            last_activity = timezone.datetime.fromisoformat(last_activity)
            timeout = SecurityConfig.SESSION_SECURITY['SESSION_TIMEOUT']
            
            if (current_time - last_activity).total_seconds() > timeout:
                return {'valid': False, 'action': 'timeout'}
        
        # Проверяем абсолютный таймаут
        session_start = session.get('session_start')
        if session_start:
            session_start = timezone.datetime.fromisoformat(session_start)
            absolute_timeout = SecurityConfig.SESSION_SECURITY['ABSOLUTE_TIMEOUT']
            
            if (current_time - session_start).total_seconds() > absolute_timeout:
                return {'valid': False, 'action': 'absolute_timeout'}
        
        # Обновляем время последней активности
        session['last_activity'] = current_time.isoformat()
        
        return {'valid': True, 'action': None}
    
    @staticmethod
    def initialize_session(request):
        """Инициализирует защищенную сессию"""
        current_time = timezone.now()
        request.session['session_start'] = current_time.isoformat()
        request.session['last_activity'] = current_time.isoformat()
        request.session['security_token'] = os.urandom(32).hex()
    
    @staticmethod
    def requires_fresh_login(action):
        """Проверяет, требуется ли свежий логин для действия"""
        sensitive_actions = SecurityConfig.SESSION_SECURITY['REQUIRE_FRESH_LOGIN']
        return action in sensitive_actions


def get_security_headers():
    """
    Возвращает словарь с заголовками безопасности
    
    Returns:
        dict: заголовки HTTP для безопасности
    """
    return {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'"
        ),
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
    }


class SecurityHeadersMiddleware:
    """Middleware для добавления заголовков безопасности"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # Добавляем заголовки безопасности
        security_headers = get_security_headers()
        for header, value in security_headers.items():
            response[header] = value
        
        return response
