from django.db import models
from django.core.cache import cache

class OptimizedModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Очистка кэша при изменении объекта
        cache_key = f'{self.__class__.__name__}_pk_{self.pk}'
        cache.delete(cache_key)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Очистка кэша при удалении объекта
        cache_key = f'{self.__class__.__name__}_pk_{self.pk}'
        cache.delete(cache_key)
        super().delete(*args, **kwargs)

    @classmethod
    def get_cached(cls, pk):
        """Получение объекта с кэшированием"""
        cache_key = f'{cls.__name__}_pk_{pk}'
        obj = cache.get(cache_key)
        if obj is None:
            obj = cls.objects.get(pk=pk)
            cache.set(cache_key, obj, timeout=3600)  # Кэшируем на 1 час
        return obj

# Оптимизированная модель Appointment перемещена в основной models.py
# для устранения дублирования и конфликтов регистрации моделей

class OptimizedServiceItem(OptimizedModel):
    category = models.ForeignKey('services.ServiceCategory', on_delete=models.PROTECT)
    is_active = models.BooleanField()
    service_type = models.CharField(max_length=20)

    class Meta:
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['service_type']),
        ]
