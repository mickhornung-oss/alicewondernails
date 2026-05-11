from django.contrib import admin

from apps.cart.models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    raw_id_fields = ('product', 'variant')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'session_key',
        'customer_group',
        'status',
        'currency',
        'updated_at',
    )
    list_filter = ('customer_group', 'status', 'currency')
    search_fields = ('user__email', 'user__username', 'session_key')
    raw_id_fields = ('user',)
    inlines = (CartItemInline,)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        'cart',
        'product',
        'variant',
        'quantity',
        'updated_at',
    )
    search_fields = (
        'product__name',
        'variant__name',
        'variant__sku',
        'cart__user__email',
    )
    raw_id_fields = ('cart', 'product', 'variant')
