from django.contrib import admin
from .models import CheckoutSession, CheckoutEvent


class CheckoutEventInline(admin.TabularInline):
    model = CheckoutEvent
    extra = 0
    fields = ('event_type', 'message', 'created_at')
    readonly_fields = ('event_type', 'message', 'created_at')
    can_delete = False


@admin.register(CheckoutSession)
class CheckoutSessionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'cart',
        'status',
        'customer_group',
        'cart_subtotal',
        'shipping_amount',
        'order_total',
        'item_count',
        'updated_at'
    )
    list_filter = (
        'status',
        'customer_group',
        'currency',
        'created_at'
    )
    search_fields = (
        'user__email',
        'user__username',
        'cart__session_key',
        'order__order_number'
    )
    raw_id_fields = (
        'user',
        'cart',
        'shipping_method',
        'payment_method',
        'order'
    )
    readonly_fields = (
        'cart_subtotal',
        'order_total',
        'item_count',
        'shipping_snapshot',
        'payment_snapshot',
        'legal_snapshot',
        'consent_snapshot',
        'started_at',
        'validated_at',
        'order_created_at',
        'cancelled_at',
        'created_at',
        'updated_at'
    )
    inlines = [CheckoutEventInline]

    fieldsets = (
        ('Basis-Informationen', {
            'fields': ('user', 'cart', 'status', 'customer_group', 'currency')
        }),
        ('Versand', {
            'fields': ('shipping_method', 'shipping_snapshot', 'shipping_amount')
        }),
        ('Zahlung', {
            'fields': ('payment_method', 'payment_snapshot')
        }),
        ('Summen', {
            'fields': ('cart_subtotal', 'order_total', 'item_count')
        }),
        ('Rechtliches & Consent', {
            'fields': ('legal_snapshot', 'consent_snapshot')
        }),
        ('Order', {
            'fields': ('order',)
        }),
        ('Zeitstempel', {
            'fields': (
                'started_at',
                'validated_at',
                'order_created_at',
                'cancelled_at',
                'expires_at',
                'created_at',
                'updated_at'
            )
        }),
    )


@admin.register(CheckoutEvent)
class CheckoutEventAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'checkout',
        'event_type',
        'message',
        'created_at'
    )
    list_filter = (
        'event_type',
        'created_at'
    )
    search_fields = (
        'message',
        'checkout__user__email',
        'checkout__order__order_number'
    )
    readonly_fields = (
        'checkout',
        'event_type',
        'message',
        'metadata',
        'created_at'
    )

    fieldsets = (
        ('Ereignis', {
            'fields': ('checkout', 'event_type')
        }),
        ('Details', {
            'fields': ('message', 'metadata')
        }),
        ('Zeitstempel', {
            'fields': ('created_at',)
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
