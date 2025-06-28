from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from .models import RemdSettings, GisOmsSettings, EsiaSettings, FgisFssSettings

class SingletonModelAdmin(admin.ModelAdmin):
    """Базовый класс для моделей-одиночек (Singleton)."""

    def has_add_permission(self, request):
        # Запрещаем добавление новых объектов, если один уже существует
        return not self.model.objects.exists()

    def get_urls(self):
        urls = super().get_urls()
        # Переопределяем URL для списка, чтобы он сразу вёл на страницу редактирования
        # единственного объекта или на страницу создания, если объекта нет.
        model_name = self.model._meta.model_name
        custom_urls = [
            path('', self.admin_site.admin_view(self.changelist_redirect_view), name=f'{model_name}_changelist'),
        ]
        return custom_urls + urls

    def changelist_redirect_view(self, request):
        obj = self.model.objects.first()
        if obj:
            # Если объект существует, перенаправляем на его страницу редактирования
            return HttpResponseRedirect(reverse(f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change', args=(obj.pk,)))
        else:
            # Если объекта нет, перенаправляем на страницу создания
            return HttpResponseRedirect(reverse(f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_add'))

@admin.register(RemdSettings)
class RemdSettingsAdmin(SingletonModelAdmin):
    list_display = ('name', 'is_active', 'api_url', 'org_oid')
    fieldsets = (
        (None, {'fields': ('name', 'description', 'is_active')}),
        ('Параметры подключения', {'fields': ('api_url', 'org_oid', 'auth_token')}),
    )

@admin.register(GisOmsSettings)
class GisOmsSettingsAdmin(SingletonModelAdmin):
    list_display = ('name', 'is_active', 'api_url', 'wsdl_url')
    fieldsets = (
        (None, {'fields': ('name', 'description', 'is_active')}),
        ('Параметры подключения', {'fields': ('api_url', 'wsdl_url', 'username', 'password')}),
    )

@admin.register(EsiaSettings)
class EsiaSettingsAdmin(SingletonModelAdmin):
    list_display = ('name', 'is_active', 'client_id')
    fieldsets = (
        (None, {'fields': ('name', 'description', 'is_active')}),
        ('Параметры OAuth', {'fields': ('api_url', 'client_id', 'client_secret', 'redirect_uri', 'scope')}),
    )

@admin.register(FgisFssSettings)
class FgisFssSettingsAdmin(SingletonModelAdmin):
    list_display = ('name', 'is_active', 'fss_id')
    fieldsets = (
        (None, {'fields': ('name', 'description', 'is_active')}),
        ('Параметры подключения', {'fields': ('api_url', 'fss_id', 'certificate_thumbprint')}),
    )
