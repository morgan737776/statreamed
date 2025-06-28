from django.db import models
from django.contrib.auth import get_user_model

class IntegrationLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Пользователь')
    operation = models.CharField(max_length=64, blank=True, verbose_name='Операция')
    request_data = models.TextField(blank=True)
    response_data = models.TextField(blank=True)
    status = models.CharField(max_length=32, blank=True)
    error = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Журнал интеграции ЕГИСЗ'
        verbose_name_plural = 'Журнал интеграции ЕГИСЗ'
        ordering = ['-timestamp']
