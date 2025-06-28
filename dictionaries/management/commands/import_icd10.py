import csv
from django.core.management.base import BaseCommand
from dictionaries.models import ICD10

class Command(BaseCommand):
    help = 'Импорт МКБ-10 из CSV-файла. Формат: code;name;parent_code (parent_code опционально)'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Путь к CSV-файлу с МКБ-10')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                parent = None
                if row.get('parent_code'):
                    parent = ICD10.objects.filter(code=row['parent_code']).first()
                obj, created = ICD10.objects.update_or_create(
                    code=row['code'],
                    defaults={
                        'name': row['name'],
                        'parent': parent,
                        'is_active': True,
                    }
                )
                self.stdout.write(self.style.SUCCESS(f"{'Создан' if created else 'Обновлен'}: {obj.code} - {obj.name}"))
