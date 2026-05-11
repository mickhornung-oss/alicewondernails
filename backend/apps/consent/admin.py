from django.contrib import admin
from .models import ConsentCategory, ConsentRecord


@admin.register(ConsentCategory)
class ConsentCategoryAdmin(admin.ModelAdmin):
    """Admin für ConsentCategory."""
    list_display = ['key', 'name', 'is_required', 'is_active', 'sort_order']
    list_filter = ['is_required', 'is_active']
    search_fields = ['key', 'name']
    ordering = ['sort_order', 'key']


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    """Admin für ConsentRecord."""
    list_display = ['category', 'user', 'session_key', 'granted', 'consent_version', 'source', 'created_at']
    list_filter = ['granted', 'source', 'category']
    search_fields = ['user__email', 'user__username', 'session_key', 'consent_version']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
