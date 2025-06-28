from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import (MedicalRecord, MedicalRecordEntry, TestResult, 
                    Prescription, TreatmentItem, TreatmentCategory)

User = get_user_model()


class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'has_chronic_diseases', 'has_disability')
    search_fields = ('patient__first_name', 'patient__last_name', 'patient__middle_name')
    list_filter = ('disability',)
    
    def patient_name(self, obj):
        return str(obj.patient)
    patient_name.short_description = _('Пациент')
    patient_name.admin_order_field = 'patient__last_name'
    
    def has_chronic_diseases(self, obj):
        return bool(obj.chronic_diseases)
    has_chronic_diseases.boolean = True
    has_chronic_diseases.short_description = _('Хронические заболевания')
    
    def has_disability(self, obj):
        return obj.disability != 'no'
    has_disability.boolean = True
    has_disability.short_description = _('Инвалидность')


class MedicalRecordEntryAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'entry_type_display', 'title', 'patient_name', 'created_by_name')
    list_filter = ('entry_type', 'is_confidential', 'is_important', 'created_at')
    search_fields = ('title', 'content', 'medical_record__patient__first_name', 
                    'medical_record__patient__last_name', 'medical_record__patient__middle_name', 
                    'created_by__first_name', 'created_by__last_name', 'created_by__username')
    date_hierarchy = 'created_at'
    
    def entry_type_display(self, obj):
        return obj.get_entry_type_display()
    entry_type_display.short_description = _('Тип записи')
    
    def patient_name(self, obj):
        return str(obj.medical_record.patient)
    patient_name.short_description = _('Пациент')
    patient_name.admin_order_field = 'medical_record__patient__last_name'
    
    def created_by_name(self, obj):
        return obj.created_by.get_full_name() or obj.created_by.username
    created_by_name.short_description = _('Автор')
    created_by_name.admin_order_field = 'created_by__last_name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'medical_record__patient', 'created_by'
        )


class TestResultAdmin(admin.ModelAdmin):
    list_display = ('test_name', 'test_type_display', 'result_preview', 'collected_at', 'patient_name')
    list_filter = ('test_type', 'is_abnormal', 'collected_at')
    search_fields = ('test_name', 'medical_record__patient__first_name',
                    'medical_record__patient__last_name', 'medical_record__patient__middle_name', 'notes')
    date_hierarchy = 'collected_at'
    
    def test_type_display(self, obj):
        return obj.get_test_type_display()
    test_type_display.short_description = _('Тип исследования')
    
    def result_preview(self, obj):
        if obj.result_numeric is not None:
            return f"{obj.result_numeric} {obj.unit or ''}"
        return obj.result_text[:100] + '...' if obj.result_text else "-"
    result_preview.short_description = _('Результат')
    
    def patient_name(self, obj):
        return str(obj.medical_record.patient)
    patient_name.short_description = _('Пациент')
    patient_name.admin_order_field = 'medical_record__patient__last_name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('medical_record', 'medical_record__patient')


@admin.register(TreatmentCategory)
class TreatmentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(TreatmentItem)
class TreatmentItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name',)
    list_filter = ('category',)
    raw_id_fields = ('category',)


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('treatment_item', 'status_display', 'frequency_display', 'patient_name', 'start_date', 'end_date')
    list_filter = ('status', 'frequency', 'is_prn', 'start_date', 'end_date', 'treatment_item__category')
    search_fields = ('treatment_item__name', 'description', 'medical_record__patient__first_name',
                    'medical_record__patient__last_name', 'medical_record__patient__middle_name')
    date_hierarchy = 'start_date'
    raw_id_fields = ('treatment_item',)

    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = _('Статус')

    def frequency_display(self, obj):
        return obj.get_frequency_display()
    frequency_display.short_description = _('Периодичность')

    def patient_name(self, obj):
        return str(obj.medical_record.patient)
    patient_name.short_description = _('Пациент')
    patient_name.admin_order_field = 'medical_record__patient__last_name'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('medical_record__patient', 'treatment_item')


# Register models with admin site
admin.site.register(MedicalRecord, MedicalRecordAdmin)
admin.site.register(MedicalRecordEntry, MedicalRecordEntryAdmin)
admin.site.register(TestResult, TestResultAdmin)

