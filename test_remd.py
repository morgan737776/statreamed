import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rehab_center.settings')
django.setup()

from emr.models import MedicalRecordEntry
from integrations.services_remd import RemdService

# Получаем первую запись для теста. Убедитесь, что у вас есть хотя бы одна запись в базе.
try:
    entry = MedicalRecordEntry.objects.first()
    if not entry:
        print("В базе данных нет записей MedicalRecordEntry. Пожалуйста, создайте одну для теста.")
    else:
        print(f"Тестируем отправку для записи с ID: {entry.id}")
        
        # Создаем экземпляр сервиса
        remd_service = RemdService()
        
        # Вызываем метод отправки
        result = remd_service.send_document(entry.id)
        
        # Выводим результат
        print("\n--- Результат вызова send_document ---")
        print(result)
        print("------------------------------------\n")

        # Дополнительно проверим статус записи в БД
        entry.refresh_from_db()
        print(f"Статус записи в БД (remd_status): {entry.remd_status}")
        print(f"ID документа в РЭМД (remd_document_id): {entry.remd_document_id}")

except Exception as e:
    print(f"Произошла ошибка: {e}")
