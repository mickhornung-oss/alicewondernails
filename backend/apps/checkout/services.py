from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from .models import CheckoutSession, CheckoutEvent
from apps.cart.models import Cart
from apps.shipping.services import get_shipping_method, build_shipping_snapshot
from apps.payments.services import get_payment_method, build_payment_method_snapshot
from apps.legal.services import get_active_document_version
from apps.consent.services import get_latest_consent


class CheckoutError(Exception):
    """Raised when checkout validation or operations fail."""
    pass


def start_checkout(cart, user=None, expires_at=None):
    """
    Start a new checkout session.

    Args:
        cart: Cart instance (must be active with items)
        user: User instance (optional, used if cart.user is None)
        expires_at: Optional expiration datetime

    Returns:
        CheckoutSession instance

    Raises:
        CheckoutError: If cart is invalid or user is missing
    """
    if not cart or cart.status != 'active':
        raise CheckoutError("Cart must be active")

    # Check if cart has items
    item_count = cart.items.count()
    if item_count == 0:
        raise CheckoutError("Cart must have at least one item")

    # Determine user
    if user is None:
        user = cart.user
    if user is None:
        raise CheckoutError("Cart must have associated user or user must be provided")

    # Get customer_group and currency from cart
    customer_group = getattr(cart, 'customer_group', 'b2c')
    currency = getattr(cart, 'currency', 'EUR')

    # Create checkout session
    checkout = CheckoutSession.objects.create(
        user=user,
        cart=cart,
        status='started',
        customer_group=customer_group,
        currency=currency,
        expires_at=expires_at
    )

    # Log event
    log_checkout_event(checkout, 'started', 'Checkout session started')

    return checkout


def select_shipping_method(checkout, shipping_method_code, country_code="DE"):
    """
    Select and set shipping method for checkout.

    Args:
        checkout: CheckoutSession instance
        shipping_method_code: Code of ShippingMethod
        country_code: Country code (default "DE")

    Returns:
        Updated CheckoutSession

    Raises:
        CheckoutError: If method not found or incompatible
    """
    try:
        shipping_method = get_shipping_method(
            shipping_method_code,
            country_code=country_code,
            customer_group=checkout.customer_group
        )
    except Exception as e:
        raise CheckoutError(f"Failed to get shipping method: {str(e)}")

    # Build snapshot as dict (not ShippingRateSnapshot object)
    snapshot = {
        'method_code': shipping_method.code,
        'method_name': shipping_method.name,
        'zone_code': shipping_method.zone.code,
        'zone_name': shipping_method.zone.name,
        'customer_group': checkout.customer_group,
        'amount': str(shipping_method.base_price),
        'currency': shipping_method.currency,
    }

    # Update checkout
    checkout.shipping_method = shipping_method
    checkout.shipping_snapshot = snapshot
    checkout.shipping_amount = shipping_method.base_price
    checkout.save()

    # Log event
    log_checkout_event(
        checkout,
        'shipping_selected',
        f'Shipping method selected: {shipping_method_code}',
        metadata={'shipping_method_code': shipping_method_code}
    )

    return checkout


def select_payment_method(checkout, payment_method_code):
    """
    Select and set payment method for checkout.

    Args:
        checkout: CheckoutSession instance
        payment_method_code: Code of PaymentMethod

    Returns:
        Updated CheckoutSession

    Raises:
        CheckoutError: If method not found or incompatible
    """
    try:
        payment_method = get_payment_method(
            payment_method_code,
            customer_group=checkout.customer_group
        )
    except Exception as e:
        raise CheckoutError(f"Failed to get payment method: {str(e)}")

    # Build snapshot
    try:
        snapshot = build_payment_method_snapshot(
            payment_method,
            customer_group=checkout.customer_group
        )
    except Exception as e:
        raise CheckoutError(f"Failed to build payment snapshot: {str(e)}")

    # Update checkout
    checkout.payment_method = payment_method
    checkout.payment_snapshot = snapshot
    checkout.save()

    # Log event
    log_checkout_event(
        checkout,
        'payment_selected',
        f'Payment method selected: {payment_method_code}',
        metadata={'payment_method_code': payment_method_code}
    )

    return checkout


