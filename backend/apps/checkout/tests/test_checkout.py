import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
import uuid

from apps.checkout.models import CheckoutSession, CheckoutEvent
from apps.checkout.services import (
    CheckoutError,
    start_checkout,
    select_shipping_method,
    select_payment_method,
    build_legal_snapshot,
    build_consent_snapshot,
    validate_checkout,
    create_order_from_checkout,
    cancel_checkout,
    log_checkout_event
)
from apps.cart.models import Cart, CartItem
from apps.catalog.models import ProductCategory, Product, ProductVariant
from apps.pricing.models import ProductPrice
from apps.shipping.models import ShippingZone, ShippingMethod
from apps.payments.models import PaymentMethod
from apps.legal.models import LegalDocument, LegalDocumentVersion
from apps.consent.models import ConsentCategory, ConsentRecord

User = get_user_model()


class CheckoutSessionModelTest(TestCase):
    """Tests for CheckoutSession model."""

    def setUp(self):
        uid = uuid.uuid4().hex[:8]
        self.user = User.objects.create_user(
            username=f'testuser{uid}',
            email=f'test{uid}@example.com',
            password='testpass123'
        )
        self.cart = Cart.objects.create(
            user=self.user,
            customer_group='b2c',
            status='active'
        )

    def test_checkout_session_created(self):
        """Test CheckoutSession can be created."""
        checkout = CheckoutSession.objects.create(
            user=self.user,
            cart=self.cart,
            status='started'
        )
        assert checkout.pk is not None
        assert checkout.status == 'started'

    def test_status_default_started(self):
        """Test status defaults to started."""
        checkout = CheckoutSession.objects.create(
            user=self.user,
            cart=self.cart
        )
        assert checkout.status == 'started'

    def test_customer_group_default_b2c(self):
        """Test customer_group defaults to b2c."""
        checkout = CheckoutSession.objects.create(
            user=self.user,
            cart=self.cart
        )
        assert checkout.customer_group == 'b2c'

    def test_amounts_non_negative(self):
        """Test negative amounts are prevented by constraint."""
        checkout = CheckoutSession.objects.create(
            user=self.user,
            cart=self.cart,
            shipping_amount=Decimal('0.00'),
            cart_subtotal=Decimal('10.00'),
            order_total=Decimal('10.00')
        )
        assert checkout.shipping_amount >= 0
        assert checkout.cart_subtotal >= 0
        assert checkout.order_total >= 0

    def test_snapshots_store_dicts(self):
        """Test snapshots store JSON dicts."""
        snapshot_data = {'key': 'value', 'nested': {'data': 123}}
        checkout = CheckoutSession.objects.create(
            user=self.user,
            cart=self.cart,
            legal_snapshot=snapshot_data
        )
        assert checkout.legal_snapshot == snapshot_data
        assert isinstance(checkout.legal_snapshot, dict)

    def test_str_representation(self):
        """Test __str__ method."""
        checkout = CheckoutSession.objects.create(
            user=self.user,
            cart=self.cart
        )
        assert 'Checkout' in str(checkout)
        assert 'started' in str(checkout)


