from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Count
from django.utils import timezone
from django.http import HttpResponse
import csv

# --- project models ---
from .models import (
    Patient,
    # Staff,  # Временно отключено
    SystemSettings,
    IntegrationSettings,
    AuditLog as CoreAuditLog,
    Appointment,
    Notification,
    TreatmentReminder,
    ExternalCalendarSync,
    MedicalRecord,
)


# ---------------------------------------------------------------------------
#  Patient admin
# ---------------------------------------------------------------------------
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "get_full_name",
        "date_of_birth",
        "phone",
        "email",
        "status",
        "blood_type",
    )
    list_filter = ("gender", "status", "blood_type")
    search_fields = ("first_name", "last_name", "middle_name", "phone", "email")
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        (_("Основная информация"), {
            'fields': ('first_name', 'last_name', 'middle_name', 'date_of_birth', 'gender')
        }),
        (_("Контакты"), {
            'fields': ('phone', 'email', 'address')
        }),
        (_("Медицинская информация"), {
            'fields': ('blood_type', 'allergies', 'chronic_diseases', 'status')
        }),
        (_("Дополнительно"), {
            'fields': ('passport_series', 'passport_number', 'insurance_policy', 'emergency_contact_name', 'emergency_contact_phone')
        }),
    )

    def get_full_name(self, obj):
        return f"{obj.last_name} {obj.first_name} {obj.middle_name or ''}".strip()
    get_full_name.short_description = "ФИО"


# ---------------------------------------------------------------------------
#  Appointment admin
# ---------------------------------------------------------------------------
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "patient",
        "start_datetime",
        "end_datetime",
        "status",
        "service",
        "doctor",
    )
    list_filter = ("status", "service", "doctor")
    search_fields = ("patient__first_name", "patient__last_name", "service__name", "doctor__username")
    date_hierarchy = "start_datetime"
    readonly_fields = ("created_at", "updated_at")


# ---------------------------------------------------------------------------
#  Notification admin
# ---------------------------------------------------------------------------
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "notification_type",
        "delivery_method", 
        "status",
        "created_at",
    )
    list_filter = ("notification_type", "delivery_method", "status")
    search_fields = ("title", "message")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "sent_at", "read_at")


# ---------------------------------------------------------------------------
#  Medical Record admin
# ---------------------------------------------------------------------------
@admin.register(MedicalRecord)
class CoreMedicalRecordAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "patient",
        "record_type",
        "priority",
        "created_by",
        "created_at",
    )
    list_filter = ("record_type", "priority", "is_important")
    search_fields = ("title", "content", "patient__first_name", "patient__last_name")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")


# ---------------------------------------------------------------------------
#  Treatment Reminder admin
# ---------------------------------------------------------------------------
@admin.register(TreatmentReminder)
class TreatmentReminderAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "patient",
        "frequency",
        "start_date",
        "is_active",
    )
    list_filter = ("frequency", "is_active")
    search_fields = ("title", "patient__first_name", "patient__last_name")
    date_hierarchy = "start_date"


# ---------------------------------------------------------------------------
#  External Calendar Sync admin
# ---------------------------------------------------------------------------
@admin.register(ExternalCalendarSync)
class ExternalCalendarSyncAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "provider",
        "is_active",
        "last_sync",
    )
    list_filter = ("provider", "is_active")
    search_fields = ("user__username", "calendar_id")
    readonly_fields = ("created_at", "last_sync")


# ---------------------------------------------------------------------------
#  System Settings admin
# ---------------------------------------------------------------------------
@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ("clinic_name", "language", "timezone", "maintenance_mode")
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not SystemSettings.objects.exists()


# ---------------------------------------------------------------------------
#  Integration Settings admin
# ---------------------------------------------------------------------------
@admin.register(IntegrationSettings)
class IntegrationSettingsAdmin(admin.ModelAdmin):
    list_display = ('service_1c_url', 'sms_provider', 'email_host')
    search_fields = ('service_1c_url', 'sms_provider')


# ---------------------------------------------------------------------------
#  Audit Log admin
# ---------------------------------------------------------------------------
@admin.register(CoreAuditLog)
class CoreAuditLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "model", "timestamp")
    list_filter = ("action", "model", "timestamp")
    search_fields = ("user__username", "action", "object_id")
    date_hierarchy = "timestamp"
    readonly_fields = ("user", "action", "model", "object_id", "old_value", "new_value", "timestamp")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False