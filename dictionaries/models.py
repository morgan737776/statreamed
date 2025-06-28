from django.db import models
from django.utils.translation import gettext_lazy as _

class ICD10(models.Model):
    code = models.CharField(_('Код МКБ-10'), max_length=8, unique=True)
    name = models.CharField(_('Наименование'), max_length=512)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    is_active = models.BooleanField(_('Актуален'), default=True)

    class Meta:
        verbose_name = _('Код МКБ-10')
        verbose_name_plural = _('Коды МКБ-10')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} — {self.name}"

class ServiceNomenclature(models.Model):
    code = models.CharField(_('Код услуги'), max_length=32, unique=True)
    name = models.CharField(_('Наименование услуги'), max_length=512)
    is_active = models.BooleanField(_('Актуальна'), default=True)

    class Meta:
        verbose_name = _('Медицинская услуга (номенклатура)')
        verbose_name_plural = _('Медицинские услуги (номенклатура)')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} — {self.name}"
