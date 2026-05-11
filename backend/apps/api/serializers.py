from rest_framework import serializers
from apps.catalog.models import ProductCategory, Product, ProductVariant
from apps.shipping.models import ShippingMethod
from apps.payments.models import PaymentMethod
from apps.legal.models import LegalDocumentVersion


class HealthSerializer(serializers.Serializer):
    """Serializer for health check response."""
    status = serializers.CharField()
    service = serializers.CharField()
    version = serializers.CharField()
    environment = serializers.CharField()


class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories - read-only."""
    class Meta:
        model = ProductCategory
        fields = ('id', 'name', 'slug', 'sort_order')
        read_only_fields = fields


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for product variants - read-only."""
    class Meta:
        model = ProductVariant
        fields = ('id', 'sku', 'name', 'color_name', 'color_code', 'finish', 'size_label', 'is_default')
        read_only_fields = fields


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list - read-only."""
    category = ProductCategorySerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'short_description', 'category', 'variants')
        read_only_fields = fields


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product detail - read-only."""
    category = ProductCategorySerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'description', 'short_description', 'category', 'variants')
        read_only_fields = fields


class ShippingMethodSerializer(serializers.ModelSerializer):
    """Serializer for shipping methods - read-only."""
    class Meta:
        model = ShippingMethod
        fields = ('id', 'name', 'code', 'customer_group', 'base_price', 'currency', 
                  'estimated_min_days', 'estimated_max_days')
        read_only_fields = fields


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for payment methods - read-only."""
    class Meta:
        model = PaymentMethod
        fields = ('id', 'name', 'code', 'provider', 'customer_group', 'description')
        read_only_fields = fields


class LegalDocumentVersionSerializer(serializers.ModelSerializer):
    """Serializer for legal document versions - metadata only."""
    document_type = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    target_group = serializers.SerializerMethodField()
    
    class Meta:
        model = LegalDocumentVersion
        fields = ('document_type', 'title', 'version', 'target_group', 'effective_from', 'status')
        read_only_fields = fields
    
    def get_document_type(self, obj):
        return obj.document.document_type if obj.document else None
    
    def get_title(self, obj):
        return obj.document.title if obj.document else None
    
    def get_target_group(self, obj):
        return obj.document.target_group if obj.document else None
