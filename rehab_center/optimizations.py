from django.conf import settings
from django.core.cache import cache
from django.db import connections
from django.db.models import F, Index
import logging
import time
import os
from pathlib import Path

logger = logging.getLogger('optimization')

# Импортируем наши модули оптимизации
try:
    from core.models_indexes import OptimizationMixins
    from core.query_optimization import optimize_queryset
    from core.cache_optimization import cache_invalidate_on_change
except ImportError:
    logger.warning('Не удалось импортировать модули оптимизации')
    OptimizationMixins = None
    optimize_queryset = None
    cache_invalidate_on_change = None

# Оптимизация запросов
def optimize_database():
    # Начало отсчета времени
    start_time = time.time()
    
    # Оптимизация индексов
    with connections['default'].cursor() as cursor:
        try:
            # Оптимизация таблиц SQLite
            cursor.execute("PRAGMA optimize")
            cursor.execute("PRAGMA vacuum")
            cursor.execute("PRAGMA analysis_limit=1000")
            cursor.execute("PRAGMA analyze")
            
            # Оптимизируем работу журнала
            cursor.execute("PRAGMA journal_mode=WAL")
            
            # Оптимизируем кэширование и производительность
            cursor.execute("PRAGMA cache_size=10000")
            cursor.execute("PRAGMA synchronous=NORMAL") # Безопасный баланс между скоростью и надежностью
            cursor.execute("PRAGMA temp_store=MEMORY") # Храним временные таблицы в памяти
            cursor.execute("PRAGMA mmap_size=30000000000") # 30GB для memory-mapped I/O
            
            # Включаем foreign key constraints если они выключены
            cursor.execute("PRAGMA foreign_keys=ON")
        except Exception as e:
            logger.error(f"Ошибка оптимизации базы данных: {str(e)}")
    
    # Применяем автоматическую индексацию к моделям если доступно
    if OptimizationMixins:
        try:
            from django.apps import apps
            for model in apps.get_models():
                # Не применяем к моделям из сторонних приложений
                if model._meta.app_label in ['core', 'medical_history', 'inpatient', 'services']:
                    OptimizationMixins.add_indexes(model)
        except Exception as e:
            logger.error(f"Ошибка при добавлении индексов: {str(e)}")
    
    # Логируем время выполнения
    execution_time = time.time() - start_time
    logger.info(f"Оптимизация базы данных выполнена за {execution_time:.2f} секунд")

def optimize_static_files():
    if settings.DEBUG:
        # В режиме разработки используем стандартные настройки
        return
    
    # Оптимизация статических файлов
    from django.contrib.staticfiles.storage import staticfiles_storage
    from django.conf import settings
    import hashlib
    
    try:
        # Создаем директорию для статических файлов, если её нет
        os.makedirs(settings.STATIC_ROOT, exist_ok=True)
        
        # Очистка старых файлов кэша, но не всех статических файлов
        # Это безопаснее, чем удалять все файлы
        static_root = Path(settings.STATIC_ROOT)
        cache_pattern = "*.cache"
        expired_files = 0
        
        # Очищаем только кэш-файлы старше 7 дней
        import time
        week_ago = time.time() - (7 * 24 * 60 * 60)  # 7 дней в секундах
        
        for cache_file in static_root.glob(cache_pattern):
            if cache_file.stat().st_mtime < week_ago:
                cache_file.unlink()
                expired_files += 1
        
        logger.info(f"Удалено {expired_files} устаревших файлов кэша")
        
        # Проверяем целостность важных статических файлов
        important_static_files = ['css/main.css', 'js/app.js']
        for file_path in important_static_files:
            full_path = static_root / file_path
            if not full_path.exists():
                logger.warning(f"Важный статический файл отсутствует: {file_path}")
    except Exception as e:
        logger.error(f"Ошибка при оптимизации статических файлов: {str(e)}")

def setup_caching():
    """Настройка кэширования системы"""
    try:
        # Не очищаем весь кэш, это может ухудшить производительность
        # Очищаем только системные ключи (если поддерживается)
        try:
            if hasattr(cache, 'keys'):
                system_keys = cache.keys('system_*')
                if system_keys:
                    cache.delete_many(system_keys)
        except Exception:
            # Если keys() не поддерживается, просто пропускаем
            pass
        
        # Устанавливаем маркер, что оптимизация выполнена
        cache.set('system_database_optimized', True, timeout=24*3600)  # 24 часа
        cache.set('system_optimization_timestamp', time.time(), timeout=24*3600)
        
        # Подготавливаем кэш для часто используемых данных
        try:
            # Предварительная загрузка в кэш некоторых данных
            from django.contrib.auth.models import User
            from core.models import Patient, Staff
            
            # Кэшируем количество пользователей и пациентов
            cache.set('stats_total_users', User.objects.count(), 3600*6)  # 6 часов
            cache.set('stats_total_patients', Patient.objects.count(), 3600*6)
            cache.set('stats_total_staff', Staff.objects.count(), 3600*6)
        except Exception as e:
            logger.warning(f"Не удалось предварительно заполнить кэш: {str(e)}")
            
        logger.info("Настройка кэширования выполнена успешно")
    except Exception as e:
        logger.error(f"Ошибка при настройке кэширования: {str(e)}")

def optimize_queries():
    """Применение оптимизаций запросов моделей"""
    try:
        # Настраиваем автоматическую оптимизацию запросов
        if cache_invalidate_on_change:
            from django.apps import apps
            # Применяем cache_invalidate_on_change к основным моделям
            key_models = []
            for model_name in ['Patient', 'Appointment', 'MedicalRecord']:
                for app_label in ['core', 'medical_history']:
                    try:
                        model = apps.get_model(app_label, model_name)
                        key_models.append(model)
                    except LookupError:
                        pass
            
            # Применяем декоратор к ключевым моделям
            for model in key_models:
                cache_invalidate_on_change(model)
                logger.info(f"Применена автоматическая инвалидация кэша к модели {model.__name__}")
                
        logger.info("Оптимизация запросов выполнена успешно")
    except Exception as e:
        logger.error(f"Ошибка при оптимизации запросов: {str(e)}")

def run_optimizations():
    """Запуск всех оптимизаций системы"""
    logger.info("Начало процесса оптимизации системы")
    
    # Выполняем оптимизации
    optimize_database()
    optimize_static_files()
    setup_caching()
    optimize_queries()
    
    logger.info("Процесс оптимизации системы завершен успешно")
    return True
