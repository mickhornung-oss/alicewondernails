from decimal import Decimal

from django.db import transaction

from apps.cart.models import Cart, CartItem
from apps.pricing.services import (
    PriceNotFound,
    build_price_snapshot,
    get_active_price,
)


class CartError(Exception):
    pass


def get_or_create_cart(user=None, session_key=None, customer_group=Cart.CustomerGroup.B2C):
    if user is None and not session_key:
        raise CartError('Cart requires either a user or a session_key.')

    lookup = {'status': Cart.Status.ACTIVE}
    if user is not None:
        lookup['user'] = user
    else:
        lookup['user__isnull'] = True
        lookup['session_key'] = session_key

    cart = Cart.objects.filter(**lookup).order_by('-updated_at').first()
    if cart is not None:
        return cart

    create_kwargs = {
        'status': Cart.Status.ACTIVE,
        'customer_group': customer_group,
    }
    if user is not None:
        create_kwargs['user'] = user
    if session_key:
        create_kwargs['session_key'] = session_key

    return Cart.objects.create(**create_kwargs)


@transaction.atomic
def add_item(cart, product, variant=None, quantity=1):
    if quantity is None or quantity <= 0:
        raise CartError('Quantity must be greater than zero.')

    if variant is not None and variant.product_id != product.id:
        raise CartError('Variant must belong to the selected product.')

    item = (
        CartItem.objects.select_for_update()
        .filter(cart=cart, product=product, variant=variant)
        .first()
    )
    if item is not None:
        item.quantity += quantity
        item.save(update_fields=['quantity', 'updated_at'])
        return item

    return CartItem.objects.create(
        cart=cart,
        product=product,
        variant=variant,
        quantity=quantity,
    )


def update_item_quantity(item, quantity):
    if quantity is None or quantity <= 0:
        raise CartError('Quantity must be greater than zero.')

    item.quantity = quantity
    item.save(update_fields=['quantity', 'updated_at'])
    return item


def remove_item(item):
    item.delete()


def clear_cart(cart):
    cart.items.all().delete()


def calculate_cart(cart):
    lines = []
    subtotal = Decimal('0.00')
    currency = cart.currency
    item_count = 0

    items = cart.items.select_related('product', 'variant').order_by('created_at')

    for item in items:
        try:
            price = get_active_price(
                product=item.product,
                customer_group=cart.customer_group,
                variant=item.variant,
            )
        except PriceNotFound as exc:
            raise CartError(
                f'No active price for cart item {item.pk} '
                f'(product={item.product_id}, variant={item.variant_id}).'
            ) from exc

        snapshot = build_price_snapshot(price)
        unit_amount = Decimal(snapshot['amount'])
        line_total = unit_amount * item.quantity
        subtotal += line_total
        item_count += item.quantity
        currency = snapshot['currency']

        lines.append({
            'item_id': item.pk,
            'product_id': item.product_id,
            'variant_id': item.variant_id,
            'quantity': item.quantity,
            'unit_amount': unit_amount,
            'line_total': line_total,
            'price_snapshot': snapshot,
        })

    return {
        'cart_id': cart.pk,
        'customer_group': cart.customer_group,
        'currency': currency,
        'item_count': item_count,
        'subtotal': subtotal,
        'lines': lines,
    }
