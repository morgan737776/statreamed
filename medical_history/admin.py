# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import ICD10Disease, MedicalRecord

@admin.register(ICD10Disease)
class ICD10DiseaseAdmin(admin.ModelAdmin):
    search_fields = ('code', 'name')
    list_display = ('code', 'name')

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'disease', 'diagnosis_date')
    list_filter = ('diagnosis_date', 'disease')
    search_fields = ('patient__last_name', 'patient__first_name')
    autocomplete_fields = ['patient', 'disease']
