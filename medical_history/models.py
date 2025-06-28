# -*- coding: utf-8 -*-
from django.db import models
from core.models import Patient
from django.utils.translation import gettext_lazy as _

class ICD10Disease(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name=_("Код МКБ-10"))
    name = models.TextField(verbose_name=_("Название болезни"))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                             related_name='children', verbose_name=_('Родительская категория'))
    is_category = models.BooleanField(_('Это категория?'), default=False)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = _("Болезнь (МКБ-10)")
        verbose_name_plural = _("Справочник МКБ-10")
        ordering = ['code']

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='history_medical_records', verbose_name=_("Пациент"))
    disease = models.ForeignKey(ICD10Disease, on_delete=models.PROTECT, verbose_name=_("Диагноз по МКБ-10"))
    diagnosis_date = models.DateField(verbose_name=_("Дата постановки диагноза"))
    notes = models.TextField(blank=True, verbose_name=_("Примечания"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))

    def __str__(self):
        return _('Запись для {} от {}').format(self.patient, self.diagnosis_date)

    class Meta:
        verbose_name = _("Медицинская запись")
        verbose_name_plural = _("Медицинские записи")
        ordering = ['-diagnosis_date']
