"""Serializers for pricing API endpoints (v1.1 extension)."""

from rest_framework import serializers
from apps.pricing.models import ProductPrice
from apps.catalog.models import Product


class ProductPriceSerializer(serializers.ModelSerializer):
    """Serializer for ProductPrice - read-only, for pricing API."""
    
    type = serializers.SerializerMethodField()
    variant_sku = serializers.SerializerMethodField()
    variant_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductPrice
        fields = (
            'type',
            'variant_sku',
            'variant_name',
            'amount',
            'currency',
            'tax_rate',
            'price_includes_tax',
        )
        read_only_fields = fields
    
    def get_type(self, obj):
        """Return 'product' for product-level price, 'variant' for variant-level price."""
        return 'variant' if obj.variant_id else 'product'
    
    def get_variant_sku(self, obj):
        """Return variant SKU if variant exists, otherwise None."""
        return obj.variant.sku if obj.variant_id else None
    
    def get_variant_name(self, obj):
        """Return variant name if variant exists, otherwise None."""
        return obj.variant.name if obj.variant_id else None

