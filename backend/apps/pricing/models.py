from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from apps.catalog.models import Product, ProductVariant


class ProductPrice(models.Model):
    class CustomerGroup(models.TextChoices):
        B2C = 'b2c', 'B2C'
        B2B = 'b2b', 'B2B'

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='prices',
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='prices',
    )
    customer_group = models.CharField(
        max_length=8,
        choices=CustomerGroup.choices,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    currency = models.CharField(max_length=3, default='EUR')
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('19.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    price_includes_tax = models.BooleanField(default=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('product', 'variant', 'customer_group')
        constraints = (
            models.CheckConstraint(
                condition=Q(amount__gte=0),
                name='pricing_productprice_amount_non_negative',
            ),
            models.CheckConstraint(
                condition=Q(tax_rate__gte=0),
                name='pricing_productprice_tax_rate_non_negative',
            ),
        )

    def clean(self):
        errors = {}

        if (
            self.valid_from
            and self.valid_until
            and self.valid_until < self.valid_from
        ):
            errors['valid_until'] = 'valid_until must not be before valid_from.'

        if (
            self.variant_id
            and self.product_id
            and self.variant.product_id != self.product_id
        ):
            errors['variant'] = 'Variant must belong to the selected product.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        item = self.product.name
        if self.variant_id:
            item = f'{item} / {self.variant.name}'
        return f'{item} - {self.customer_group} - {self.amount} {self.currency}'
