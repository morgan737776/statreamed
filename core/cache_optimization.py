# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import functools
import hashlib
import json

def get_cache_key(prefix, args=None, kwargs=None):
    """
    Создает уникальный ключ кэша на основе префикса и параметров.
    """
    key_parts = [prefix]
    
    if args:
        key_parts.append(str(args))
    
    if kwargs:
        # Сортировка ключей для обеспечения последовательного хэша
        key_parts.append(json.dumps(kwargs, sort_keys=True))
    
    key = "_".join(key_parts)
    # Хэшируем длинные ключи для компактности
    if len(key) > 200:
        hashed = hashlib.md5(key.encode()).hexdigest()
        key = f"{prefix}_{hashed}"
    
    return key

def cached_function(timeout=3600, prefix=None):
    """
    Декоратор для кэширования результатов функций.
    
    Args:
        timeout: Время кэширования в секундах
        prefix: Префикс ключа кэша (по умолчанию используется имя функции)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Получаем или создаем префикс ключа
            cache_prefix = prefix if prefix else f"{func.__module__}.{func.__name__}"
            
            # Создаем ключ кэша
            cache_key = get_cache_key(cache_prefix, args, kwargs)
            
            # Проверяем, есть ли результат в кэше
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Вычисляем результат
            result = func(*args, **kwargs)
            
            # Кэшируем результат
            cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator

def model_cache_key(model_name, object_id):
    """
    Создает ключ кэша для объекта модели.
    """
    return f"model_{model_name}_{object_id}"

def model_list_cache_key(model_name, filters=None):
    """
    Создает ключ кэша для списка объектов модели с фильтрами.
    """
    if filters:
        filters_str = json.dumps(filters, sort_keys=True)
        return f"model_list_{model_name}_{hashlib.md5(filters_str.encode()).hexdigest()}"
    return f"model_list_{model_name}"

def invalidate_model_cache(sender, instance, **kwargs):
    """
    Инвалидирует кэш для модели при изменении или удалении объекта.
    """
    model_name = sender.__name__.lower()
    
    # Инвалидируем кэш объекта
    cache.delete(model_cache_key(model_name, instance.id))
    
    # Инвалидируем кэши списков объектов этой модели
    cache_keys = cache.keys(f"model_list_{model_name}_*")
    if cache_keys:
        cache.delete_many(cache_keys)

# Этот декоратор можно применить к любой модели для автоматической инвалидации кэша
def cache_invalidate_on_change(model):
    """
    Декоратор для автоматической инвалидации кэша при изменении модели.
    """
    post_save.connect(invalidate_model_cache, sender=model)
    post_delete.connect(invalidate_model_cache, sender=model)
    return model
    
# Примеры использования кэширования для Django views
def cached_view(timeout=3600, key_prefix=None):
    """
    Декоратор для кэширования результатов view-функций Django.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Не кэшируем для авторизованных пользователей и POST-запросов
            if request.user.is_authenticated or request.method != 'GET':
                return view_func(request, *args, **kwargs)
                
            # Формируем ключ кэша
            prefix = key_prefix if key_prefix else f"{view_func.__module__}.{view_func.__name__}"
            key_params = {
                'path': request.path,
                'query': request.GET.urlencode()
            }
            cache_key = get_cache_key(prefix, kwargs=key_params)
            
            # Проверяем кэш
            response = cache.get(cache_key)
            if response is not None:
                return response
                
            # Выполняем функцию
            response = view_func(request, *args, **kwargs)
            
            # Кэшируем только успешные ответы
            if response.status_code == 200:
                cache.set(cache_key, response, timeout)
                
            return response
        return wrapper
    return decorator
