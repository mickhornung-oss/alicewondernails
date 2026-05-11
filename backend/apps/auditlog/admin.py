from django.contrib import admin
from .models import AuditLogEntry


@admin.register(AuditLogEntry)
class AuditLogEntryAdmin(admin.ModelAdmin):
    """Admin-Interface für AuditLogEntry (read-only)."""
    
    list_display = [
        'created_at',
        'actor',
        'action',
        'entity_type',
        'entity_id',
        'entity_repr',
    ]
    
    list_filter = [
        'action',
        'entity_type',
        'created_at',
    ]
    
    search_fields = [
        'actor__email',
        'actor__username',
        'entity_type',
        'entity_id',
        'entity_repr',
        'message',
    ]
    
    readonly_fields = [
        'actor',
        'action',
        'entity_type',
        'entity_id',
        'entity_repr',
        'message',
        'changes',
        'metadata',
        'ip_address',
        'user_agent',
        'created_at',
    ]
    
    fieldsets = (
        ('Aktion', {
            'fields': ('actor', 'action', 'created_at'),
        }),
        ('Entität', {
            'fields': ('entity_type', 'entity_id', 'entity_repr'),
        }),
        ('Details', {
            'fields': ('message', 'changes', 'metadata'),
        }),
        ('Anfrage-Kontext', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',),
        }),
    )
    
    def has_add_permission(self, request):
        # Audit-Logs sollten nur über Services erstellt werden
        return False
    
    def has_change_permission(self, request, obj=None):
        # Audit-Logs sind read-only
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Löschen von Audit-Logs verhindern (optional kann es für sehr alte Logs erlaubt sein)
        return False
