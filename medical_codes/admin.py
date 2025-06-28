from django.contrib import admin
from .models import ICD10Code

@admin.register(ICD10Code)
class ICD10CodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_category', 'parent')
    list_filter = ('is_category',)
    search_fields = ('code', 'name')
    ordering = ('code',)
    list_per_page = 50
