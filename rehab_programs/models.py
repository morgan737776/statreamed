# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import Patient
from django.contrib.auth.models import User

class RehabilitationProgram(models.Model):
    PROGRAM_TYPE_CHOICES = [
        ('INPATIENT', _('Стационарная')),
        ('OUTPATIENT', _('Амбулаторная')),
        ('HOME_BASED', _('На дому')),
    ]

    STATUS_CHOICES = [
        ('PLANNED', _('Запланирована')),
        ('ACTIVE', _('Активна')),
        ('COMPLETED', _('Завершена')),
        ('CANCELLED', _('Отменена')),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='rehabilitation_programs', verbose_name=_("Пациент"))
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPE_CHOICES, verbose_name=_("Форма реабилитации"))
    specialist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Ведущий специалист"))
    
    start_date = models.DateField(verbose_name=_("Дата начала"))
    end_date = models.DateField(verbose_name=_("Дата окончания"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED', verbose_name=_("Статус"))

    goal = models.TextField(verbose_name=_("Цель реабилитации"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))

    def __str__(self):
        return f"{self.get_program_type_display()} программа для {self.patient} от {self.start_date}"

    class Meta:
        verbose_name = _("Программа реабилитации")
        verbose_name_plural = _("Программы реабилитации")
        ordering = ['-start_date']

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('rehab_programs:rehab_program_detail', kwargs={'program_pk': self.pk})


class RehabActivity(models.Model):
    """
    Справочник реабилитационных процедур и занятий.
    """
    CATEGORY_CHOICES = [
        ('CONSULT_DIAGNOSTIC', _('Консультативно-диагностический блок')),
        ('LFK_KINESIO', _('Лечебная физкультура и кинезиотерапия')),
        ('PHYSIO_HARDWARE', _('Аппаратная физиотерапия')),
        ('MASSAGE_MANUAL', _('Массаж и мануальные техники')),
        ('PSYCHO_NEURO', _('Психокоррекция и нейропсихология')),
        ('SPEECH_DEFECTO', _('Логопедическая и дефектологическая помощь')),
        ('ERGO_SOCIAL', _('Эрготерапия и социально-бытовая адаптация')),
        ('HYDRO_THERAPY', _('Бальнео- и гидротерапия')),
        ('OTHER', _('Прочие процедуры')),
    ]

    name = models.CharField(max_length=200, unique=True, verbose_name=_("Название процедуры/занятия"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='OTHER', verbose_name=_("Категория"))
    default_duration = models.PositiveIntegerField(default=30, help_text=_("Длительность процедуры в минутах"), verbose_name=_("Длительность (мин)"))
    required_equipment = models.TextField(blank=True, verbose_name=_("Необходимое оборудование"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Тип реабилитационной процедуры")
        verbose_name_plural = _("Справочник типов процедур")
        ordering = ['category', 'name']


class RehabProgramTemplate(models.Model):
    """
    Шаблон программы реабилитации.
    """
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Название шаблона программы"))
    description = models.TextField(blank=True, verbose_name=_("Описание программы"))
    program_type = models.CharField(max_length=20, choices=RehabilitationProgram.PROGRAM_TYPE_CHOICES, verbose_name=_("Форма реабилитации"))
    
    # Набор процедур, входящих в шаблон
    activities = models.ManyToManyField(RehabActivity, blank=True, verbose_name=_("Процедуры в шаблоне"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Шаблон программы реабилитации")
        verbose_name_plural = _("Шаблоны программ реабилитации")
        ordering = ['name']


class ScheduledActivity(models.Model):
    """
    Запланированная процедура в рамках программы реабилитации.
    """
    STATUS_CHOICES = [
        ('PLANNED', _('Запланировано')),
        ('COMPLETED', _('Проведено')),
        ('CANCELLED', _('Отменено')),
        ('MISSED', _('Пропущено')),
    ]

    program = models.ForeignKey(RehabilitationProgram, on_delete=models.CASCADE, related_name='scheduled_activities', verbose_name=_("Программа реабилитации"))
    activity = models.ForeignKey(RehabActivity, on_delete=models.CASCADE, verbose_name=_("Процедура"))
    specialist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Специалист"))
    scheduled_date = models.DateTimeField(verbose_name=_("Запланированная дата и время проведения"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED', verbose_name=_("Статус"))
    
    specialist_notes = models.TextField(blank=True, verbose_name=_("Заметки специалиста"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))

    def __str__(self):
        return f"{self.activity.name} для {self.program.patient} в {self.scheduled_date.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = _("Запланированная процедура")
        verbose_name_plural = _("Запланированные процедуры")
        ordering = ['scheduled_date']
