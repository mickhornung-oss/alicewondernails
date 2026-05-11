from django.db.models import F, Q
from django.utils import timezone

from apps.pricing.models import ProductPrice


class PriceNotFound(Exception):
    pass


def get_active_price(product, customer_group, variant=None, at=None):
    at = at or timezone.now()

    base_queryset = ProductPrice.objects.filter(
        product=product,
        customer_group=customer_group,
        is_active=True,
    ).filter(
        Q(valid_from__isnull=True) | Q(valid_from__lte=at),
        Q(valid_until__isnull=True) | Q(valid_until__gte=at),
    )

    if variant is not None:
        variant_price = (
            base_queryset.filter(variant=variant)
            .order_by(F('valid_from').desc(nulls_last=True), '-created_at', '-id')
            .first()
        )
        if variant_price is not None:
            return variant_price

    product_price = (
        base_queryset.filter(variant__isnull=True)
        .order_by(F('valid_from').desc(nulls_last=True), '-created_at', '-id')
        .first()
    )
    if product_price is not None:
        return product_price

    raise PriceNotFound('No active price found.')


def build_price_snapshot(price):
    return {
        'product_id': price.product_id,
        'variant_id': price.variant_id,
        'product_name': price.product.name,
        'variant_name': price.variant.name if price.variant_id else '',
        'customer_group': price.customer_group,
        'amount': price.amount,
        'currency': price.currency,
        'tax_rate': price.tax_rate,
        'price_includes_tax': price.price_includes_tax,
        'price_id': price.id,
    }
