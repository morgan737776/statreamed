from django.contrib import admin
from .models import IntegrationLog

@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ("id", "timestamp", "user", "operation", "status")
    list_filter = ("status", "operation", "user", "timestamp")
    search_fields = ("operation", "user__username", "request_data", "response_data", "error")
    date_hierarchy = "timestamp"
