import secrets
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.cart.models import Cart
from apps.cart.services import calculate_cart
from apps.orders.models import Order, OrderItem


class OrderError(Exception):
    pass


def generate_order_number():
    today = timezone.now().strftime('%Y%m%d')
    for _ in range(20):
        suffix = secrets.token_hex(3).upper()
        candidate = f'AWN-{today}-{suffix}'
        if not Order.objects.filter(order_number=candidate).exists():
            return candidate
    raise OrderError('Could not generate unique order number after several attempts.')


def build_address_snapshot(address):
    if address is None:
        return {
            'full_name': '',
            'company': '',
            'street': '',
            'postal_code': '',
            'city': '',
            'country': 'DE',
        }

    return {
        'full_name': address.full_name,
        'company': address.company,
        'street': address.street,
        'postal_code': address.postal_code,
        'city': address.city,
        'country': address.country or 'DE',
    }


def _apply_address_snapshot(order, prefix, snapshot):
    setattr(order, f'{prefix}_full_name', snapshot.get('full_name', ''))
    setattr(order, f'{prefix}_company', snapshot.get('company', ''))
    setattr(order, f'{prefix}_street', snapshot.get('street', ''))
    setattr(order, f'{prefix}_postal_code', snapshot.get('postal_code', ''))
    setattr(order, f'{prefix}_city', snapshot.get('city', ''))
    setattr(order, f'{prefix}_country', snapshot.get('country', '') or 'DE')


@transaction.atomic
def create_order_from_cart(
    cart,
    user=None,
    billing_address=None,
    shipping_address=None,
    status=Order.Status.PLACED,
):
    if cart is None:
        raise OrderError('Cart is required.')

    order_user = user or cart.user
    if order_user is None:
        raise OrderError('Order requires a user.')

    if not cart.items.exists():
        raise OrderError('Cart has no items.')

    calculation = calculate_cart(cart)
    if not calculation['lines']:
        raise OrderError('Cart has no items.')

    billing_snapshot = build_address_snapshot(billing_address)
    shipping_snapshot = build_address_snapshot(shipping_address)

    order = Order(
        order_number=generate_order_number(),
        user=order_user,
        cart=cart,
        customer_group=cart.customer_group,
        status=status,
        currency=calculation['currency'],
        subtotal_amount=Decimal(calculation['subtotal']),
        total_amount=Decimal(calculation['subtotal']),
        item_count=calculation['item_count'],
    )
    _apply_address_snapshot(order, 'billing', billing_snapshot)
    _apply_address_snapshot(order, 'shipping', shipping_snapshot)
    if status == Order.Status.PLACED:
        order.placed_at = timezone.now()
    order.save()

    for line in calculation['lines']:
        snapshot = line['price_snapshot']
        sku = ''
        if line['variant_id']:
            try:
                sku = order.cart.items.select_related('variant').get(
                    pk=line['item_id']
                ).variant.sku or ''
            except Exception:
                sku = ''

        OrderItem.objects.create(
            order=order,
            product_id=snapshot['product_id'],
            variant_id=snapshot['variant_id'],
            price_id=snapshot['price_id'],
            product_id_snapshot=snapshot['product_id'],
            variant_id_snapshot=snapshot['variant_id'],
            price_id_snapshot=snapshot['price_id'],
            product_name=snapshot['product_name'],
            variant_name=snapshot['variant_name'],
            sku=sku,
            customer_group=snapshot['customer_group'],
            quantity=line['quantity'],
            unit_amount=Decimal(line['unit_amount']),
            line_total=Decimal(line['line_total']),
            currency=snapshot['currency'],
            tax_rate=Decimal(snapshot['tax_rate']),
            price_includes_tax=bool(snapshot['price_includes_tax']),
        )

    cart.status = Cart.Status.CONVERTED
    cart.save(update_fields=['status', 'updated_at'])

    return order


def recalculate_order_totals(order):
    items = order.items.all()
    subtotal = Decimal('0.00')
    item_count = 0
    for item in items:
        subtotal += item.line_total
        item_count += item.quantity

    order.subtotal_amount = subtotal
    # AB 12: Berechne total_amount inklusive Versand
    order.total_amount = subtotal + order.shipping_amount
    order.item_count = item_count
    order.save(update_fields=[
        'subtotal_amount',
        'total_amount',
        'item_count',
        'updated_at',
    ])
    return order


def apply_checkout_snapshot_to_order(order, checkout):
    """
    Apply checkout snapshots and amounts to order.
    
    Called after create_order_from_cart to capture final checkout state.
    
    Args:
        order: Order instance
        checkout: CheckoutSession instance
        
    Returns:
        Updated Order instance
    """
    order.shipping_amount = checkout.shipping_amount
    order.shipping_snapshot = checkout.shipping_snapshot or {}
    order.payment_snapshot = checkout.payment_snapshot or {}
    
    # Build checkout_snapshot with context
    order.checkout_snapshot = {
        'checkout_id': checkout.pk,
        'customer_group': checkout.customer_group,
        'currency': checkout.currency,
        'item_count': checkout.item_count,
        'cart_subtotal': str(checkout.cart_subtotal),
        'shipping_amount': str(checkout.shipping_amount),
        'order_total': str(checkout.order_total),
    }
    
    # Recalculate total_amount with shipping
    order.total_amount = order.subtotal_amount + order.shipping_amount
    
    order.save()
    return order


def cancel_order(order):
    order.status = Order.Status.CANCELLED
    order.cancelled_at = timezone.now()
    order.save(update_fields=['status', 'cancelled_at', 'updated_at'])
    return order
