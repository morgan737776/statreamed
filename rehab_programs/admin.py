# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import RehabilitationProgram, RehabActivity, ScheduledActivity, RehabProgramTemplate

class RehabilitationProgramAdminForm(forms.ModelForm):
    template = forms.ModelChoiceField(
        queryset=RehabProgramTemplate.objects.all(),
        required=False,
        label=_("Создать по шаблону"),
        help_text=_("Выберите шаблон, чтобы автоматически заполнить программу и добавить стандартный набор процедур.")
    )

    class Meta:
        model = RehabilitationProgram
        fields = '__all__'


@admin.register(RehabilitationProgram)
class RehabilitationProgramAdmin(admin.ModelAdmin):
    form = RehabilitationProgramAdminForm
    list_display = ('patient', 'program_type', 'start_date', 'end_date', 'status', 'specialist')
    list_filter = ('program_type', 'status', 'start_date')
    search_fields = ('patient__last_name', 'patient__first_name', 'goal')
    autocomplete_fields = ['patient', 'specialist']

    def get_fieldsets(self, request, obj=None):
        if not obj:  # Форма добавления
            return (
                (None, {
                    'fields': ('template', 'patient', 'specialist', 'status', 'start_date', 'end_date')
                }),
                (_('Детали программы (заполнятся из шаблона, если выбран)'), {
                    'classes': ('collapse',),
                    'fields': ('program_type', 'goal')
                }),
            )
        # Форма изменения (без шаблона)
        return (
            (None, {
                'fields': ('patient', 'specialist', 'status', 'program_type', 'goal', 'start_date', 'end_date')
            }),
        )

    def save_model(self, request, obj, form, change):
        template = form.cleaned_data.get('template')

        if not change and template:
            # Копируем данные из шаблона в объект программы
            obj.program_type = template.program_type
            if not obj.goal:
                obj.goal = template.description

        super().save_model(request, obj, form, change)

        if not change and template:
            # После сохранения программы, создаем запланированные процедуры
            activities_to_create = [
                ScheduledActivity(
                    program=obj,
                    activity=activity,
                    scheduled_date=obj.start_date,  # По умолчанию ставим дату начала программы
                    status='PLANNED'
                )
                for activity in template.activities.all()
            ]
            ScheduledActivity.objects.bulk_create(activities_to_create)


@admin.register(RehabActivity)
class RehabActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'default_duration')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    fieldsets = (
        (None, {
            'fields': ('name', 'category')
        }),
        (_('Дополнительная информация'), {
            'classes': ('collapse',),
            'fields': ('description', 'default_duration', 'required_equipment'),
        }),
    )


@admin.register(RehabProgramTemplate)
class RehabProgramTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'program_type')
    list_filter = ('program_type',)
    search_fields = ('name', 'description')
    filter_horizontal = ('activities',)
    fieldsets = (
        (None, {
            'fields': ('name', 'program_type', 'description')
        }),
        (_('Состав программы'), {
            'fields': ('activities',),
        }),
    )


@admin.register(ScheduledActivity)
class ScheduledActivityAdmin(admin.ModelAdmin):
    list_display = ('program', 'activity', 'scheduled_date', 'status')
    list_filter = ('status', 'scheduled_date', 'activity')
    search_fields = ('program__patient__last_name', 'activity__name')
    autocomplete_fields = ['program', 'activity']
