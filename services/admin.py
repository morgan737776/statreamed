from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDay, TruncMonth
from django.contrib.auth import get_user_model
from datetime import datetime

from .models import (
    ServiceCategory, ServiceItem, ServiceAppointment, 
    ServiceContract, ContractService, Payment
)
from core.services_zoom import ZoomService

class ServiceItemInline(admin.TabularInline):
    model = ServiceItem
    extra = 0
    fields = ('name', 'code', 'price', 'duration', 'duration_unit', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    show_change_link = True

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    list_per_page = 20
    inlines = [ServiceItemInline]
    
    def service_count(self, obj):
        return obj.services.count()
    service_count.short_description = _('Services Count')

@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'service_type', 'price', 'get_duration_display', 'is_active')
    list_filter = ('category', 'service_type', 'is_active', 'requires_specialist')
    search_fields = ('name', 'code', 'description')
    list_editable = ('price', 'is_active')
    list_per_page = 30
    date_hierarchy = 'created_at'
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('category', 'name', 'code', 'description')
        }),
        (_('Service Details'), {
            'fields': ('service_type', 'price', 'duration', 'duration_unit', 'requires_specialist')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

class ContractServiceInline(admin.TabularInline):
    model = ContractService
    extra = 1
    fields = ('service', 'quantity', 'unit_price', 'discount', 'total_price')
    readonly_fields = ('total_price',)
    autocomplete_fields = ('service',)

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('payment_number', 'amount', 'payment_method', 'status', 'payment_date')
    readonly_fields = ('payment_number',)

@admin.register(ServiceContract)
class ServiceContractAdmin(admin.ModelAdmin):
    inlines = [ContractServiceInline, PaymentInline]
    list_display = ('contract_number', 'client', 'start_date', 'end_date', 'status', 'total_amount', 'final_amount')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('contract_number', 'client__first_name', 'client__last_name', 'client__email')
    date_hierarchy = 'start_date'
    list_select_related = ('client',)
    autocomplete_fields = ('client',)
    readonly_fields = ('contract_number', 'total_amount', 'tax_amount', 'final_amount', 'created_at', 'updated_at')
    fieldsets = (
        (_('Contract Information'), {
            'fields': ('contract_number', 'client', 'status')
        }),
        (_('Dates'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('Financial Information'), {
            'fields': ('total_amount', 'discount', 'tax_rate', 'tax_amount', 'final_amount')
        }),
        (_('Terms & Notes'), {
            'fields': ('terms', 'notes')
        }),
        (_('Files'), {
            'fields': ('contract_file',)
        }),
        (_('Metadata'), {
            'fields': ('signed_at', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ServiceAppointment)
class ServiceAppointmentAdmin(admin.ModelAdmin):
    list_display = ('appointment_number', 'client', 'service', 'specialist', 'appointment_date', 'start_time', 'status')
    list_filter = ('status', 'appointment_date', 'service', 'specialist')
    search_fields = ('appointment_number', 'client__first_name', 'client__last_name', 'service__name')
    list_select_related = ('client', 'service', 'specialist')
    date_hierarchy = 'appointment_date'
    readonly_fields = ('appointment_number', 'created_at', 'updated_at')
    autocomplete_fields = ('client', 'service', 'specialist')
    
    fieldsets = (
        (None, {
            'fields': ('appointment_number', 'client', 'service', 'specialist')
        }),
        (_('Appointment Details'), {
            'fields': ('appointment_date', 'start_time', 'end_time', 'status')
        }),
        (_('Telemedicine'), {
            'fields': ('is_telemedicine', 'zoom_meeting_id', 'zoom_start_url', 'zoom_join_url'),
            'classes': ('collapse',)
        }),
        (_('Additional Information'), {
            'fields': ('notes',)
        }),
        (_('Metadata'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        return list(readonly_fields) + ['zoom_meeting_id', 'zoom_start_url', 'zoom_join_url']

    def save_model(self, request, obj, form, change):
        # Сначала сохраняем объект, чтобы получить ID и другие данные
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

        # Если это телемедицина и встреча еще не создана
        if obj.is_telemedicine and not obj.zoom_meeting_id:
            try:
                zoom_service = ZoomService()
                
                # Формируем дату и время начала
                start_datetime = datetime.combine(obj.appointment_date, obj.start_time)
                
                # Определяем длительность (в минутах)
                duration = obj.service.duration if obj.service else 30 # По умолчанию 30 минут

                # Создаем встречу
                meeting_data = zoom_service.create_meeting(
                    topic=f"Консультация: {obj.client} и {obj.specialist}",
                    start_time=start_datetime,
                    duration_minutes=duration
                )
                
                # Обновляем объект записи
                obj.zoom_meeting_id = meeting_data.get('id')
                obj.zoom_start_url = meeting_data.get('start_url')
                obj.zoom_join_url = meeting_data.get('join_url')
                
                # Повторно сохраняем с данными от Zoom
                obj.save(update_fields=['zoom_meeting_id', 'zoom_start_url', 'zoom_join_url'])
                
                self.message_user(request, "Конференция Zoom успешно создана.", messages.SUCCESS)

            except Exception as e:
                self.message_user(request, f"Ошибка при создании конференции Zoom: {e}", messages.ERROR)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_number', 'contract', 'amount', 'payment_method', 'status', 'payment_date', 'receipt_sent')
    list_filter = ('status', 'payment_method', 'payment_date', 'receipt_sent')
    search_fields = ('payment_number', 'transaction_id', 'contract__contract_number')
    list_select_related = ('contract', 'contract__client')
    date_hierarchy = 'payment_date'
    readonly_fields = ('payment_number', 'created_at', 'updated_at')
    actions = ['send_receipts']
    
    fieldsets = (
        (_('Payment Information'), {
            'fields': ('payment_number', 'contract', 'amount', 'payment_method', 'status')
        }),
        (_('Transaction Details'), {
            'fields': ('transaction_id', 'payment_date')
        }),
        (_('Additional Information'), {
            'fields': ('notes', 'receipt_sent')
        }),
        (_('Metadata'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def send_receipts(self, request, queryset):
        """Action to send receipts for selected payments"""
        if 'apply' in request.POST:
            sent_count = 0
            for payment in queryset:
                if payment.send_receipt(request=request):
                    sent_count += 1
            
            self.message_user(
                request,
                _('Successfully sent %(count)d receipts.') % {'count': sent_count},
                messages.SUCCESS
            )
            return HttpResponseRedirect(request.get_full_path())
        
        return TemplateResponse(
            request,
            'admin/services/payment/send_receipt_confirmation.html',
            context={
                'title': _('Send Receipts'),
                'payments': queryset,
                'opts': self.model._meta,
            },
        )
    send_receipts.short_description = _('Send receipt for selected payments')

# Register remaining models that aren't registered with decorators
admin.site.register(ContractService)
