from django.contrib import admin

from .models import Product, ProductCategory, ProductImage, ProductVariant


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'sort_order', 'is_active')
    search_fields = ('name', 'slug')
    list_filter = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'product_type',
        'visibility',
        'is_active',
        'is_featured',
    )
    search_fields = ('name', 'slug', 'collection_name')
    list_filter = ('category', 'product_type', 'visibility', 'is_active', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    inlines = (ProductVariantInline, ProductImageInline)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'product',
        'sku',
        'color_name',
        'color_code',
        'is_default',
        'is_active',
        'sort_order',
    )
    search_fields = ('name', 'sku', 'color_name', 'product__name')
    list_filter = ('is_active', 'is_default', 'finish')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'variant', 'alt_text', 'is_primary', 'sort_order')
    list_filter = ('is_primary',)
    search_fields = ('product__name', 'variant__name', 'alt_text')
