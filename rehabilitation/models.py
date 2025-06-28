from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from medical_codes.models import ICD10Code, ICFCode

class RehabilitationCard(models.Model):
    """
    Реабилитационная карта пациента. 
    Содержит основные сведения, собираемые при регистрации.
    """
    # Связь с пациентом
    patient = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='rehabilitation_card',
        verbose_name=_('Пациент')
    )

    # --- Сведения об организации (могут быть вынесены в отдельную модель) ---
    clinic_name = models.CharField(_('Наименование организации'), max_length=255, blank=True)
    clinic_address = models.CharField(_('Адрес организации'), max_length=255, blank=True)
    clinic_ogrn = models.CharField(_('ОГРН'), max_length=255, blank=True)

    # --- Общие сведения о карте ---
    card_number = models.CharField(_('Номер карты'), max_length=50, unique=True)
    card_date = models.DateField(_('Дата составления карты'), auto_now_add=True)
    
    # --- Сведения о получателе услуг ---
    SERVICE_RECIPIENT_CHOICES = [
        ('invalid', _('Инвалид')),
        ('child_invalid', _('Ребенок-инвалид')),
        ('other', _('Иное'))
    ]
    service_recipient_status = models.CharField(
        _('Статус получателя услуг'), 
        max_length=20, 
        choices=SERVICE_RECIPIENT_CHOICES, 
        blank=True
    )
    course_start_date = models.DateField(_('Дата начала реабилитационного курса'), null=True, blank=True)
    service_contract_number = models.CharField(_('Номер договора на услуги'), max_length=100, blank=True)
    service_contract_date = models.DateField(_('Дата договора на услуги'), null=True, blank=True)

    # --- II. Сведения об инвалидности (основные) ---
    DISABILITY_GROUP_CHOICES = [
        ('1', _('I группа')),
        ('2', _('II группа')),
        ('3', _('III группа')),
        ('child', _('Ребенок-инвалид')),
        ('none', _('Нет')),
    ]
    disability_group = models.CharField(
        _('Группа инвалидности'), 
        max_length=10, 
        choices=DISABILITY_GROUP_CHOICES, 
        blank=True
    )
    ipra_number = models.CharField(_('Номер ИПРА'), max_length=100, blank=True)
    ipra_date = models.DateField(_('Дата ИПРА'), null=True, blank=True)

    # --- Раздел 1: Диагнозы ---
    primary_diagnosis = models.TextField(_('Основной диагноз'), blank=True)
    primary_diagnosis_icd10 = models.ForeignKey(
        ICD10Code, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name=_('Код по МКБ-10')
    )
    concomitant_diagnosis = models.TextField(_('Сопутствующий диагноз'), blank=True)
    complications = models.TextField(_('Осложнения основного заболевания'), blank=True)

    # --- Раздел 2: Реабилитационный диагноз (по МКФ) ---
    rehab_diagnosis_b = models.ManyToManyField(
        ICFCode,
        verbose_name=_('Нарушения функций (домен b)'),
        help_text=_('Выберите коды, описывающие нарушения функций организма.'),
        related_name='rehab_cards_b',
        blank=True,
        limit_choices_to={'code__startswith': 'b'}
    )
    rehab_diagnosis_s = models.ManyToManyField(
        ICFCode,
        verbose_name=_('Нарушения структур (домен s)'),
        help_text=_('Выберите коды, описывающие нарушения структур организма.'),
        related_name='rehab_cards_s',
        blank=True,
        limit_choices_to={'code__startswith': 's'}
    )
    rehab_diagnosis_d = models.ManyToManyField(
        ICFCode,
        verbose_name=_('Активность и участие (домен d)'),
        help_text=_('Выберите коды, описывающие ограничения активности и участия.'),
        related_name='rehab_cards_d',
        blank=True,
        limit_choices_to={'code__startswith': 'd'}
    )
    environmental_factors = models.TextField(_('Факторы среды (по МКФ)'), blank=True, help_text=_('Опишите факторы окружающей среды, влияющие на пациента.'))

    # --- Раздел 3: Цели реабилитации ---
    long_term_goal = models.TextField(_('Долгосрочная цель реабилитации'), blank=True)
    short_term_goals = models.TextField(_('Краткосрочные цели (задачи)'), blank=True)

    # --- Раздел 4: Реабилитационная команда (упрощенно) ---
    rehab_team = models.TextField(_('Состав мультидисциплинарной реабилитационной команды'), blank=True, help_text=_('Перечислите специалистов, участвующих в реабилитации.'))

    # --- Раздел 5: План мероприятий (упрощенно) ---
    rehab_plan = models.TextField(_('Индивидуальный план медицинской реабилитации'), blank=True, help_text=_('Опишите запланированные мероприятия, их периодичность и ответственных.'))

    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('Реабилитационная карта')
        verbose_name_plural = _('Реабилитационные карты')
        ordering = ['-card_date']

    def __str__(self):
        return f'{_("Карта №")}{self.card_number} - {self.patient.get_full_name()}'
