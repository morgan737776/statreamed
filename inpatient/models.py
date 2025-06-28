# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from core.models import Patient
from commissions.models import SelectionCommitteeApplication

class Ward(models.Model):
    """Палата в стационаре"""
    name = models.CharField(max_length=100, verbose_name=_("Название палаты"))
    floor = models.IntegerField(verbose_name=_("Этаж"), blank=True, null=True)
    notes = models.TextField(verbose_name=_("Примечания"), blank=True)

    class Meta:
        verbose_name = _("Палата")
        verbose_name_plural = _("Палаты")
        ordering = ['floor', 'name']

    def __str__(self):
        return f"Палата №{self.name}"

class Bed(models.Model):
    """Койка в палате"""
    BED_STATUS_CHOICES = [
        ('FREE', _('Свободна')),
        ('OCCUPIED', _('Занята')),
        ('CLEANING', _('На санобработке')),
        ('REPAIR', _('На ремонте')),
    ]

    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='beds', verbose_name=_("Палата"))
    bed_number = models.CharField(max_length=20, verbose_name=_("Номер койки"))
    status = models.CharField(max_length=10, choices=BED_STATUS_CHOICES, default='FREE', verbose_name=_("Статус"))
    patient = models.OneToOneField(Patient, on_delete=models.SET_NULL, null=True, blank=True, related_name='bed', verbose_name=_("Пациент"))

    class Meta:
        verbose_name = _("Койка")
        verbose_name_plural = _("Койки")
        ordering = ['ward', 'bed_number']
        unique_together = ('ward', 'bed_number')

    def __str__(self):
        return f"{self.ward} - Койка {self.bed_number}"

class AdmissionRequest(models.Model):
    """
    Заявка на госпитализацию (очередь).
    """
    STATUS_CHOICES = [
        ('WAITING', _('Ожидает госпитализации')),
        ('FULFILLED', _('Госпитализирован')),
        ('CANCELLED', _('Отменена')),
    ]

    patient = models.ForeignKey(
        Patient, 
        on_delete=models.CASCADE, 
        related_name='admission_requests',
        verbose_name=_("Пациент")
    )
    bed = models.ForeignKey(
        Bed,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Забронированная койка"),
        help_text=_("Выберите конкретную койку для бронирования. Отобразится на диаграмме Ганта.")
    )
    requested_ward = models.ForeignKey(
        Ward, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name=_("Желаемая палата")
    )
    notes = models.TextField(blank=True, verbose_name=_("Примечания к заявке"))
    planned_admission_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("Планируемая дата госпитализации")
    )
    planned_discharge_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name=_("Планируемая дата выписки")
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='WAITING', 
        verbose_name=_("Статус заявки")
    )
    date_requested = models.DateTimeField(default=timezone.now, verbose_name=_("Дата создания заявки"))
    source_commission_application = models.OneToOneField(
        'commissions.SelectionCommitteeApplication',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_admission_request',
        verbose_name=_("Исходное обращение в комиссию")
    )

    class Meta:
        verbose_name = _("Заявка на госпитализацию")
        verbose_name_plural = _("Очередь на госпитализацию")
        ordering = ['date_requested']

    def __str__(self):
        return f"Заявка от {self.patient} на {self.date_requested.strftime('%Y-%m-%d')}"


class Hospitalization(models.Model):
    """
    Запись о госпитализации пациента.
    Хранит историю пребывания пациентов в стационаре.
    """
    patient = models.ForeignKey(
        Patient, 
        on_delete=models.CASCADE, 
        related_name='hospitalizations',
        verbose_name=_("Пациент")
    )
    bed = models.ForeignKey(
        Bed, 
        on_delete=models.CASCADE, 
        related_name='hospitalizations',
        verbose_name=_("Койка")
    )
    date_admitted = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Дата и время госпитализации")
    )
    date_discharged = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name=_("Дата и время выписки")
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активная госпитализация"),
        help_text=_("Отмечает, находится ли пациент в стационаре в данный момент по этой записи.")
    )

    class Meta:
        verbose_name = _("Госпитализация")
        verbose_name_plural = _("Госпитализации")
        ordering = ['-date_admitted']

    def __str__(self):
        return f"Госпитализация {self.patient} с {self.date_admitted.strftime('%Y-%m-%d')}"
