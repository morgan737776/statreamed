import os
import sys
import django

# Устанавливаем переменные окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rehab_center.settings')

try:
    django.setup()
    from django.apps import apps
    
    # Проверяем все модели
    for model in apps.get_models():
        print(f"Model: {model.__name__} in {model.__module__}")
    
    print("\nAll models loaded successfully!")
    
except Exception as e:
    print(f"Error: {str(e)}", file=sys.stderr)
    raise
