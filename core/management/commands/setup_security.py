# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.db import transaction
from django.conf import settings
import os
import sys


class Command(BaseCommand):
    """Команда для настройки системы безопасности и оптимизации"""
    
    help = 'Настраивает систему безопасности и оптимизацию приложения'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--security-only',
            action='store_true',
            help='Настроить только систему безопасности',
        )
        parser.add_argument(
            '--optimization-only',
            action='store_true',
            help='Настроить только оптимизацию',
        )
    
    def handle(self, *args, **options):
        """Основной метод команды"""
        try:
            self.stdout.write(
                self.style.SUCCESS('🔧 Начинается настройка системы...')
            )
            
            security_only = options.get('security_only', False)
            optimization_only = options.get('optimization_only', False)
            
            if not optimization_only:
                self.setup_security()
            
            if not security_only:
                self.setup_optimization()
            
            self.stdout.write(
                self.style.SUCCESS('🎉 Настройка системы завершена успешно!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка при настройке системы: {str(e)}')
            )
            sys.exit(1)
    
    def setup_security(self):
        """Настраивает систему безопасности"""
        self.stdout.write('🔒 Настройка системы безопасности...')
        
        # Проверяем настройки безопасности
        security_issues = []
        
        if settings.DEBUG:
            security_issues.append("DEBUG=True в продакшн среде небезопасно")
        
        if not getattr(settings, 'SESSION_COOKIE_SECURE', False):
            security_issues.append("SESSION_COOKIE_SECURE должен быть True для HTTPS")
        
        if not getattr(settings, 'CSRF_COOKIE_SECURE', False):
            security_issues.append("CSRF_COOKIE_SECURE должен быть True для HTTPS")
        
        if not getattr(settings, 'SECURE_SSL_REDIRECT', False):
            security_issues.append("SECURE_SSL_REDIRECT должен быть True для продакшн")
        
        if getattr(settings, 'ALLOWED_HOSTS', []) == ['*']:
            security_issues.append("ALLOWED_HOSTS не должен содержать '*' в продакшн")
        
        # Выводим предупреждения
        for issue in security_issues:
            self.stdout.write(f"⚠️  {issue}")
        
        if security_issues:
            self.stdout.write(f"Найдено {len(security_issues)} потенциальных проблем безопасности")
        else:
            self.stdout.write("✅ Настройки безопасности в порядке")
        
        self.stdout.write(
            self.style.SUCCESS('✅ Анализ безопасности завершен')
        )
    
    def setup_optimization(self):
        """Настраивает оптимизацию системы"""
        self.stdout.write('⚡ Настройка оптимизации системы...')
        
        # Очищаем кэш
        self.stdout.write('🧹 Очистка кэша безопасности...')
        try:
            if hasattr(cache, 'clear'):
                cache.clear()
                self.stdout.write("✅ Кэш очищен")
            else:
                self.stdout.write("⚠️  Кэш не поддерживает метод clear()")
        except Exception as e:
            self.stdout.write(f"⚠️  Предупреждение при очистке кэша: {e}")
        
        # Проверяем настройки производительности
        self.check_performance_settings()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Оптимизация системы настроена')
        )
    
    def check_performance_settings(self):
        """Проверяет настройки производительности"""
        self.stdout.write('📊 Проверка настроек производительности...')
        
        performance_issues = []
        
        # Проверяем настройки базы данных
        databases = getattr(settings, 'DATABASES', {})
        default_db = databases.get('default', {})
        
        if default_db.get('ENGINE') == 'django.db.backends.sqlite3':
            performance_issues.append("SQLite может быть медленным для продакшн")
        
        # Проверяем кэширование
        caches = getattr(settings, 'CACHES', {})
        default_cache = caches.get('default', {})
        
        if default_cache.get('BACKEND') == 'django.core.cache.backends.dummy.DummyCache':
            performance_issues.append("DummyCache отключает кэширование")
        
        # Проверяем статические файлы
        if not getattr(settings, 'USE_TZ', True):
            performance_issues.append("USE_TZ должен быть True")
        
        # Выводим рекомендации
        for issue in performance_issues:
            self.stdout.write(f"💡 Рекомендация: {issue}")
        
        if not performance_issues:
            self.stdout.write("✅ Настройки производительности в порядке")
