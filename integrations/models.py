import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class BaseIntegrationSettings(models.Model):
    """Абстрактная базовая модель для настроек интеграций."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(_('Активна'), default=False, help_text=_('Включена ли эта интеграция?'))
    name = models.CharField(_('Название системы'), max_length=255, unique=True)
    description = models.TextField(_('Описание'), blank=True, null=True)
    api_url = models.URLField(_('URL API/сервиса'), max_length=500)
    
    # Поля для аудита
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name

class RemdSettings(BaseIntegrationSettings):
    """Настройки для интеграции с РЭМД (Регистр электронных медицинских документов)."""
    org_oid = models.CharField(_('OID медицинской организации'), max_length=255, help_text=_('Уникальный идентификатор организации в РЭМД'))
    auth_token = models.CharField(_('Токен авторизации'), max_length=1024, blank=True, help_text=_('Секретный ключ для доступа к API'))

    class Meta:
        verbose_name = _('Настройка интеграции с РЭМД')
        verbose_name_plural = _('Настройки интеграции с РЭМД')

class GisOmsSettings(BaseIntegrationSettings):
    """Настройки для интеграции с ГИС ОМС."""
    wsdl_url = models.URLField(_('URL WSDL-сервиса'), max_length=500, help_text=_('Адрес SOAP-сервиса для обмена данными'))
    username = models.CharField(_('Имя пользователя'), max_length=255, blank=True)
    password = models.CharField(_('Пароль'), max_length=255, blank=True, help_text=_('Пароль для аутентификации в сервисе'))

    class Meta:
        verbose_name = _('Настройка интеграции с ГИС ОМС')
        verbose_name_plural = _('Настройки интеграции с ГИС ОМС')

class EsiaSettings(BaseIntegrationSettings):
    """Настройки для интеграции с ЕСИА (Госуслуги)."""
    client_id = models.CharField(_('ID клиента (мнемоника)'), max_length=255)
    client_secret = models.CharField(_('Секрет клиента'), max_length=1024, blank=True)
    redirect_uri = models.URLField(_('URI для перенаправления'), max_length=500)
    scope = models.CharField(_('Запрашиваемые права (scope)'), max_length=1024, default='openid profile email')

    class Meta:
        verbose_name = _('Настройка интеграции с ЕСИА')
        verbose_name_plural = _('Настройки интеграции с ЕСИА')

class FgisFssSettings(BaseIntegrationSettings):
    """Настройки для интеграции с ФГИС ФСС (ЭЛН)."""
    certificate_thumbprint = models.CharField(_('Отпечаток сертификта ЭЦП'), max_length=255, help_text=_('Используется для подписи запросов'))
    fss_id = models.CharField(_('Идентификатор страхователя в ФСС'), max_length=50, blank=True)

    class Meta:
        verbose_name = _('Настройка интеграции с ФГИС ФСС')
        verbose_name_plural = _('Настройки интеграции с ФГИС ФСС')

# Можно добавить остальные модели по аналогии:
# - Интеграция с ЕРН (Единый реестр населения)
# - Интеграция с системой мониторинга лекарственного обеспечения
# и т.д.
