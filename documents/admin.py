from django.contrib import admin
from .models import DocumentCategory, Document

@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

from django.utils.html import format_html
import csv
from django.http import HttpResponse
from .models import DocumentVersion

class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    fields = ('title', 'description', 'file', 'status', 'category', 'patient', 'changed_by', 'created_at', 'download_link')
    readonly_fields = fields
    can_delete = False
    show_change_link = False

    def download_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" download>Скачать</a>', obj.file.url)
        return '-'
    download_link.short_description = 'Скачать файл'

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    inlines = [DocumentVersionInline]

    list_display = (
        'preview', 'title', 'patient', 'category', 'status', 'approved_by', 'approved_at', 'uploaded_by', 'created_at', 'download_link')
    list_filter = ('status', 'category', 'created_at', 'approved_by', 'uploaded_by')
    search_fields = ('title', 'patient__first_name', 'patient__last_name', 'description')
    raw_id_fields = ('patient', 'uploaded_by', 'approved_by')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_editable = ('status',)
    actions = ['approve_selected', 'archive_selected', 'export_as_csv']

    fieldsets = (
        (None, {
            'fields': ('patient', 'title', 'category', 'status', 'description')
        }),
        ('File Information', {
            'fields': ('file', 'preview', 'download_link')
        }),
        ('Metadata', {
            'fields': ('uploaded_by', 'approved_by', 'approved_at', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'preview', 'download_link')

    def preview(self, obj):
        if obj.file:
            if obj.file.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                return format_html('<img src="{}" width="60" style="border-radius:4px;" />', obj.file.url)
            elif obj.file.url.lower().endswith('.pdf'):
                return format_html('<a href="{}" target="_blank">PDF</a>', obj.file.url)
            else:
                return format_html('<a href="{}" target="_blank">Файл</a>', obj.file.url)
        return '-'
    preview.short_description = 'Превью'

    def download_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" download>Скачать</a>', obj.file.url)
        return '-'
    download_link.short_description = 'Скачать файл'

    def approve_selected(self, request, queryset):
        updated = queryset.filter(status='pending_approval').update(status='approved')
        self.message_user(request, f'Утверждено документов: {updated}')
    approve_selected.short_description = 'Утвердить выбранные документы'

    def archive_selected(self, request, queryset):
        updated = queryset.exclude(status='archived').update(status='archived')
        self.message_user(request, f'В архив отправлено документов: {updated}')
    archive_selected.short_description = 'Архивировать выбранные документы'

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=documents.csv'
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        return response
    export_as_csv.short_description = 'Экспортировать выбранные в CSV'
