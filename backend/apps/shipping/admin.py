from django.contrib import admin

from .models import ShippingZone, ShippingMethod, ShippingRateSnapshot


@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    """Admin-Interface für ShippingZone."""
    
    list_display = [
        'name',
        'code',
        'is_active',
        'sort_order',
    ]
    
    list_filter = [
        'is_active',
    ]
    
    search_fields = [
        'name',
        'code',
    ]
    
    fieldsets = (
        ('Grundinfo', {
            'fields': ('name', 'code', 'sort_order'),
        }),
        ('Länder', {
            'fields': ('countries',),
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
        ('Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    """Admin-Interface für ShippingMethod."""
    
    list_display = [
        'name',
        'code',
        'zone',
        'customer_group',
        'base_price',
        'currency',
        'is_active',
        'sort_order',
    ]
    
    list_filter = [
        'zone',
        'customer_group',
        'is_active',
        'currency',
    ]
    
    search_fields = [
        'name',
        'code',
        'zone__name',
        'zone__code',
    ]
    
    fieldsets = (
        ('Grundinfo', {
            'fields': ('zone', 'name', 'code', 'customer_group', 'sort_order'),
        }),
        ('Kosten', {
            'fields': ('base_price', 'currency'),
        }),
        ('Lieferdauer (geschätzt)', {
            'fields': ('estimated_min_days', 'estimated_max_days'),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
        ('Zeitstempel', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ShippingRateSnapshot)
class ShippingRateSnapshotAdmin(admin.ModelAdmin):
    """Admin-Interface für ShippingRateSnapshot (read-mostly)."""
    
    list_display = [
        'method_name',
        'zone_name',
        'customer_group',
        'amount',
        'currency',
        'created_at',
    ]
    
    list_filter = [
        'customer_group',
        'currency',
        'created_at',
    ]
    
    search_fields = [
        'method_name',
        'method_code',
        'zone_name',
        'zone_code',
    ]
    
    fieldsets = (
        ('Snapshot-Daten', {
            'fields': ('method', 'method_code', 'method_name'),
        }),
        ('Zone', {
            'fields': ('zone_code', 'zone_name'),
        }),
        ('Kosten', {
            'fields': ('customer_group', 'amount', 'currency'),
        }),
        ('Lieferdauer (geschätzt)', {
            'fields': ('estimated_min_days', 'estimated_max_days'),
            'classes': ('collapse',),
        }),
        ('Zeitstempel', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = [
        'method',
        'method_code',
        'method_name',
        'zone_code',
        'zone_name',
        'customer_group',
        'amount',
        'currency',
        'estimated_min_days',
        'estimated_max_days',
        'created_at',
    ]
    
    def has_add_permission(self, request):
        # Snapshots werden nur durch Services erstellt
        return False
    
    def has_change_permission(self, request, obj=None):
        # Snapshots sind unveränderlich
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Snapshots können durch Admin nicht gelöscht werden (Audit-Trail)
        return False
