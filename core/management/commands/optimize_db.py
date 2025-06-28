from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Optimize database tables and add indexes for better performance'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            self.stdout.write('Optimizing database tables...')
            
            # Получаем список всех таблиц
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            # Оптимизируем каждую таблицу
            for table in tables:
                try:
                    cursor.execute(f"ANALYZE TABLE `{table}`")
                    cursor.execute(f"OPTIMIZE TABLE `{table}`")
                    self.stdout.write(self.style.SUCCESS(f'Optimized table: {table}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error optimizing {table}: {str(e)}'))
            
            # Добавляем индексы для часто используемых полей
            try:
                self.add_indexes(cursor)
                self.stdout.write(self.style.SUCCESS('Added indexes'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error adding indexes: {str(e)}'))
            
            self.stdout.write(self.style.SUCCESS('Database optimization complete!'))
    
    def add_indexes(self, cursor):
        # Добавляем индексы для часто используемых полей
        indexes = [
            ("core_patient", ["last_name", "first_name"]),
            ("core_appointment", ["start_datetime", "end_datetime"]),
            ("core_appointment", ["status"]),
            ("core_patientdocument", ["patient_id"]),
        ]
        
        for table, columns in indexes:
            index_name = f'idx_{table}_{"_".join(columns)}'
            try:
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS {index_name} 
                    ON `{table}` ({','.join(f'`{col}`' for col in columns)})
                """)
            except Exception as e:
                if 'Duplicate key name' not in str(e):
                    raise e
