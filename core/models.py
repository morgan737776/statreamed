# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from PIL import Image
import os
from .models_optimization import OptimizedServiceItem



class SystemSettings(models.Model):
    """Singleton-модель для хранения системных настроек центра."""
    singleton_id = models.PositiveSmallIntegerField(default=1, unique=True, editable=False)
    clinic_name = models.CharField(max_length=255, default="Реабилитационный центр", verbose_name=_('Название клиники'))
    timezone = models.CharField(max_length=64, default="Europe/Moscow", verbose_name=_('Часовой пояс'))
    date_format = models.CharField(max_length=32, default="DD.MM.YYYY", verbose_name=_('Формат даты'))
    language = models.CharField(max_length=8, default="ru", verbose_name=_('Язык'))
    maintenance_mode = models.BooleanField(default=False, verbose_name=_('Техническое обслуживание'))
    logo = models.ImageField(upload_to='branding/', blank=True, null=True, verbose_name=_('Логотип'))
    color_theme = models.CharField(max_length=32, default="default", verbose_name=_('Цветовая схема'))
    
    def save(self, *args, **kwargs):
        self.singleton_id = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(singleton_id=1)
        return obj
    
    class Meta:
        verbose_name = _('Системные настройки')
        verbose_name_plural = _('Системные настройки')


class IntegrationSettings(models.Model):
    """Модель для хранения ключей и параметров интеграций."""
    service_1c_url = models.URLField(blank=True, verbose_name=_('1С: URL сервиса'))
    service_1c_key = models.CharField(max_length=128, blank=True, verbose_name=_('1С: API-ключ'))
    sms_provider = models.CharField(max_length=64, blank=True, verbose_name=_('SMS-провайдер'))
    sms_api_key = models.CharField(max_length=128, blank=True, verbose_name=_('SMS API-ключ'))
    email_host = models.CharField(max_length=128, blank=True, verbose_name=_('SMTP сервер'))
    email_user = models.CharField(max_length=128, blank=True, verbose_name=_('SMTP пользователь'))
    email_password = models.CharField(max_length=128, blank=True, verbose_name=_('SMTP пароль'))
    webhook_url = models.URLField(blank=True, verbose_name=_('Webhook URL'))
    
    class Meta:
        verbose_name = _('Интеграции и API')
        verbose_name_plural = _('Интеграции и API')







