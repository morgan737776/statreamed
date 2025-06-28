from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from medical_codes.models import ICD10Code

class SelectionCommitteeApplication(models.Model):
    """Заявка, поступающая в отборочную комиссию (первичный контакт)."""

    class Status(models.TextChoices):
        NEW = 'NEW', _('Новая')
        SCHEDULED = 'SCHEDULED', _('Запланирована встреча')
        COMPLETED = 'COMPLETED', _('Встреча состоялась')
        APPROVED = 'APPROVED', _('Одобрено для врачебной комиссии')
        REJECTED = 'REJECTED', _('Отклонено')
        CLARIFY = 'CLARIFY', _('Требует уточнения')

    # Данные пациента
    full_name = models.CharField(_("ФИО пациента"), max_length=255)
    date_of_birth = models.DateField(_("Дата рождения"))
    phone_number = models.CharField(_("Номер телефона"), max_length=20)
    address = models.TextField(_("Адрес регистрации"), blank=True)
    diagnosis = models.TextField(_("Предварительный диагноз"), help_text=_("Со слов пациента или из направления"))

    # Служебная информация
    operator = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        verbose_name=_("Оператор"),
        related_name='created_applications',
        help_text=_("Сотрудник, принявший обращение")
    )
    created_at = models.DateTimeField(_("Дата и время обращения"), auto_now_add=True)
    operator_comment = models.TextField(_("Комментарий оператора"), blank=True)

    # Запись и результат
    appointment_date = models.DateTimeField(verbose_name=_("Назначенная дата и время заседания"), null=True, blank=True)
    status = models.CharField(_("Статус заявки"), max_length=10, choices=Status.choices, default=Status.NEW)
    committee_comment = models.TextField(_("Комментарий отборочной комиссии"), blank=True)
    
    # Связь с кодами МКБ-10
    icd10_codes = models.ManyToManyField(
        ICD10Code,
        verbose_name=_('Коды МКБ-10'),
        related_name='selection_applications',
        blank=True,
        help_text=_('Выберите соответствующие коды МКБ-10')
    )

    def __str__(self):
        return f"Заявка №{self.id} от {self.created_at.strftime('%Y-%m-%d')} на {self.full_name}"

    class Meta:
        verbose_name = _("Заявка в отборочную комиссию")
        verbose_name_plural = _("Заявки в отборочную комиссию")
        ordering = ['-created_at']


class MedicalCommitteeConclusion(models.Model):
    """Заключение врачебной комиссии (финальное решение)."""

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Ожидает записи')
        SCHEDULED = 'SCHEDULED', _('Запланирована встреча')
        CONCLUDED = 'CONCLUDED', _('Решение принято')

    class Decision(models.TextChoices):
        HOSPITALIZATION = 'HOSPITAL', _('Рекомендована госпитализация')
        OUTPATIENT = 'OUTPATIENT', _('Рекомендовано амбулаторное лечение')
        HOME_CARE = 'HOME_CARE', _('Рекомендовано лечение на дому')
        REJECTED = 'REJECTED', _('Отклонено')

    application = models.OneToOneField(
        SelectionCommitteeApplication, 
        on_delete=models.CASCADE, 
        verbose_name=_("Заявка"),
        related_name='medical_conclusion'
    )
    appointment_date = models.DateTimeField(_("Дата и время записи во врачебную комиссию"), null=True, blank=True)
    status = models.CharField(_("Статус"), max_length=10, choices=Status.choices, default=Status.PENDING)
    final_decision = models.CharField(_("Итоговое решение"), max_length=10, choices=Decision.choices, blank=True)
    committee_comment = models.TextField(_("Комментарий врачебной комиссии"), blank=True)

    def __str__(self):
        return f"Заключение по заявке №{self.application.id} ({self.application.full_name})"

    class Meta:
        verbose_name = _("Заключение врачебной комиссии")
        verbose_name_plural = _("Заключения врачебной комиссии")
        ordering = ['-application__created_at']