def build_legal_snapshot(customer_group="b2c"):
    """
    Build snapshot of active legal documents required for checkout.

    Args:
        customer_group: 'b2c' or 'b2b'

    Returns:
        dict with document snapshots

    Raises:
        CheckoutError: If required documents are missing
    """
    # Determine required document types based on customer group
    if customer_group == 'b2c':
        required_types = [
            'terms_b2c',
            'privacy_policy',
            'withdrawal_b2c',
            'shipping_info',
            'payment_info'
        ]
    elif customer_group == 'b2b':
        required_types = [
            'terms_b2b',
            'privacy_policy',
            'shipping_info',
            'payment_info'
        ]
    else:
        raise CheckoutError(f"Invalid customer_group: {customer_group}")

    snapshot = {}
    missing = []

    for doc_type in required_types:
        try:
            version = get_active_document_version(doc_type, customer_group)
            if version:
                snapshot[doc_type] = {
                    'document_type': doc_type,
                    'target_group': customer_group,
                    'title': version.document.title,
                    'version': version.version,
                    'version_id': version.id,
                    'effective_from': version.effective_from.isoformat() if version.effective_from else None,
                }
            else:
                missing.append(doc_type)
        except Exception as e:
            missing.append(doc_type)

    if missing:
        raise CheckoutError(
            f"Required legal documents missing for {customer_group}: {', '.join(missing)}"
        )

    return snapshot


def build_consent_snapshot(user=None, session_key=None):
    """
    Build snapshot of current consent records.

    Args:
        user: User instance (optional)
        session_key: Session key for anonymous users (optional)

    Returns:
        dict with consent snapshots or empty dict if no records
    """
    snapshot = {}

    if user:
        try:
            records = get_latest_consent(user=user)
            for category_key, record in records.items():
                if record:
                    snapshot[category_key] = {
                        'category_key': category_key,
                        'granted': record.granted,
                        'consent_version': record.consent_version,
                        'record_id': record.id,
                        'created_at': record.created_at.isoformat() if record.created_at else None,
                    }
        except Exception:
            pass

    elif session_key:
        try:
            records = get_latest_consent(session_key=session_key)
            for category_key, record in records.items():
                if record:
                    snapshot[category_key] = {
                        'category_key': category_key,
                        'granted': record.granted,
                        'consent_version': record.consent_version,
                        'record_id': record.id,
                        'created_at': record.created_at.isoformat() if record.created_at else None,
                    }
        except Exception:
            pass

    return snapshot


def validate_checkout(checkout):
    """
    Validate checkout and calculate totals.

    Args:
        checkout: CheckoutSession instance

    Returns:
        Updated CheckoutSession

    Raises:
        CheckoutError: If validation fails
    """
    # Verify cart exists and is active
    if not checkout.cart or checkout.cart.status != 'active':
        raise CheckoutError("Cart must be active")

    # Verify cart is not empty
    item_count = checkout.cart.items.count()
    if item_count == 0:
        raise CheckoutError("Cart must not be empty")

    # Verify shipping method selected
    if not checkout.shipping_method:
        raise CheckoutError("Shipping method must be selected")

    # Verify payment method selected
    if not checkout.payment_method:
        raise CheckoutError("Payment method must be selected")

    # Verify snapshots exist
    if not checkout.shipping_snapshot:
        raise CheckoutError("Shipping snapshot must be present")

    if not checkout.payment_snapshot:
        raise CheckoutError("Payment snapshot must be present")

    if not checkout.legal_snapshot:
        raise CheckoutError("Legal snapshot must be present")

    # Calculate cart totals
    try:
        from apps.cart.services import calculate_cart
        cart_data = calculate_cart(checkout.cart)
    except Exception as e:
        raise CheckoutError(f"Failed to calculate cart: {str(e)}")

    # Build/update consent snapshot if user present
    if checkout.user:
        checkout.consent_snapshot = build_consent_snapshot(user=checkout.user)

    # Update totals
    checkout.cart_subtotal = Decimal(str(cart_data.get('subtotal', 0)))
    checkout.shipping_amount = Decimal(str(checkout.shipping_amount or 0))
    checkout.order_total = checkout.cart_subtotal + checkout.shipping_amount
    checkout.item_count = item_count

    # Update status
    checkout.status = 'validated'
    checkout.validated_at = timezone.now()
    checkout.save()

    # Log event
    log_checkout_event(
        checkout,
        'validated',
        'Checkout validated successfully',
        metadata={
            'subtotal': str(checkout.cart_subtotal),
            'shipping': str(checkout.shipping_amount),
            'total': str(checkout.order_total),
            'items': checkout.item_count
        }
    )

    return checkout


