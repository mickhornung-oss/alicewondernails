from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.catalog.models import Product, ProductVariant


class Cart(models.Model):
    class CustomerGroup(models.TextChoices):
        B2C = 'b2c', 'B2C'
        B2B = 'b2b', 'B2B'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        CONVERTED = 'converted', 'Converted'
        ABANDONED = 'abandoned', 'Abandoned'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts',
    )
    session_key = models.CharField(max_length=80, blank=True, default='')
    customer_group = models.CharField(
        max_length=8,
        choices=CustomerGroup.choices,
        default=CustomerGroup.B2C,
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    currency = models.CharField(max_length=3, default='EUR')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_at',)
        constraints = (
            models.CheckConstraint(
                condition=Q(user__isnull=False) | ~Q(session_key=''),
                name='cart_user_or_session_key_required',
            ),
            models.UniqueConstraint(
                fields=('user',),
                condition=Q(status='active') & Q(user__isnull=False),
                name='cart_one_active_per_user',
            ),
            models.UniqueConstraint(
                fields=('session_key',),
                condition=Q(status='active') & ~Q(session_key=''),
                name='cart_one_active_per_session_key',
            ),
        )

    def clean(self):
        if self.user_id is None and not self.session_key:
            raise ValidationError(
                'Cart requires either a user or a session_key.'
            )

    def __str__(self):
        if self.user_id:
            owner = f'user={self.user_id}'
        else:
            owner = f'session={self.session_key}'
        return f'Cart#{self.pk or "new"} {owner} {self.customer_group} {self.status}'


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='cart_items',
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='cart_items',
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created_at',)
        constraints = (
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name='cart_cartitem_quantity_positive',
            ),
            models.UniqueConstraint(
                fields=('cart', 'product', 'variant'),
                name='cart_cartitem_unique_product_variant',
            ),
        )

    def clean(self):
        errors = {}

        if self.quantity is not None and self.quantity <= 0:
            errors['quantity'] = 'Quantity must be greater than zero.'

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
        return f'{item} x {self.quantity}'
