# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Index

class OptimizationMixins:
    """
    Миксины для оптимизации моделей
    """
    @classmethod
    def add_indexes(cls, model_class):
        """
        Добавляет оптимальные индексы к указанной модели
        """
        meta = model_class._meta
        
        # Добавляем индексы для всех полей ForeignKey и DateTimeField
        for field in meta.fields:
            if isinstance(field, models.ForeignKey):
                # Для полей ForeignKey добавляем индекс для более быстрых JOIN-запросов
                field_name = field.name
                index_name = f'{meta.model_name}_{field_name}_idx'
                
                # Проверяем, существует ли уже индекс
                if not any(index.name == index_name for index in meta.indexes):
                    meta.indexes.append(Index(fields=[field_name], name=index_name))
            
            elif isinstance(field, models.DateTimeField) or isinstance(field, models.DateField):
                # Для дат добавляем индексы для ускорения сортировки и выборки по диапазону
                field_name = field.name
                index_name = f'{meta.model_name}_{field_name}_idx'
                
                # Проверяем, существует ли уже индекс
                if not any(index.name == index_name for index in meta.indexes):
                    meta.indexes.append(Index(fields=[field_name], name=index_name))
        
        return model_class
