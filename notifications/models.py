from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from patients.models import Patient

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('APPOINTMENT', _('Назначен прием')),
        ('REMINDER', _('Напоминание о приеме')),
        ('SYSTEM', _('Системное уведомление')),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', _('Ожидает отправки')),
        ('SENT', _('Отправлено')),
        ('DELIVERED', _('Доставлено')),
        ('FAILED', _('Ошибка доставки')),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200, verbose_name=_('Заголовок'))
    message = models.TextField(verbose_name=_('Сообщение'))
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='SYSTEM',
        verbose_name=_('Тип уведомления')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name=_('Статус')
    )
    scheduled_time = models.DateTimeField(verbose_name=_('Время отправки'))
    sent_time = models.DateTimeField(null=True, blank=True, verbose_name=_('Время отправки'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    
    class Meta:
        verbose_name = _('Уведомление')
        verbose_name_plural = _('Уведомления')
        ordering = ['-scheduled_time']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.title}"

class SMSNotification(models.Model):
    notification = models.OneToOneField(
        Notification,
        on_delete=models.CASCADE,
        related_name='sms_notification'
    )
    phone_number = models.CharField(max_length=20, verbose_name=_('Номер телефона'))
    sms_provider = models.CharField(max_length=50, verbose_name=_('Провайдер SMS'))
    provider_response = models.TextField(blank=True, verbose_name=_('Ответ провайдера'))
    
    class Meta:
        verbose_name = _('SMS уведомление')
        verbose_name_plural = _('SMS уведомления')
    
    def __str__(self):
        return f"SMS: {self.phone_number}"

class EmailNotification(models.Model):
    notification = models.OneToOneField(
        Notification,
        on_delete=models.CASCADE,
        related_name='email_notification'
    )
    email = models.EmailField(verbose_name=_('Email адрес'))
    subject = models.CharField(max_length=200, verbose_name=_('Тема письма'))
    
    class Meta:
        verbose_name = _('Email уведомление')
        verbose_name_plural = _('Email уведомления')
    
    def __str__(self):
        return f"Email: {self.email}"
