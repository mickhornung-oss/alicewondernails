from django.contrib import admin
from .models import LegalDocument, LegalDocumentVersion


class LegalDocumentVersionInline(admin.TabularInline):
    """Inline Admin für LegalDocumentVersion."""
    model = LegalDocumentVersion
    extra = 0
    fields = ['version', 'status', 'effective_from', 'activated_at', 'archived_at', 'summary']
    readonly_fields = ['activated_at', 'archived_at']


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    """Admin für LegalDocument."""
    list_display = ['document_type', 'title', 'target_group', 'slug', 'is_required']
    list_filter = ['document_type', 'target_group', 'is_required']
    search_fields = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LegalDocumentVersionInline]


@admin.register(LegalDocumentVersion)
class LegalDocumentVersionAdmin(admin.ModelAdmin):
    """Admin für LegalDocumentVersion."""
    list_display = ['document', 'version', 'status', 'effective_from', 'activated_at', 'archived_at']
    list_filter = ['status', 'document__document_type', 'document__target_group']
    search_fields = ['document__title', 'version', 'summary']
    raw_id_fields = ['created_by', 'activated_by']
    readonly_fields = ['created_at', 'updated_at', 'activated_at', 'archived_at']