class AuditLog(models.Model):
    """Модель для аудита изменений настроек и действий админов."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_('Пользователь'))
    action = models.CharField(max_length=255, verbose_name=_('Действие'))
    model = models.CharField(max_length=100, blank=True, verbose_name=_('Модель'))
    object_id = models.CharField(max_length=64, blank=True, verbose_name=_('ID объекта'))
    old_value = models.TextField(blank=True, verbose_name=_('Старое значение'))
    new_value = models.TextField(blank=True, verbose_name=_('Новое значение'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Время'))
    
    class Meta:
        verbose_name = _('Журнал аудита')
        verbose_name_plural = _('Журнал аудита')
        ordering = ['-timestamp']


class PatientDocument(models.Model):
    """Модель для хранения документов пациента."""
    DOCUMENT_TYPES = [
        ('passport', _('Паспорт')),
        ('insurance', _('Страховой полис')),
        ('medical', _('Медицинские документы')),
        ('other', _('Прочие документы'))
    ]
    
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, verbose_name=_('Пациент'))
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, verbose_name=_('Тип документа'))
    file = models.FileField(upload_to='patient_documents/', verbose_name=_('Файл'))
    description = models.TextField(blank=True, verbose_name=_('Описание'))
    upload_date = models.DateField(default=timezone.now, verbose_name=_('Дата загрузки'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    
    class Meta:
        verbose_name = _('Документ пациента')
        verbose_name_plural = _('Документы пациентов')
        ordering = ['-upload_date']


class Staff(models.Model):
    STATUS_CHOICES = [
        ('active', _('Активен')),
        ('inactive', _('Неактивен')),
    ]
    first_name = models.CharField(max_length=100, verbose_name=_('Имя'))
    last_name = models.CharField(max_length=100, verbose_name=_('Фамилия'))
    middle_name = models.CharField(max_length=100, blank=True, verbose_name=_('Отчество'))
    position = models.CharField(max_length=100, verbose_name=_('Должность'))
    department = models.CharField(max_length=100, blank=True, verbose_name=_('Отдел'))
    email = models.EmailField(blank=True, verbose_name=_('Email'))
    phone = models.CharField(max_length=30, blank=True, verbose_name=_('Телефон'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name=_('Статус'))
    hire_date = models.DateField(verbose_name=_('Дата приёма'))
    fire_date = models.DateField(null=True, blank=True, verbose_name=_('Дата увольнения'))
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_('Пользователь'))

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()

    class Meta:
        verbose_name = _('Сотрудник')
        verbose_name_plural = _('Сотрудники')
        ordering = ['last_name', 'first_name']


class Patient(models.Model):
    """Модель пациента реабилитационного центра."""
    GENDER_CHOICES = [
        ('M', _('Мужской')),
        ('F', _('Женский')),
    ]
    STATUS_CHOICES = [
        ('active', _('Активен')),
        ('discharged', _('Выписан')),
        ('transferred', _('Переведен')),
        ('deceased', _('Умер')),
    ]
    
    first_name = models.CharField(max_length=100, verbose_name=_("Имя"))
    last_name = models.CharField(max_length=100, verbose_name=_("Фамилия"))
    middle_name = models.CharField(max_length=100, blank=True, verbose_name=_("Отчество"))
    date_of_birth = models.DateField(verbose_name=_("Дата рождения"))
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name=_("Пол"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Телефон"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    address = models.TextField(blank=True, verbose_name=_("Адрес"))
    passport_series = models.CharField(max_length=10, blank=True, verbose_name=_("Серия паспорта"))
    passport_number = models.CharField(max_length=20, blank=True, verbose_name=_("Номер паспорта"))
    insurance_policy = models.CharField(max_length=50, blank=True, verbose_name=_("Страховой полис"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name=_("Статус"))
    
    # Новые поля для расширенного функционала
    photo = models.ImageField(upload_to='patients/photos/', blank=True, null=True, verbose_name=_("Фото"))
    emergency_contact_name = models.CharField(max_length=200, blank=True, verbose_name=_("Контактное лицо"))
    emergency_contact_phone = models.CharField(max_length=20, blank=True, verbose_name=_("Телефон контактного лица"))
    allergies = models.TextField(blank=True, verbose_name=_("Аллергии"))
    chronic_diseases = models.TextField(blank=True, verbose_name=_("Хронические заболевания"))
    blood_type = models.CharField(max_length=5, blank=True, verbose_name=_("Группа крови"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания записи"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления записи"))

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()

    # Возвращает полное имя пациента.
    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Обработка фото - изменение размера
        if self.photo:
            img = Image.open(self.photo.path)
            if img.height > 300 or img.width > 300:
                img.thumbnail((300, 300))
                img.save(self.photo.path)

    class Meta:
        verbose_name = _("Пациент")
        verbose_name_plural = _("Пациенты")
        ordering = ['last_name', 'first_name']


class Appointment(models.Model):
    """Модель приема"""
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, verbose_name=_('Пациент'))
    service = models.ForeignKey('services.ServiceItem', on_delete=models.CASCADE, verbose_name=_('Услуга'))
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Врач'))
    start_datetime = models.DateTimeField(verbose_name=_('Начало'))
    end_datetime = models.DateTimeField(verbose_name=_('Конец'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Цена'))
    status = models.CharField(
        max_length=20,
        choices=[
            ('scheduled', _('Запланировано')),
            ('completed', _('Выполнено')),
            ('cancelled', _('Отменено'))
        ],
        default='scheduled',
        verbose_name=_('Статус')
    )
    notes = models.TextField(blank=True, verbose_name=_('Примечания'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активен'))
    
    class Meta:
        verbose_name = _('Прием')
        verbose_name_plural = _('Приемы')
        ordering = ['-start_datetime']
    
    def __str__(self):
        return f"{self.patient} - {self.service} - {self.start_datetime}"
    
    @property
    def duration_minutes(self):
        """Возвращает продолжительность приема в минутах."""
        if self.end_datetime and self.start_datetime:
            delta = self.end_datetime - self.start_datetime
            return int(delta.total_seconds() / 60)
        return 0
        
    def save(self, *args, **kwargs):
        # Автоматически устанавливаем время окончания, если не указано
        if not self.end_datetime and hasattr(self.service, 'duration'):
            from datetime import timedelta
            self.end_datetime = self.start_datetime + timedelta(minutes=self.service.duration)
        super().save(*args, **kwargs)


class Notification(models.Model):
    """Модель уведомлений."""
    TYPE_CHOICES = [
        ('appointment_reminder', _('Напоминание о приеме')),
        ('treatment_reminder', _('Напоминание о лечении')),
        ('medication_reminder', _('Напоминание о лекарстве')),
        ('system', _('Системное уведомление')),
        ('custom', _('Пользовательское')),
    ]
    
    DELIVERY_METHOD_CHOICES = [
        ('email', _('Email')),
        ('sms', _('SMS')),
        ('push', _('Push-уведомление')),
        ('system', _('В системе')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Ожидает отправки')),
        ('sent', _('Отправлено')),
        ('delivered', _('Доставлено')),
        ('failed', _('Ошибка отправки')),
        ('read', _('Прочитано')),
    ]
    
    recipient_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Получатель"))
    recipient_patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Пациент-получатель"))
    
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, verbose_name=_("Тип уведомления"))
    title = models.CharField(max_length=200, verbose_name=_("Заголовок"))
    message = models.TextField(verbose_name=_("Сообщение"))
    
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHOD_CHOICES, default='system', verbose_name=_("Способ доставки"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Статус"))
    
    # Планирование отправки
    scheduled_for = models.DateTimeField(null=True, blank=True, verbose_name=_("Запланировано на"))
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Отправлено в"))
    read_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Прочитано в"))
    
    # Связанные объекты
    related_appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Связанная запись"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_notifications')
    
    class Meta:
        verbose_name = _("Уведомление")
        verbose_name_plural = _("Уведомления")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_notification_type_display()}"
    
    def mark_as_read(self):
        """Отметить уведомление как прочитанное."""
        if not self.read_at:
            self.read_at = timezone.now()
            self.status = 'read'
            self.save()


class ExternalCalendarSync(models.Model):
    """Модель для синхронизации с внешними календарями."""
    PROVIDER_CHOICES = [
        ('google', _('Google Calendar')),
        ('outlook', _('Outlook')),
        ('ical', _('iCal')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Пользователь"))
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, verbose_name=_("Провайдер"))
    
    # Данные для аутентификации
    access_token = models.TextField(blank=True, verbose_name=_("Access Token"))
    refresh_token = models.TextField(blank=True, verbose_name=_("Refresh Token"))
    calendar_id = models.CharField(max_length=200, blank=True, verbose_name=_("ID календаря"))
    
    is_active = models.BooleanField(default=True, verbose_name=_("Активна"))
    last_sync = models.DateTimeField(null=True, blank=True, verbose_name=_("Последняя синхронизация"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Синхронизация календаря")
        verbose_name_plural = _("Синхронизации календарей")
    
    def __str__(self):
        return f"{self.user} - {self.get_provider_display()}"


class MedicalRecord(models.Model):
    """Модель для хранения медицинских записей о пациенте."""
    RECORD_TYPES = [
        ('examination', _('Осмотр')),
        ('diagnosis', _('Диагноз')),
        ('treatment', _('Лечение')),
        ('procedure', _('Процедура')),
        ('prescription', _('Назначение')),
        ('note', _('Заметка')),
        ('other', _('Другое')),
    ]
    
    PRIORITY_CHOICES = [
        ('low', _('Низкий')),
        ('medium', _('Средний')),
        ('high', _('Высокий')),
    ]
    
    patient = models.ForeignKey(
        Patient, 
        on_delete=models.CASCADE, 
        related_name='medical_records',
        verbose_name=_("Пациент")
    )
    record_type = models.CharField(
        max_length=20,
        choices=RECORD_TYPES,
        default='note',
        verbose_name=_("Тип записи")
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Заголовок")
    )
    content = models.TextField(
        verbose_name=_("Содержание")
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_medical_records',
        verbose_name=_("Автор записи")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )
    is_important = models.BooleanField(
        default=False,
        verbose_name=_("Важная запись")
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name=_("Приоритет")
    )
    
    class Meta:
        verbose_name = _("Медицинская запись")
        verbose_name_plural = _("Медицинские записи")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_record_type_display()}: {self.title} - {self.patient}"
    
    def get_short_content(self, max_length=100):
        """Возвращает укороченное содержимое записи."""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + '...'


class TreatmentReminder(models.Model):
    """Модель напоминаний о лечении."""
    FREQUENCY_CHOICES = [
        ('daily', _('Ежедневно')),
        ('weekly', _('Еженедельно')),
        ('monthly', _('Ежемесячно')),
        ('custom', _('Пользовательский')),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name=_("Пациент"))
    title = models.CharField(max_length=200, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    
    start_date = models.DateField(verbose_name=_("Дата начала"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("Дата окончания"))
    
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='daily', verbose_name=_("Частота"))
    time_of_day = models.TimeField(verbose_name=_("Время"))
    
    is_active = models.BooleanField(default=True, verbose_name=_("Активно"))
    
    # Связь с медицинскими записями
    related_record = models.ForeignKey('MedicalRecord', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = _("Напоминание о лечении")
        verbose_name_plural = _("Напоминания о лечении")
        ordering = ['start_date', 'time_of_day']
    
    def __str__(self):
        return f"{self.title} - {self.patient} ({self.get_frequency_display()})"
