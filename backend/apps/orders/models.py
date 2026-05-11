from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class Order(models.Model):
    class CustomerGroup(models.TextChoices):
        B2C = 'b2c', 'B2C'
        B2B = 'b2b', 'B2B'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PLACED = 'placed', 'Placed'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    order_number = models.CharField(max_length=32, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
    )
    cart = models.ForeignKey(
        'cart.Cart',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )
    customer_group = models.CharField(
        max_length=8,
        choices=CustomerGroup.choices,
        default=CustomerGroup.B2C,
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    currency = models.CharField(max_length=3, default='EUR')
    subtotal_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    item_count = models.PositiveIntegerField(default=0)

    billing_full_name = models.CharField(max_length=255, blank=True)
    billing_company = models.CharField(max_length=255, blank=True)
    billing_street = models.CharField(max_length=255, blank=True)
    billing_postal_code = models.CharField(max_length=32, blank=True)
    billing_city = models.CharField(max_length=255, blank=True)
    billing_country = models.CharField(max_length=2, default='DE')

    shipping_full_name = models.CharField(max_length=255, blank=True)
    shipping_company = models.CharField(max_length=255, blank=True)
    shipping_street = models.CharField(max_length=255, blank=True)
    shipping_postal_code = models.CharField(max_length=32, blank=True)
    shipping_city = models.CharField(max_length=255, blank=True)
    shipping_country = models.CharField(max_length=2, default='DE')

    # Checkout Snapshots (AB 12: kontrollierte Erweiterung)
    shipping_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Final shipping amount from checkout"
    )
    shipping_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot of shipping method (no secrets)"
    )
    payment_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot of payment method (no secrets)"
    )
    checkout_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot of checkout context (customer_group, currency, item_count, amounts)"
    )

    placed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        constraints = (
            models.CheckConstraint(
                condition=Q(subtotal_amount__gte=0),
                name='orders_order_subtotal_non_negative',
            ),
            models.CheckConstraint(
                condition=Q(total_amount__gte=0),
                name='orders_order_total_non_negative',
            ),
            models.CheckConstraint(
                condition=Q(shipping_amount__gte=0),
                name='orders_order_shipping_amount_non_negative',
            ),
        )

    def __str__(self):
        return f'Order {self.order_number} ({self.status})'


class OrderItem(models.Model):
    class CustomerGroup(models.TextChoices):
        B2C = 'b2c', 'B2C'
        B2B = 'b2b', 'B2B'

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
    )
    variant = models.ForeignKey(
        'catalog.ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
    )
    price = models.ForeignKey(
        'pricing.ProductPrice',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
    )

    product_id_snapshot = models.PositiveIntegerField()
    variant_id_snapshot = models.PositiveIntegerField(null=True, blank=True)
    price_id_snapshot = models.PositiveIntegerField(null=True, blank=True)
    product_name = models.CharField(max_length=255)
    variant_name = models.CharField(max_length=255, blank=True)
    sku = models.CharField(max_length=128, blank=True)
    customer_group = models.CharField(
        max_length=8,
        choices=CustomerGroup.choices,
    )
    quantity = models.PositiveIntegerField()
    unit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    currency = models.CharField(max_length=3, default='EUR')
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    price_includes_tax = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created_at',)
        constraints = (
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name='orders_orderitem_quantity_positive',
            ),
            models.CheckConstraint(
                condition=Q(unit_amount__gte=0),
                name='orders_orderitem_unit_amount_non_negative',
            ),
            models.CheckConstraint(
                condition=Q(line_total__gte=0),
                name='orders_orderitem_line_total_non_negative',
            ),
        )

    def clean(self):
        errors = {}

        if self.quantity is not None and self.quantity <= 0:
            errors['quantity'] = 'Quantity must be greater than zero.'

        if self.unit_amount is not None and self.unit_amount < 0:
            errors['unit_amount'] = 'Unit amount must not be negative.'

        if self.line_total is not None and self.line_total < 0:
            errors['line_total'] = 'Line total must not be negative.'

        if (
            self.quantity is not None
            and self.unit_amount is not None
            and self.line_total is not None
            and self.line_total != self.unit_amount * self.quantity
        ):
            errors['line_total'] = 'Line total must equal unit_amount * quantity.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        item = self.product_name
        if self.variant_name:
            item = f'{item} / {self.variant_name}'
        return f'{item} x {self.quantity} ({self.order.order_number})'
