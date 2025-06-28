"""
Команда для полной инициализации системы
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from django.db import connection
from core.models import SystemSettings
import os


class Command(BaseCommand):
    help = 'Инициализация системы: миграции, суперпользователь, настройки'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Пропустить миграции',
        )
        parser.add_argument(
            '--skip-superuser',
            action='store_true',
            help='Пропустить создание суперпользователя',
        )
        parser.add_argument(
            '--skip-settings',
            action='store_true',
            help='Пропустить инициализацию настроек',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Инициализация системы реабилитационного центра...')
        )
        self.stdout.write('')

        # 1. Применяем миграции
        if not options.get('skip_migrations'):
            self.stdout.write('📦 Применение миграций...')
            try:
                call_command('migrate', verbosity=0)
                self.stdout.write(
                    self.style.SUCCESS('✅ Миграции применены успешно')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Ошибка при применении миграций: {str(e)}')
                )
                return

        # 2. Создаем суперпользователя если его нет
        if not options.get('skip_superuser'):
            self.stdout.write('')
            self.stdout.write('👤 Проверка суперпользователя...')
            
            if not User.objects.filter(is_superuser=True).exists():
                self.stdout.write('Суперпользователь не найден. Создаем...')
                try:
                    call_command('create_superuser')
                except KeyboardInterrupt:
                    self.stdout.write(
                        self.style.WARNING('\n⚠️ Создание суперпользователя отменено')
                    )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ Суперпользователь уже существует')
                )

        # 3. Инициализируем системные настройки
        if not options.get('skip_settings'):
            self.stdout.write('')
            self.stdout.write('⚙️ Инициализация системных настроек...')
            try:
                settings, created = SystemSettings.objects.get_or_create(
                    defaults={
                        'clinic_name': 'Реабилитационный центр',
                        'timezone': 'Europe/Moscow',
                        'language': 'ru',
                        'date_format': '%d.%m.%Y',
                        'maintenance_mode': False
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Системные настройки созданы')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Системные настройки уже существуют')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Ошибка при создании настроек: {str(e)}')
                )

        # 4. Собираем статические файлы
        self.stdout.write('')
        self.stdout.write('📁 Сбор статических файлов...')
        try:
            call_command('collectstatic', '--noinput', verbosity=0)
            self.stdout.write(
                self.style.SUCCESS('✅ Статические файлы собраны')
            )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Предупреждение при сборе статических файлов: {str(e)}')
            )

        # 5. Проверяем состояние системы
        self.stdout.write('')
        self.stdout.write('🔍 Проверка состояния системы...')
        
        # Проверяем подключение к БД
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write('  ✅ База данных: подключение установлено')
        except Exception as e:
            self.stdout.write(f'  ❌ База данных: ошибка подключения - {str(e)}')

        # Проверяем количество пользователей
        user_count = User.objects.count()
        self.stdout.write(f'  📊 Пользователей в системе: {user_count}')

        # Проверяем настройки безопасности
        from django.conf import settings as django_settings
        security_issues = []
        
        if django_settings.DEBUG:
            security_issues.append('DEBUG=True')
        
        if django_settings.SECRET_KEY.startswith('django-insecure-'):
            security_issues.append('Небезопасный SECRET_KEY')
        
        if security_issues:
            self.stdout.write(f'  ⚠️ Проблемы безопасности: {", ".join(security_issues)}')
        else:
            self.stdout.write('  ✅ Настройки безопасности: в порядке')

        # Финальное сообщение
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS('🎉 Инициализация системы завершена!')
        )
        self.stdout.write('')
        self.stdout.write('Следующие шаги:')
        self.stdout.write('  1. Запустите сервер: python manage.py runserver')
        self.stdout.write('  2. Откройте браузер: http://127.0.0.1:8000')
        self.stdout.write('  3. Войдите с учетными данными суперпользователя')
        self.stdout.write('  4. Проверьте дашборд безопасности: /security/')
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS('Добро пожаловать в систему управления реабилитационным центром!')
        )
