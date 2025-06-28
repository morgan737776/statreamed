import csv
from django.core.management.base import BaseCommand
from dictionaries.models import ServiceNomenclature

class Command(BaseCommand):
    help = 'Импорт номенклатуры медицинских услуг из CSV-файла. Формат: code;name'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Путь к CSV-файлу с услугами')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                obj, created = ServiceNomenclature.objects.update_or_create(
                    code=row['code'],
                    defaults={
                        'name': row['name'],
                        'is_active': True,
                    }
                )
                self.stdout.write(self.style.SUCCESS(f"{'Создан' if created else 'Обновлен'}: {obj.code} - {obj.name}"))
