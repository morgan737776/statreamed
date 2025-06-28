from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

# Assuming the Patient model is in the 'core' app.
# If not, this import will need to be adjusted.
from core.models import Patient

User = get_user_model()

class DocumentCategory(models.Model):
    """
    Категория для организации документов, например, 'Медицинские записи', 'Контракты'.
    """
    name = models.CharField(_('Название категории'), max_length=100, unique=True)
    description = models.TextField(_('Описание'), blank=True, null=True)
    template_content = models.TextField(_('Шаблон документа'), blank=True, null=True, help_text=_('HTML-шаблон с плейсхолдерами для генерации документов.'))

    class Meta:
        verbose_name = _('Категория документа')
        verbose_name_plural = _('Категории документов')
        ordering = ['name']

    def __str__(self):
        return self.name

def get_document_upload_path(instance, filename):
    """
    Generates the upload path for a document file.
    Files will be stored in: MEDIA_ROOT/documents/<patient_id>/<filename>
    """
    return f'documents/{instance.patient.id}/{filename}'

from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver

class Document(models.Model):
    """
    Представляет собой отдельный документ в системе.
    """
    STATUS_CHOICES = [
        ('draft', _('Черновик')),
        ('pending_approval', _('Ожидает утверждения')),
        ('approved', _('Утвержден')),
        ('archived', _('В архиве')),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='managed_documents',
        verbose_name=_('Пациент')
    )
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name=_('Категория')
    )
    title = models.CharField(_('Название'), max_length=255)
    description = models.TextField(_('Описание'), blank=True)
    file = models.FileField(_('Файл'), upload_to=get_document_upload_path)
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_uploaded_documents',
        verbose_name=_('Загружен кем')
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_documents',
        verbose_name=_('Утвержден кем')
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата утверждения')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))

    class Meta:
        verbose_name = _('Документ')
        verbose_name_plural = _('Документы')
        ordering = ['-created_at']
        permissions = [
            ('approve_document', _('Может утверждать документ')),
        ]

    def __str__(self):
        return f'{self.title} - {self.patient.get_full_name()}'

class DocumentVersion(models.Model):
    document = models.ForeignKey('Document', on_delete=models.CASCADE, related_name='versions', verbose_name=_('Оригинал документа'))
    title = models.CharField(_('Название'), max_length=255)
    description = models.TextField(_('Описание'), blank=True)
    file = models.FileField(_('Файл'), upload_to='document_versions/', blank=True, null=True)
    status = models.CharField(_('Статус'), max_length=32)
    category = models.ForeignKey('DocumentCategory', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Категория'))
    patient = models.ForeignKey('core.Patient', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Пациент'))
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Изменил'))
    created_at = models.DateTimeField(_('Дата версии'), auto_now_add=True)

    class Meta:
        verbose_name = _('Версия документа')
        verbose_name_plural = _('Версии документа')
        ordering = ['-created_at']

    def __str__(self):
        return f"Версия {self.title} ({self.created_at:%d.%m.%Y %H:%M})"

from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=Document)
def create_document_version(sender, instance, **kwargs):
    if not instance.pk:
        return  # Не создавать версию для новых документов
    try:
        old = Document.objects.get(pk=instance.pk)
    except Document.DoesNotExist:
        return
    # Сохраняем только если есть изменения
    fields = ['title', 'description', 'file', 'status', 'category', 'patient']
    changed = any(getattr(old, f) != getattr(instance, f) for f in fields)
    if changed:
        DocumentVersion.objects.create(
            document=old,
            title=old.title,
            description=old.description,
            file=old.file,
            status=old.status,
            category=old.category,
            patient=old.patient,
            changed_by=getattr(instance, '_changed_by', None)
        )
