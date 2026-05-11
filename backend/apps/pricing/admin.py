from django.contrib import admin

from apps.pricing.models import ProductPrice


@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'variant',
        'customer_group',
        'amount',
        'currency',
        'tax_rate',
        'price_includes_tax',
        'valid_from',
        'valid_until',
        'is_active',
    )
    search_fields = ('product__name', 'variant__name', 'variant__sku')
    list_filter = (
        'customer_group',
        'currency',
        'is_active',
        'price_includes_tax',
    )
    raw_id_fields = ('product', 'variant')
