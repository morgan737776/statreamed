# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import Ward, Bed, Hospitalization, AdmissionRequest

@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ('name', 'floor', 'get_bed_count', 'get_occupied_beds')
    list_filter = ('floor',)
    search_fields = ('name',)

    def get_bed_count(self, obj):
        return obj.beds.count()
    get_bed_count.short_description = 'Всего коек'

    def get_occupied_beds(self, obj):
        return obj.beds.filter(status='OCCUPIED').count()
    get_occupied_beds.short_description = 'Занято коек'

@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ('bed_number', 'ward', 'status', 'patient')
    list_filter = ('ward', 'status')
    search_fields = ('bed_number', 'patient__last_name')

@admin.register(Hospitalization)
class HospitalizationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'bed', 'date_admitted', 'date_discharged', 'is_active')
    list_filter = ('is_active', 'bed__ward')
    search_fields = ('patient__last_name', 'patient__first_name')
    autocomplete_fields = ['patient', 'bed']
    list_editable = ('is_active', 'date_discharged')


@admin.register(AdmissionRequest)
class AdmissionRequestAdmin(admin.ModelAdmin):
    list_display = ('patient', 'status', 'bed', 'planned_admission_date', 'planned_discharge_date', 'requested_ward')
    list_filter = ('status', 'requested_ward', 'bed__ward')
    search_fields = ('patient__last_name', 'patient__first_name')
    autocomplete_fields = ['patient', 'requested_ward', 'bed']
    list_editable = ('status', 'bed', 'planned_admission_date', 'planned_discharge_date')

