import uuid
from datetime import date

from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Import from our apps
from core.models import Patient as CorePatient
# from integrations.tasks import send_document_to_remd_task  # Временно отключено из-за ошибки OpenSSL

User = get_user_model()

# Use the CorePatient model instead of defining a new one
# All patient-related fields have been moved to the core.Patient model


class MedicalRecord(models.Model):
    """Медицинская карта пациента"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.OneToOneField(
        CorePatient,  # Changed from Patient to CorePatient
        on_delete=models.CASCADE,
        related_name='medical_record',
        verbose_name=_('Пациент')
    )
    
    # Основная информация
    record_number = models.CharField(
        _('Номер карты'),
        max_length=50,
        unique=True,
        help_text=_('Уникальный номер медицинской карты')
    )
    
    # Медицинская информация
    allergies = models.TextField(
        _('Аллергии и реакции'),
        blank=True,
        help_text=_('Укажите аллергические реакции и непереносимость лекарств')
    )
    
    chronic_diseases = models.TextField(
        _('Хронические заболевания'),
        blank=True,
        help_text=_('Наличие хронических заболеваний')
    )
    
    disability = models.CharField(
        _('Инвалидность'),
        max_length=5,  # Increased to 5 to fit 'child' value
        choices=[
            ('no', _('Нет')),
            ('I', 'I группа'),
            ('II', 'II группа'),
            ('III', 'III группа'),
            ('child', _('Ребенок-инвалид'))
        ],
        default='no',
        blank=True
    )
    
    disability_details = models.TextField(
        _('Дополнительно об инвалидности'),
        blank=True,
        help_text=_('Дополнительная информация об инвалидности')
    )
    
    # Системная информация
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('Медицинская карта')
        verbose_name_plural = _('Медицинские карты')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Мед. карта №{self.record_number} ({self.patient})"
    
    def save(self, *args, **kwargs):
        if not self.record_number:
            # Генерация номера карты: ГГММДД-XXXXXX
            from datetime import datetime
            date_part = datetime.now().strftime('%y%m%d')
            last_record = MedicalRecord.objects.order_by('-record_number').first()
            if last_record and last_record.record_number.startswith(date_part):
                try:
                    num = int(last_record.record_number[7:]) + 1
                except (ValueError, IndexError):
                    num = 1
            else:
                num = 1
            self.record_number = f"{date_part}-{num:06d}"
        super().save(*args, **kwargs)


class MedicalRecordEntry(models.Model):
    """Запись в медицинской карте (осмотр, диагноз, лечение и т.д.)"""
    ENTRY_TYPES = [
        ('examination', _('Осмотр')),
        ('diagnosis', _('Диагноз')),
        ('treatment', _('Лечение')),
        ('procedure', _('Процедура')),
        ('test_result', _('Результат анализа')),
        ('note', _('Заметка')),
        ('referral', _('Направление')),
        ('consultation', _('Консультация')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='entries',
        verbose_name=_('Медицинская карта')
    )
    
    # Основная информация о записи
    entry_type = models.CharField(
        _('Тип записи'),
        max_length=20,
        choices=ENTRY_TYPES,
        default='note'
    )

    # Поля для интеграции с РЭМД
    REMD_STATUS_CHOICES = [
        ('pending', _('Ожидает отправки')),
        ('processing', _('В обработке')),
        ('sent', _('Отправлено')),
        ('failed', _('Ошибка отправки')),
    ]
    remd_status = models.CharField(
        _('Статус в РЭМД'),
        max_length=10,
        choices=REMD_STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    remd_document_id = models.CharField(_('ID документа в РЭМД'), max_length=255, blank=True, null=True)
    
    title = models.CharField(
        _('Заголовок'),
        max_length=255,
        help_text=_('Краткое описание записи')
    )
    
    content = models.TextField(
        _('Содержание'),
        help_text=_('Подробное описание')
    )
    
    # Метаданные
    created_at = models.DateTimeField(_('Дата и время записи'), default=timezone.now)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_medical_entries',
        verbose_name=_('Автор записи')
    )
    
    # Ссылка на диагноз (если применимо)
    diagnosis = models.ManyToManyField(
        'medical_codes.ICD10Code',
        related_name='medical_entries',
        blank=True,
        verbose_name=_('Диагнозы (МКБ-10)')
    )
    
    # Дополнительные параметры
    is_confidential = models.BooleanField(
        _('Конфиденциально'),
        default=False,
        help_text=_('Доступно только уполномоченному персоналу')
    )
    
    is_important = models.BooleanField(
        _('Важная запись'),
        default=False,
        help_text=_('Выделить как важную информацию')
    )
    
    # Временные метки
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('Запись в медицинской карте')
        verbose_name_plural = _('Записи в медицинских картах')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['medical_record', 'entry_type', 'created_at']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_important']),
        ]
    
    def __str__(self):
        return f"{self.get_entry_type_display()}: {self.title} - {self.medical_record.patient.get_full_name()} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"
    
    def get_absolute_url(self):
        return reverse('emr:entry_detail', kwargs={'pk': self.pk})
    
    def can_view(self, user):
        # Врач может видеть все записи
        if user.is_staff:
            return True
        # Пациент может видеть только свои записи
        return self.medical_record.patient.user == user

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        original_remd_status = None

        if not is_new:
            try:
                original_remd_status = MedicalRecordEntry.objects.get(pk=self.pk).remd_status
            except MedicalRecordEntry.DoesNotExist:
                pass # Объект еще не в базе, ведем себя как при создании

        super().save(*args, **kwargs)

        # Отправляем в РЭМД, если это новая запись подходящего типа,
        # или если статус был 'failed' и его изменили на 'pending' для повторной отправки.
        should_send = (is_new and self.entry_type in ['examination', 'diagnosis', 'treatment'] and self.remd_status == 'pending') or \
                      (original_remd_status == 'failed' and self.remd_status == 'pending')
        
        if should_send:
            # send_document_to_remd_task.delay(self.id)
            pass


class TreatmentCategory(models.Model):
    """Категории для элементов назначений"""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Название категории"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))

    class Meta:
        verbose_name = _("Категория назначений")
        verbose_name_plural = _("Категории назначений")
        ordering = ['name']

    def __str__(self):
        return self.name


class TreatmentItem(models.Model):
    """Справочник всех возможных назначений (услуг, лекарств, процедур и т.д.)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    category = models.ForeignKey(
        TreatmentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Категория")
    )

    class Meta:
        verbose_name = _("Элемент назначений (Справочник)")
        verbose_name_plural = _("Элементы назначений (Справочник)")
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class Prescription(models.Model):
    """Назначение врача (рецепт, рекомендации, лечение)"""
    STATUS_CHOICES = [
        ('draft', _('Черновик')),
        ('active', _('Активно')),
        ('completed', _('Выполнено')),
        ('cancelled', _('Отменено')),
        ('expired', _('Просрочено')),
    ]
    
    FREQUENCY_CHOICES = [
        ('once', _('Однократно')),
        ('daily', _('Ежедневно')),
        ('bid', _('Дважды в день')),
        ('tid', _('Трижды в день')),
        ('qid', _('4 раза в день')),
        ('q4h', _('Каждые 4 часа')),
        ('q6h', _('Каждые 6 часов')),
        ('q8h', _('Каждые 8 часов')),
        ('q12h', _('Каждые 12 часов')),
        ('qod', _('Через день')),
        ('weekly', _('Еженедельно')),
        ('as_needed', _('По требованию')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        verbose_name=_('Медицинская карта')
    )
    
    # Основная информация о назначении
    treatment_item = models.ForeignKey(
        TreatmentItem,
        on_delete=models.PROTECT,  # Защита от случайного удаления из справочника
        related_name='prescriptions',
        verbose_name=_('Назначение из справочника'),
        null=True
    )
    
    description = models.TextField(
        _('Подробное описание'),
        help_text=_('Детальное описание назначения, дозировки и т.д.')
    )
    
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    # Детали назначения
    frequency = models.CharField(
        _('Периодичность'),
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='once',
        help_text=_('Как часто следует выполнять назначение')
    )
    
    start_date = models.DateTimeField(
        _('Дата начала'),
        default=timezone.now,
        help_text=_('Когда начинать выполнение назначения')
    )
    
    end_date = models.DateTimeField(
        _('Дата окончания'),
        null=True,
        blank=True,
        help_text=_('Когда заканчивается срок действия назначения')
    )
    
    is_prn = models.BooleanField(
        _('По требованию (ПРН)'),
        default=False,
        help_text=_('Принимать по мере необходимости')
    )
    
    prn_reason = models.TextField(
        _('Причина ПРН'),
        blank=True,
        help_text=_('Причина приема по требованию')
    )
    
    # Метаданные
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_prescriptions',
        verbose_name=_('Назначил')
    )
    
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('Назначение')
        verbose_name_plural = _('Назначения')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['medical_record', 'status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.treatment_item.name} - {self.medical_record.patient.get_full_name()} ({self.get_status_display()})"
    
    @property
    def is_active(self):
        """Проверяет, действительно ли назначение в данный момент"""
        now = timezone.now()
        if self.status != 'active':
            return False
        if self.start_date and self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True
    
    def can_edit(self, user):
        """Проверка прав на редактирование назначения"""
        if user.is_superuser:
            return True
        return user == self.created_by
    
    def mark_as_completed(self, user):
        """Отметить назначение как выполненное"""
        if self.status == 'active':
            self.status = 'completed'
            self.updated_by = user
            self.completed_at = timezone.now()
            self.save()
            return True
        return False
    
    def cancel(self, user, reason=''):
        """Отменить назначение"""
        if self.status in ['draft', 'active']:
            self.status = 'cancelled'
            self.updated_by = user
            self.cancellation_reason = reason
            self.save()
            return True
        return False


class TestResult(models.Model):
    """Результаты медицинских исследований и анализов"""
    TEST_TYPES = [
        ('blood', _('Анализ крови')),
        ('urine', _('Анализ мочи')),
        ('imaging', _('Визуализация')),
        ('biopsy', _('Биопсия')),
        ('microbiology', _('Микробиология')),
        ('genetic', _('Генетический анализ')),
        ('other', _('Другое')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='test_results',
        verbose_name=_('Медицинская карта')
    )
    
    # Основная информация
    test_name = models.CharField(_('Название исследования'), max_length=255)
    test_type = models.CharField(
        _('Тип исследования'),
        max_length=20,
        choices=TEST_TYPES,
        default='other'
    )
    
    # Результаты
    result_numeric = models.FloatField(
        _('Числовой результат'),
        null=True,
        blank=True,
        help_text=_('Числовое значение результата, если применимо')
    )
    result_text = models.TextField(
        _('Текстовый результат'),
        blank=True,
        help_text=_('Текстовое описание результата')
    )
    
    # Референсные значения
    reference_range = models.CharField(
        _('Референсные значения'),
        max_length=100,
        blank=True,
        help_text=_('Нормальный диапазон значений')
    )
    unit = models.CharField(
        _('Единицы измерения'),
        max_length=20,
        blank=True,
        help_text=_('Единицы измерения результата')
    )
    
    # Статус
    is_abnormal = models.BooleanField(
        _('Отклонение от нормы'),
        default=False,
        help_text=_('Отмечено, если результат выходит за пределы нормы')
    )
    
    # Метаданные
    collected_at = models.DateTimeField(
        _('Дата и время забора'),
        default=timezone.now
    )
    processed_at = models.DateTimeField(
        _('Дата и время обработки'),
        null=True,
        blank=True
    )
    notes = models.TextField(_('Примечания'), blank=True)
    
    # Файлы результатов (если есть)
    result_file = models.FileField(
        _('Файл с результатами'),
        upload_to='test_results/%Y/%m/%d/',
        null=True,
        blank=True
    )
    
    # Ответственный
    ordered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ordered_tests',
        verbose_name=_('Назначил')
    )
    
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('Результат исследования')
        verbose_name_plural = _('Результаты исследований')
        ordering = ['-collected_at', 'test_name']
    
    def __str__(self):
        return f"{self.test_name} - {self.medical_record.patient.get_full_name()} ({self.collected_at.strftime('%d.%m.%Y')})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('emr:test_result_detail', args=[str(self.id)])
    
    @property
    def result_display(self):
        """Форматированный вывод результата"""
        if self.result_numeric is not None:
            result = f"{self.result_numeric}"
            if self.unit:
                result += f" {self.unit}"
            if self.reference_range:
                result += f" ({self.reference_range})"
            return result
        return self.result_text or ""
    
    def save(self, *args, **kwargs):
        # При необходимости можно добавить логику проверки на нормальные значения
        super().save(*args, **kwargs)