class CheckoutEventModelTest(TestCase):
    """Tests for CheckoutEvent model."""

    def setUp(self):
        uid = uuid.uuid4().hex[:8]
        self.user = User.objects.create_user(
            username=f'testuser{uid}',
            email=f'test{uid}@example.com'
        )
        self.cart = Cart.objects.create(user=self.user)
        self.checkout = CheckoutSession.objects.create(
            user=self.user,
            cart=self.cart
        )

    def test_event_created(self):
        """Test CheckoutEvent can be created."""
        event = CheckoutEvent.objects.create(
            checkout=self.checkout,
            event_type='started',
            message='Test event'
        )
        assert event.pk is not None
        assert event.event_type == 'started'

    def test_metadata_stores_dict(self):
        """Test metadata stores JSON dict."""
        meta = {'key': 'value', 'count': 42}
        event = CheckoutEvent.objects.create(
            checkout=self.checkout,
            event_type='validated',
            metadata=meta
        )
        assert event.metadata == meta

    def test_str_representation(self):
        """Test __str__ method."""
        event = CheckoutEvent.objects.create(
            checkout=self.checkout,
            event_type='started'
        )
        assert 'CheckoutEvent' in str(event)
        assert 'started' in str(event)

    def test_ordering_by_created_at(self):
        """Test events are ordered by -created_at."""
        event1 = CheckoutEvent.objects.create(
            checkout=self.checkout,
            event_type='started'
        )
        event2 = CheckoutEvent.objects.create(
            checkout=self.checkout,
            event_type='validated'
        )
        events = list(CheckoutEvent.objects.all())
        assert events[0].id == event2.id  # Newer first


class CheckoutServiceTest(TestCase):
    """Tests for checkout services."""

    def setUp(self):
        """Create fresh user and cart for each test."""
        uid = uuid.uuid4().hex[:8]
        self.user = User.objects.create_user(
            username=f'testuser{uid}',
            email=f'test{uid}@example.com',
            password='testpass123'
        )
        
        # Create product category, product, variant
        cat_slug = f'cat{uuid.uuid4().hex[:4]}'
        self.category = ProductCategory.objects.create(
            name='Test Category',
            slug=cat_slug
        )
        prod_slug = f'prod{uuid.uuid4().hex[:4]}'
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            slug=prod_slug
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku=f'TEST-{uuid.uuid4().hex[:6].upper()}',
            name='Test Variant'
        )

        # Create pricing
        ProductPrice.objects.create(
            product=self.product,
            variant=self.variant,
            customer_group='b2c',
            amount=Decimal('50.00')
        )

        # Create cart with item
        self.cart = Cart.objects.create(
            user=self.user,
            customer_group='b2c',
            status='active'
        )
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            variant=self.variant,
            quantity=1
        )

        # Create shipping zone and method
        zone_code = f'ZONE{uuid.uuid4().hex[:4].upper()}'
        self.zone = ShippingZone.objects.create(
            name='Test Zone',
            code=zone_code,
            countries=['DE'],
            is_active=True
        )
        self.shipping_method = ShippingMethod.objects.create(
            zone=self.zone,
            name='Standard',
            code=f'standard_{uuid.uuid4().hex[:6]}',
            customer_group='b2c',
            base_price=Decimal('5.00'),
            is_active=True
        )

        # Create payment method
        self.payment_method = PaymentMethod.objects.create(
            name='Manual',
            code=f'manual_{uuid.uuid4().hex[:6]}',
            provider='manual',
            customer_group='all',
            is_active=True
        )

    def test_start_checkout_creates_session(self):
        """Test start_checkout creates valid session."""
        checkout = start_checkout(self.cart, user=self.user)
        assert checkout.pk is not None
        assert checkout.status == 'started'
        assert checkout.cart == self.cart

    def test_start_checkout_requires_active_cart(self):
        """Test start_checkout rejects inactive cart."""
        self.cart.status = 'converted'
        self.cart.save()
        with pytest.raises(CheckoutError):
            start_checkout(self.cart)

    def test_start_checkout_requires_items(self):
        """Test start_checkout rejects empty cart."""
        uid = uuid.uuid4().hex[:8]
        user2 = User.objects.create_user(
            username=f'testuser{uid}',
            email=f'test{uid}@example.com'
        )
        cart2 = Cart.objects.create(user=user2, status='active')
        with pytest.raises(CheckoutError):
            start_checkout(cart2)

    def test_select_payment_method(self):
        """Test select_payment_method updates checkout."""
        checkout = start_checkout(self.cart)
        checkout = select_payment_method(checkout, self.payment_method.code)
        assert checkout.payment_method == self.payment_method
        assert checkout.payment_snapshot is not None

    def test_cancel_checkout_sets_status(self):
        """Test cancel_checkout sets status and timestamp."""
        checkout = start_checkout(self.cart)
        checkout = cancel_checkout(checkout, "User cancelled")
        assert checkout.status == 'cancelled'
        assert checkout.cancelled_at is not None

    def test_log_checkout_event_creates_event(self):
        """Test log_checkout_event creates event."""
        checkout = start_checkout(self.cart)
        event = log_checkout_event(
            checkout,
            'started',
            'Test message',
            metadata={'test': 'data'}
        )
        assert event.pk is not None
        assert event.checkout == checkout
        assert event.message == 'Test message'


