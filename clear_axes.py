from axes.models import AccessLog
AccessLog.objects.all().delete()

# Проверяем, что таблица пуста
print(f"Очищено записей: {AccessLog.objects.count()}")

# Создаём миграцию для axes
from django.core.management import call_command
call_command('makemigrations', 'axes')
