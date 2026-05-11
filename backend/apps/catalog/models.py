from django.db import models


class ProductCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('sort_order', 'name')
        verbose_name = 'product category'
        verbose_name_plural = 'product categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    class ProductType(models.TextChoices):
        NAIL_POLISH = 'nail_polish', 'Nail polish'
        GEL = 'gel', 'Gel'
        CARE = 'care', 'Care'
        ACCESSORY = 'accessory', 'Accessory'
        SET = 'set', 'Set'
        OTHER = 'other', 'Other'

    class Visibility(models.TextChoices):
        PUBLIC = 'public', 'Public'
        B2C_ONLY = 'b2c_only', 'B2C only'
        B2B_ONLY = 'b2b_only', 'B2B only'
        HIDDEN = 'hidden', 'Hidden'

    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name='products',
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    short_description = models.TextField(blank=True)
    description = models.TextField(blank=True)
    collection_name = models.CharField(max_length=255, blank=True)
    product_type = models.CharField(
        max_length=32,
        choices=ProductType.choices,
        default=ProductType.OTHER,
    )
    visibility = models.CharField(
        max_length=16,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
    )
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    @property
    def is_visible_for_b2c(self):
        return self.visibility in {
            self.Visibility.PUBLIC,
            self.Visibility.B2C_ONLY,
        }

    @property
    def is_visible_for_b2b(self):
        return self.visibility in {
            self.Visibility.PUBLIC,
            self.Visibility.B2B_ONLY,
        }


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
    )
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=128, unique=True, null=True, blank=True)
    color_name = models.CharField(max_length=128, blank=True)
    color_code = models.CharField(max_length=32, blank=True)
    finish = models.CharField(max_length=128, blank=True)
    size_label = models.CharField(max_length=128, blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('product', 'sort_order', 'name')

    def __str__(self):
        return f'{self.product.name} - {self.name}'


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='images',
    )
    image = models.FileField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('product', 'sort_order')

    def __str__(self):
        label = self.alt_text or self.image.name
        return f'{self.product.name} - {label}'
