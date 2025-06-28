# -*- coding: utf-8 -*-
from django.db.models import Prefetch
from django.core.paginator import Paginator

def optimize_queryset(queryset, related_fields=None, count_related=None):
    """
    Оптимизирует запрос, добавляя select_related и prefetch_related для указанных полей.
    
    Args:
        queryset: Исходный QuerySet
        related_fields: Список полей для select_related (ForeignKey)
        count_related: Словарь {'field': 'count_attr'}, где field - поле для аннотации,
                      а count_attr - имя атрибута для хранения количества связанных объектов
    
    Returns:
        Оптимизированный QuerySet
    """
    if related_fields:
        for field in related_fields:
            if isinstance(field, tuple):
                # Если передан кортеж (поле, поля_для_выборки), используем Prefetch
                prefetch_field, prefetch_queryset = field
                queryset = queryset.prefetch_related(
                    Prefetch(prefetch_field, queryset=prefetch_queryset)
                )
            else:
                # Иначе используем обычный select_related
                if '__' in field:
                    queryset = queryset.prefetch_related(field)
                else:
                    queryset = queryset.select_related(field)
    
    if count_related:
        # Добавляем аннотации для подсчета связанных объектов
        from django.db.models import Count
        for field, attr_name in count_related.items():
            queryset = queryset.annotate(**{attr_name: Count(field)})
    
    return queryset

class CachedCountPaginator(Paginator):
    """
    Оптимизированный класс пагинатора, который кэширует общее количество записей.
    Это особенно полезно для больших наборов данных.
    """
    def validate_number(self, number):
        """Проверяет, что переданная страница находится в диапазоне."""
        try:
            number = int(number)
        except (TypeError, ValueError):
            return 1
        
        if number < 1:
            return 1
        if number > self.num_pages:
            if number == 1 and self.allow_empty_first_page:
                return 1
            return self.num_pages
        return number

    @property
    def count(self):
        """Возвращает общее количество записей, используя кэширование."""
        if not hasattr(self, "_count"):
            self._count = self.object_list.count()
        return self._count
