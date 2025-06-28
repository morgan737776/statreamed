"""
Команда для создания суперпользователя с интерактивным вводом
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.management import call_command
import getpass


class Command(BaseCommand):
    help = 'Создает суперпользователя с интерактивным вводом'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Имя пользователя для суперпользователя',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email суперпользователя',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Пароль суперпользователя',
        )
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Не запрашивать интерактивный ввод',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔧 Создание суперпользователя...')
        )

        username = options.get('username')
        email = options.get('email')
        password = options.get('password')
        no_input = options.get('no_input', False)

        if not no_input:
            # Интерактивный ввод
            if not username:
                username = input('Введите имя пользователя: ')
            
            if not email:
                email = input('Введите email: ')
            
            if not password:
                password = getpass.getpass('Введите пароль: ')
                password_confirm = getpass.getpass('Подтвердите пароль: ')
                
                if password != password_confirm:
                    self.stdout.write(
                        self.style.ERROR('❌ Пароли не совпадают!')
                    )
                    return

        # Проверяем обязательные поля
        if not all([username, email, password]):
            self.stdout.write(
                self.style.ERROR('❌ Все поля обязательны для заполнения!')
            )
            return

        # Проверяем существование пользователя
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'❌ Пользователь с именем "{username}" уже существует!')
            )
            return

        try:
            # Создаем суперпользователя
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )

            self.stdout.write(
                self.style.SUCCESS(f'✅ Суперпользователь "{username}" успешно создан!')
            )

            # Выводим информацию о пользователе
            self.stdout.write('')
            self.stdout.write('📋 Информация о пользователе:')
            self.stdout.write(f'   Имя пользователя: {user.username}')
            self.stdout.write(f'   Email: {user.email}')
            self.stdout.write(f'   Суперпользователь: {user.is_superuser}')
            self.stdout.write(f'   Персонал: {user.is_staff}')
            self.stdout.write(f'   Активен: {user.is_active}')
            self.stdout.write('')

            self.stdout.write(
                self.style.SUCCESS('🎉 Теперь вы можете войти в систему!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка при создании суперпользователя: {str(e)}')
            )