def create_order_from_checkout(checkout):
    """
    Create an Order from a validated Checkout.
    
    This operation is fully atomic: either the entire checkout→order transition
    succeeds, or it fails and rolls back completely with no partial state.

    Args:
        checkout: Validated CheckoutSession instance

    Returns:
        Order instance

    Raises:
        CheckoutError: If checkout not validated or order creation fails
    """
    # AB 13: Wrap entire operation in transaction.atomic for data consistency
    with transaction.atomic():
        # Get fresh checkout instance with pessimistic lock to prevent concurrent access
        checkout = CheckoutSession.objects.select_for_update().get(pk=checkout.pk)
        
        if checkout.status != 'validated':
            raise CheckoutError("Checkout must be validated before creating order")

        try:
            from apps.orders.services import create_order_from_cart, apply_checkout_snapshot_to_order
            from apps.auditlog.services import create_audit_log

            # Create order from cart
            order = create_order_from_cart(checkout.cart, user=checkout.user)

            # AB 12: Apply checkout snapshots and amounts to order
            apply_checkout_snapshot_to_order(order, checkout)

            # Link order to checkout
            checkout.order = order
            checkout.status = 'order_created'
            checkout.order_created_at = timezone.now()
            checkout.save()

            # Log checkout event
            log_checkout_event(
                checkout,
                'order_created',
                f'Order created: {order.order_number}',
                metadata={'order_id': order.id, 'order_number': order.order_number}
            )

            # Create audit log if possible
            try:
                create_audit_log(
                    action='order_created_from_checkout',
                    entity=order,
                    message=f'Order {order.order_number} created from checkout session {checkout.id}',
                    changes=None
                )
            except Exception:
                pass  # Audit logging is optional

            return order

        except Exception as e:
            # Transaction will automatically rollback on exception
            raise CheckoutError(f"Failed to create order: {str(e)}")


def cancel_checkout(checkout, message=""):
    """
    Cancel a checkout session.

    Args:
        checkout: CheckoutSession instance
        message: Optional cancellation message

    Returns:
        Updated CheckoutSession
    """
    checkout.status = 'cancelled'
    checkout.cancelled_at = timezone.now()
    checkout.save()

    # Log event
    log_checkout_event(
        checkout,
        'cancelled',
        message or 'Checkout cancelled',
    )

    return checkout


def log_checkout_event(checkout, event_type, message="", metadata=None):
    """
    Log a checkout event.

    Args:
        checkout: CheckoutSession instance
        event_type: Type of event
        message: Optional message
        metadata: Optional metadata dict

    Returns:
        CheckoutEvent instance
    """
    if metadata is None:
        metadata = {}

    event = CheckoutEvent.objects.create(
        checkout=checkout,
        event_type=event_type,
        message=message,
        metadata=metadata
    )

    return event
