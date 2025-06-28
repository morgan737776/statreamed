from django.contrib import admin
from .models import SelectionCommitteeApplication, MedicalCommitteeConclusion

@admin.register(SelectionCommitteeApplication)
class SelectionCommitteeApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'status', 'appointment_date', 'operator', 'created_at')
    list_filter = ('status', 'operator', 'created_at')
    search_fields = ('full_name', 'phone_number', 'diagnosis')
    list_editable = ('status', 'appointment_date')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Данные пациента', {
            'fields': ('full_name', 'date_of_birth', 'phone_number', 'address', 'diagnosis')
        }),
        ('Служебная информация', {
            'fields': ('operator', 'operator_comment', 'created_at')
        }),
        ('Работа комиссии', {
            'fields': ('status', 'appointment_date', 'committee_comment')
        }),
    )

@admin.register(MedicalCommitteeConclusion)
class MedicalCommitteeConclusionAdmin(admin.ModelAdmin):
    list_display = ('application', 'status', 'final_decision', 'appointment_date')
    list_filter = ('status', 'final_decision')
    search_fields = ('application__full_name',)
    autocomplete_fields = ['application']
    list_editable = ('status', 'final_decision', 'appointment_date')
