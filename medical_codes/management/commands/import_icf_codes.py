import csv
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from medical_codes.models import ICFCode

class Command(BaseCommand):
    help = 'Импортирует иерархический справочник кодов МКФ из локального CSV файла.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Начинаю импорт кодов МКФ из локального файла...")

        # Путь к файлу внутри приложения medical_codes
        file_path = os.path.join(settings.BASE_DIR, 'medical_codes', 'data', 'icf_codes.csv')

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"Файл не найден: {file_path}"))
            return

        # Очищаем старые данные перед импортом
        ICFCode.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Старые коды МКФ удалены."))

        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            reader = csv.DictReader(csv_file)
            all_rows = list(reader)

            # --- Первый проход: Создаем все объекты без связей ---
            objects_to_create = []
            for row in all_rows:
                objects_to_create.append(
                    ICFCode(
                        code=row['code'],
                        name=row['name'],
                        is_category=bool(int(row.get('is_category', 0) or 0))
                    )
                )
            
            ICFCode.objects.bulk_create(objects_to_create)
            self.stdout.write(self.style.SUCCESS(f"Этап 1: Успешно создано {len(objects_to_create)} объектов МКФ."))

            # --- Второй проход: Устанавливаем родительские связи ---
            all_codes_map = {c.code: c for c in ICFCode.objects.all()}
            objects_to_update = []

            for row in all_rows:
                parent_code = row.get('parent_code')
                if parent_code and parent_code in all_codes_map:
                    child_obj = all_codes_map.get(row['code'])
                    parent_obj = all_codes_map.get(parent_code)
                    if child_obj and parent_obj:
                        child_obj.parent = parent_obj
                        objects_to_update.append(child_obj)

            # Обновляем только поле 'parent' для всех измененных объектов
            ICFCode.objects.bulk_update(objects_to_update, ['parent'])
            self.stdout.write(self.style.SUCCESS(f"Этап 2: Успешно обновлено {len(objects_to_update)} родительских связей."))

        self.stdout.write(self.style.SUCCESS(f"Импорт кодов МКФ успешно завершен."))