class CreateOrderFromCheckoutAB12Test(TestCase):
    """Tests for AB 12: create_order_from_checkout with snapshots integration."""

    def setUp(self):
        """Set up test data with all required documents."""
        uid = uuid.uuid4().hex[:8]
        self.user = User.objects.create_user(
            username=f'testuser{uid}',
            email=f'test{uid}@example.com',
            password='testpass123'
        )
        
        # Create required legal documents for b2c checkout
        required_docs = [
            'terms_b2c',
            'privacy_policy',
            'withdrawal_b2c',
            'shipping_info',
            'payment_info'
        ]
        
        for doc_type in required_docs:
            doc = LegalDocument.objects.create(
                document_type=doc_type,
                target_group='b2c',
                title=f'Document {doc_type}',
                slug=f'doc-{doc_type}'
            )
            LegalDocumentVersion.objects.create(
                document=doc,
                version='1',
                content=f'Content for {doc_type}',
                status='active'
            )
        
        # Create product and cart
        category = ProductCategory.objects.create(name='Gel', slug='gel')
        product = Product.objects.create(
            category=category,
            name='Builder Gel',
            slug='builder-gel',
            product_type=Product.ProductType.GEL,
        )
        variant = ProductVariant.objects.create(
            product=product,
            name='Rose',
            sku='GEL-ROSE',
            color_name='Rose',
            color_code='#d98ca3',
        )
        ProductPrice.objects.create(
            product=product,
            variant=variant,
            customer_group=ProductPrice.CustomerGroup.B2C,
            amount=Decimal('50.00')
        )

        # Create cart with item
        self.cart = Cart.objects.create(
            user=self.user,
            customer_group='b2c',
            status='active'
        )
        CartItem.objects.create(
            cart=self.cart,
            product=product,
            variant=variant,
            quantity=1
        )

        # Create shipping zone and method
        zone_code = f'ZONE{uuid.uuid4().hex[:4].upper()}'
        zone = ShippingZone.objects.create(
            name='Test Zone',
            code=zone_code,
            countries=['DE'],
            is_active=True
        )
        self.shipping_method = ShippingMethod.objects.create(
            zone=zone,
            name='Standard',
            code=f'standard_{uuid.uuid4().hex[:6]}',
            customer_group='b2c',
            base_price=Decimal('5.00'),
            is_active=True
        )

        # Create payment method
        self.payment_method = PaymentMethod.objects.create(
            name='Manual',
            code=f'manual_{uuid.uuid4().hex[:6]}',
            provider='manual',
            customer_group='all',
            is_active=True
        )

    def test_create_order_from_checkout_transfers_snapshots(self):
        """Test create_order_from_checkout transfers snapshots to order."""
        # Setup complete checkout session
        checkout = start_checkout(self.cart, user=self.user)
        select_shipping_method(checkout, self.shipping_method.code)
        select_payment_method(checkout, self.payment_method.code)
        
        # Build snapshots
        legal_snapshot = build_legal_snapshot(customer_group='b2c')
        checkout.legal_snapshot = legal_snapshot
        checkout.save()

        # Validate checkout (calculates amounts)
        checkout = validate_checkout(checkout)

        # Create order from checkout
        order = create_order_from_checkout(checkout)

        # Verify order created
        assert order.pk is not None
        assert order.order_number is not None

        # Verify snapshots transferred to order
        assert order.shipping_amount == checkout.shipping_amount
        assert order.shipping_snapshot == checkout.shipping_snapshot
        assert order.payment_snapshot == checkout.payment_snapshot
        assert order.checkout_snapshot['checkout_id'] == checkout.pk

    def test_create_order_from_checkout_updates_checkout_status(self):
        """Test create_order_from_checkout sets checkout status."""
        checkout = start_checkout(self.cart, user=self.user)
        select_shipping_method(checkout, self.shipping_method.code)
        select_payment_method(checkout, self.payment_method.code)
        
        legal_snapshot = build_legal_snapshot(customer_group='b2c')
        checkout.legal_snapshot = legal_snapshot
        checkout.save()

        checkout = validate_checkout(checkout)
        create_order_from_checkout(checkout)

        checkout.refresh_from_db()
        assert checkout.status == 'order_created'
        assert checkout.order is not None
        assert checkout.order_created_at is not None

    def test_create_order_total_includes_shipping(self):
        """Test order total_amount includes shipping after create_order_from_checkout."""
        checkout = start_checkout(self.cart, user=self.user)
        select_shipping_method(checkout, self.shipping_method.code)
        select_payment_method(checkout, self.payment_method.code)
        
        legal_snapshot = build_legal_snapshot(customer_group='b2c')
        checkout.legal_snapshot = legal_snapshot
        checkout.save()

        checkout = validate_checkout(checkout)
        order = create_order_from_checkout(checkout)

        # Total amount should be subtotal + shipping
        expected_total = order.subtotal_amount + Decimal('5.00')
        assert order.total_amount == expected_total

    def test_create_order_from_checkout_requires_validation(self):
        """Test create_order_from_checkout requires validated checkout."""
        checkout = start_checkout(self.cart, user=self.user)
        
        # Try to create order from unvalidated checkout
        with pytest.raises(CheckoutError):
            create_order_from_checkout(checkout)

    def test_create_order_from_checkout_rolls_back_on_snapshot_failure(self):
        """
        AB 13: Test that checkout→order transition is fully atomic.
        
        When apply_checkout_snapshot_to_order fails, the entire transaction
        should rollback: no half-finished Order or Checkout status change.
        """
        from unittest.mock import patch
        from django.db import transaction
        
        checkout = start_checkout(self.cart, user=self.user)
        select_shipping_method(checkout, self.shipping_method.code)
        select_payment_method(checkout, self.payment_method.code)
        
        legal_snapshot = build_legal_snapshot(customer_group='b2c')
        checkout.legal_snapshot = legal_snapshot
        checkout.save()

        checkout = validate_checkout(checkout)
        original_checkout_id = checkout.id
        original_status = checkout.status
        
        # Get initial order count
        from apps.orders.models import Order
        initial_order_count = Order.objects.count()

        # Mock apply_checkout_snapshot_to_order (from apps.orders.services) to fail
        with patch('apps.orders.services.apply_checkout_snapshot_to_order') as mock_apply:
            mock_apply.side_effect = Exception("Snapshot application failed")
            
            # Try to create order
            with pytest.raises(CheckoutError):
                create_order_from_checkout(checkout)

        # After failure, verify rollback:
        # 1. Checkout status should still be 'validated', not 'order_created'
        checkout_after = CheckoutSession.objects.get(id=original_checkout_id)
        assert checkout_after.status == original_status, \
            f"Checkout status should remain '{original_status}' after failure, not '{checkout_after.status}'"
        
        # 2. Checkout.order should still be None
        assert checkout_after.order is None, \
            "Checkout.order should remain None after rollback"
        
        # 3. No new Order should be created (transaction rolled back)
        final_order_count = Order.objects.count()
        assert final_order_count == initial_order_count, \
            "No new Order should exist after rollback"


