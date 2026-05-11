from django.contrib import admin

from apps.orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        'product_id_snapshot',
        'variant_id_snapshot',
        'price_id_snapshot',
        'product_name',
        'variant_name',
        'sku',
        'customer_group',
        'quantity',
        'unit_amount',
        'line_total',
        'currency',
        'tax_rate',
        'price_includes_tax',
        'created_at',
        'updated_at',
    )
    raw_id_fields = ('product', 'variant', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'user',
        'customer_group',
        'status',
        'total_amount',
        'currency',
        'item_count',
        'created_at',
    )
    list_filter = ('customer_group', 'status', 'currency', 'created_at')
    search_fields = (
        'order_number',
        'user__email',
        'user__username',
        'billing_full_name',
        'shipping_full_name',
    )
    readonly_fields = (
        'order_number',
        'subtotal_amount',
        'shipping_amount',
        'total_amount',
        'item_count',
        'shipping_snapshot',
        'payment_snapshot',
        'checkout_snapshot',
        'placed_at',
        'cancelled_at',
        'created_at',
        'updated_at',
    )
    raw_id_fields = ('user', 'cart')
    inlines = (OrderItemInline,)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'product_name',
        'variant_name',
        'quantity',
        'unit_amount',
        'line_total',
        'currency',
    )
    search_fields = (
        'order__order_number',
        'product_name',
        'variant_name',
        'sku',
    )
    readonly_fields = (
        'product_id_snapshot',
        'variant_id_snapshot',
        'price_id_snapshot',
        'product_name',
        'variant_name',
        'sku',
        'customer_group',
        'quantity',
        'unit_amount',
        'line_total',
        'currency',
        'tax_rate',
        'price_includes_tax',
        'created_at',
        'updated_at',
    )
    raw_id_fields = ('order', 'product', 'variant', 'price')
