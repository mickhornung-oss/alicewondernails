from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.cart.models import Cart
from apps.cart.services import add_item, get_or_create_cart
from apps.catalog.models import Product, ProductCategory, ProductVariant
from apps.customers.models import Address
from apps.orders.models import Order, OrderItem
from apps.orders.services import (
    OrderError,
    build_address_snapshot,
    cancel_order,
    create_order_from_cart,
    generate_order_number,
    recalculate_order_totals,
    apply_checkout_snapshot_to_order,
)
from apps.pricing.models import ProductPrice


User = get_user_model()


class OrdersTestBase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='order_user',
            email='order@example.local',
            password='orderpass1234',
        )
        self.category = ProductCategory.objects.create(
            name='Gel',
            slug='gel',
        )
        self.product = Product.objects.create(
            category=self.category,
            name='Builder Gel',
            slug='builder-gel',
            product_type=Product.ProductType.GEL,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            name='Rose',
            sku='GEL-ROSE',
            color_name='Rose',
            color_code='#d98ca3',
        )
        self.other_product = Product.objects.create(
            category=self.category,
            name='Top Coat',
            slug='top-coat',
            product_type=Product.ProductType.CARE,
        )
        self.billing_address = Address.objects.create(
            user=self.user,
            address_type=Address.AddressType.BILLING,
            full_name='Alice Wonder',
            street='Wonderstr. 1',
            postal_code='12345',
            city='Berlin',
            country='DE',
        )
        self.shipping_address = Address.objects.create(
            user=self.user,
            address_type=Address.AddressType.SHIPPING,
            full_name='Alice Wonder',
            street='Wonderstr. 1',
            postal_code='12345',
            city='Berlin',
            country='DE',
        )

    def _create_b2c_price(self, amount=Decimal('9.99'), variant=None):
        return ProductPrice.objects.create(
            product=self.product,
            variant=variant,
            customer_group=ProductPrice.CustomerGroup.B2C,
            amount=amount,
        )

    def _create_b2b_price(self, amount=Decimal('7.50'), variant=None):
        return ProductPrice.objects.create(
            product=self.product,
            variant=variant,
            customer_group=ProductPrice.CustomerGroup.B2B,
            amount=amount,
        )


class OrderModelTests(OrdersTestBase):
    def test_order_can_be_created(self):
        order = Order.objects.create(
            order_number='AWN-TEST-0001',
            user=self.user,
        )

        self.assertEqual(order.order_number, 'AWN-TEST-0001')
        self.assertEqual(order.status, Order.Status.DRAFT)
        self.assertEqual(order.customer_group, Order.CustomerGroup.B2C)
        self.assertEqual(order.currency, 'EUR')

    def test_order_number_is_unique(self):
        Order.objects.create(order_number='AWN-DUP-0001', user=self.user)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Order.objects.create(
                    order_number='AWN-DUP-0001',
                    user=self.user,
                )

    def test_default_status_is_draft(self):
        order = Order.objects.create(order_number='AWN-T-2', user=self.user)

        self.assertEqual(order.status, Order.Status.DRAFT)

    def test_default_customer_group_is_b2c(self):
        order = Order.objects.create(order_number='AWN-T-3', user=self.user)

        self.assertEqual(order.customer_group, Order.CustomerGroup.B2C)

    def test_subtotal_must_not_be_negative(self):
        order = Order(
            order_number='AWN-T-4',
            user=self.user,
            subtotal_amount=Decimal('-1.00'),
        )

        with self.assertRaises(ValidationError):
            order.full_clean()

    def test_total_must_not_be_negative(self):
        order = Order(
            order_number='AWN-T-5',
            user=self.user,
            total_amount=Decimal('-1.00'),
        )

        with self.assertRaises(ValidationError):
            order.full_clean()

    def test_str_is_meaningful(self):
        order = Order.objects.create(
            order_number='AWN-T-6',
            user=self.user,
            status=Order.Status.PLACED,
        )

        self.assertIn('AWN-T-6', str(order))
        self.assertIn('placed', str(order))


class OrderItemModelTests(OrdersTestBase):
    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            order_number='AWN-OI-1',
            user=self.user,
        )

    def test_order_item_can_be_created(self):
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_id_snapshot=self.product.id,
            product_name='Builder Gel',
            customer_group=OrderItem.CustomerGroup.B2C,
            quantity=2,
            unit_amount=Decimal('9.99'),
            line_total=Decimal('19.98'),
        )

        self.assertEqual(item.product_name, 'Builder Gel')
        self.assertEqual(item.quantity, 2)

    def test_quantity_must_be_positive(self):
        item = OrderItem(
            order=self.order,
            product_id_snapshot=self.product.id,
            product_name='X',
            customer_group=OrderItem.CustomerGroup.B2C,
            quantity=0,
            unit_amount=Decimal('1.00'),
            line_total=Decimal('0.00'),
        )

        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_unit_amount_must_not_be_negative(self):
        item = OrderItem(
            order=self.order,
            product_id_snapshot=self.product.id,
            product_name='X',
            customer_group=OrderItem.CustomerGroup.B2C,
            quantity=1,
            unit_amount=Decimal('-1.00'),
            line_total=Decimal('0.00'),
        )

        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_line_total_must_not_be_negative(self):
        item = OrderItem(
            order=self.order,
            product_id_snapshot=self.product.id,
            product_name='X',
            customer_group=OrderItem.CustomerGroup.B2C,
            quantity=1,
            unit_amount=Decimal('1.00'),
            line_total=Decimal('-1.00'),
        )

        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_snapshot_fields_are_persisted(self):
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            variant=self.variant,
            product_id_snapshot=self.product.id,
            variant_id_snapshot=self.variant.id,
            product_name='Builder Gel',
            variant_name='Rose',
            sku='GEL-ROSE',
            customer_group=OrderItem.CustomerGroup.B2C,
            quantity=1,
            unit_amount=Decimal('9.99'),
            line_total=Decimal('9.99'),
        )

        item.refresh_from_db()
        self.assertEqual(item.product_id_snapshot, self.product.id)
        self.assertEqual(item.variant_id_snapshot, self.variant.id)
        self.assertEqual(item.product_name, 'Builder Gel')
        self.assertEqual(item.variant_name, 'Rose')
        self.assertEqual(item.sku, 'GEL-ROSE')

    def test_str_is_meaningful(self):
        item = OrderItem.objects.create(
            order=self.order,
            product_id_snapshot=self.product.id,
            product_name='Builder Gel',
            variant_name='Rose',
            customer_group=OrderItem.CustomerGroup.B2C,
            quantity=3,
            unit_amount=Decimal('9.99'),
            line_total=Decimal('29.97'),
        )

        self.assertIn('Builder Gel', str(item))
        self.assertIn('Rose', str(item))
        self.assertIn('AWN-OI-1', str(item))


class GenerateOrderNumberTests(OrdersTestBase):
    def test_generate_order_number_unique(self):
        numbers = {generate_order_number() for _ in range(10)}

        self.assertEqual(len(numbers), 10)
        for number in numbers:
            self.assertTrue(number.startswith('AWN-'))


class BuildAddressSnapshotTests(OrdersTestBase):
    def test_with_address(self):
        snapshot = build_address_snapshot(self.billing_address)

        self.assertEqual(snapshot['full_name'], 'Alice Wonder')
        self.assertEqual(snapshot['street'], 'Wonderstr. 1')
        self.assertEqual(snapshot['postal_code'], '12345')
        self.assertEqual(snapshot['city'], 'Berlin')
        self.assertEqual(snapshot['country'], 'DE')

    def test_with_none_returns_defaults(self):
        snapshot = build_address_snapshot(None)

        self.assertEqual(snapshot['full_name'], '')
        self.assertEqual(snapshot['country'], 'DE')


class CreateOrderFromCartTests(OrdersTestBase):
    def test_creates_order_from_cart_with_b2c_price(self):
        self._create_b2c_price(amount=Decimal('9.99'))
        cart = get_or_create_cart(user=self.user)
        add_item(cart, self.product, quantity=2)

        order = create_order_from_cart(
            cart,
            billing_address=self.billing_address,
            shipping_address=self.shipping_address,
        )

        self.assertEqual(order.user, self.user)
        self.assertEqual(order.customer_group, Order.CustomerGroup.B2C)
        self.assertEqual(order.subtotal_amount, Decimal('19.98'))
        self.assertEqual(order.total_amount, Decimal('19.98'))
        self.assertEqual(order.item_count, 2)
        self.assertEqual(order.status, Order.Status.PLACED)
        self.assertIsNotNone(order.placed_at)
        self.assertEqual(order.billing_full_name, 'Alice Wonder')
        self.assertEqual(order.shipping_city, 'Berlin')
        self.assertEqual(order.items.count(), 1)

    def test_order_items_have_snapshots(self):
        self._create_b2c_price(amount=Decimal('9.99'), variant=self.variant)
        cart = get_or_create_cart(user=self.user)
        add_item(cart, self.product, variant=self.variant, quantity=2)

        order = create_order_from_cart(cart)
        item = order.items.first()

        self.assertEqual(item.product_id_snapshot, self.product.id)
        self.assertEqual(item.variant_id_snapshot, self.variant.id)
        self.assertEqual(item.product_name, 'Builder Gel')
        self.assertEqual(item.variant_name, 'Rose')
        self.assertEqual(item.sku, 'GEL-ROSE')
        self.assertEqual(item.unit_amount, Decimal('9.99'))
        self.assertEqual(item.line_total, Decimal('19.98'))

    def test_marks_cart_as_converted(self):
        self._create_b2c_price()
        cart = get_or_create_cart(user=self.user)
        add_item(cart, self.product, quantity=1)

        create_order_from_cart(cart)
        cart.refresh_from_db()

        self.assertEqual(cart.status, Cart.Status.CONVERTED)

    def test_uses_b2b_prices(self):
        self._create_b2b_price(amount=Decimal('7.50'))
        cart = get_or_create_cart(
            user=self.user,
            customer_group=Cart.CustomerGroup.B2B,
        )
        add_item(cart, self.product, quantity=2)

        order = create_order_from_cart(cart)

        self.assertEqual(order.customer_group, Order.CustomerGroup.B2B)
        self.assertEqual(order.subtotal_amount, Decimal('15.00'))
        self.assertEqual(order.items.first().unit_amount, Decimal('7.50'))

    def test_uses_variant_prices(self):
        self._create_b2c_price(amount=Decimal('9.99'))
        self._create_b2c_price(variant=self.variant, amount=Decimal('8.99'))
        cart = get_or_create_cart(user=self.user)
        add_item(cart, self.product, variant=self.variant, quantity=1)

        order = create_order_from_cart(cart)

        self.assertEqual(order.items.first().unit_amount, Decimal('8.99'))

    def test_fails_on_empty_cart(self):
        cart = get_or_create_cart(user=self.user)

        with self.assertRaises(OrderError):
            create_order_from_cart(cart)

    def test_fails_without_user(self):
        self._create_b2c_price()
        cart = Cart.objects.create(session_key='anon-1')
        add_item(cart, self.product, quantity=1)

        with self.assertRaises(OrderError):
            create_order_from_cart(cart)

    def test_later_price_change_does_not_alter_order_item(self):
        price = self._create_b2c_price(amount=Decimal('9.99'))
        cart = get_or_create_cart(user=self.user)
        add_item(cart, self.product, quantity=1)

        order = create_order_from_cart(cart)
        item = order.items.first()
        original_unit_amount = item.unit_amount
        original_line_total = item.line_total

        price.amount = Decimal('15.00')
        price.save(update_fields=['amount', 'updated_at'])
        item.refresh_from_db()

        self.assertEqual(item.unit_amount, original_unit_amount)
        self.assertEqual(item.line_total, original_line_total)


class RecalculateOrderTotalsTests(OrdersTestBase):
    def test_recalculates_totals(self):
        order = Order.objects.create(order_number='AWN-RC-1', user=self.user)
        OrderItem.objects.create(
            order=order,
            product_id_snapshot=self.product.id,
            product_name='Builder Gel',
            customer_group=OrderItem.CustomerGroup.B2C,
            quantity=2,
            unit_amount=Decimal('5.00'),
            line_total=Decimal('10.00'),
        )
        OrderItem.objects.create(
            order=order,
            product_id_snapshot=self.product.id,
            product_name='Builder Gel',
            customer_group=OrderItem.CustomerGroup.B2C,
            quantity=1,
            unit_amount=Decimal('3.00'),
            line_total=Decimal('3.00'),
        )

        recalculate_order_totals(order)
        order.refresh_from_db()

        self.assertEqual(order.subtotal_amount, Decimal('13.00'))
        self.assertEqual(order.total_amount, Decimal('13.00'))
        self.assertEqual(order.item_count, 3)


class CancelOrderTests(OrdersTestBase):
    def test_cancel_order_sets_status_and_keeps_snapshots(self):
        self._create_b2c_price()
        cart = get_or_create_cart(user=self.user)
        add_item(cart, self.product, quantity=1)
        order = create_order_from_cart(cart)
        item = order.items.first()
        original_unit = item.unit_amount
        original_total = item.line_total
        original_name = item.product_name

        cancel_order(order)
        order.refresh_from_db()
        item.refresh_from_db()

        self.assertEqual(order.status, Order.Status.CANCELLED)
        self.assertIsNotNone(order.cancelled_at)
        self.assertEqual(item.unit_amount, original_unit)
        self.assertEqual(item.line_total, original_total)
        self.assertEqual(item.product_name, original_name)


class OrderShippingSnapshotsTests(OrdersTestBase):
    """Tests for AB 12: Shipping/Payment Snapshots in Order."""

    def test_order_shipping_amount_default_zero(self):
        """Order shipping_amount defaults to 0.00."""
        order = Order.objects.create(
            order_number='AWN-SHIP-1',
            user=self.user,
        )
        self.assertEqual(order.shipping_amount, Decimal('0.00'))

    def test_order_shipping_amount_non_negative_constraint(self):
        """shipping_amount must not be negative."""
        order = Order(
            order_number='AWN-SHIP-2',
            user=self.user,
            shipping_amount=Decimal('-1.00'),
        )
        with self.assertRaises(ValidationError):
            order.full_clean()

    def test_order_shipping_snapshot_default_empty(self):
        """Order shipping_snapshot defaults to empty dict."""
        order = Order.objects.create(
            order_number='AWN-SHIP-3',
            user=self.user,
        )
        self.assertEqual(order.shipping_snapshot, {})

    def test_order_payment_snapshot_default_empty(self):
        """Order payment_snapshot defaults to empty dict."""
        order = Order.objects.create(
            order_number='AWN-SHIP-4',
            user=self.user,
        )
        self.assertEqual(order.payment_snapshot, {})

    def test_order_checkout_snapshot_default_empty(self):
        """Order checkout_snapshot defaults to empty dict."""
        order = Order.objects.create(
            order_number='AWN-SHIP-5',
            user=self.user,
        )
        self.assertEqual(order.checkout_snapshot, {})

    def test_recalculate_order_totals_with_shipping(self):
        """recalculate_order_totals includes shipping_amount in total_amount."""
        order = Order.objects.create(
            order_number='AWN-SHIP-6',
            user=self.user,
            shipping_amount=Decimal('5.99'),
        )
        OrderItem.objects.create(
            order=order,
            product_id_snapshot=self.product.id,
            product_name='Builder Gel',
            customer_group=OrderItem.CustomerGroup.B2C,
            quantity=2,
            unit_amount=Decimal('10.00'),
            line_total=Decimal('20.00'),
        )

        recalculate_order_totals(order)
        order.refresh_from_db()

        self.assertEqual(order.subtotal_amount, Decimal('20.00'))
        # AB 12: total_amount now includes shipping_amount
        self.assertEqual(order.total_amount, Decimal('25.99'))

    def test_apply_checkout_snapshot_to_order(self):
        """apply_checkout_snapshot_to_order transfers checkout data to order."""
        from apps.checkout.models import CheckoutSession
        from apps.cart.models import Cart

        # Create checkout session
        cart = get_or_create_cart(user=self.user)
        checkout = CheckoutSession.objects.create(
            user=self.user,
            cart=cart,
            status='validated',
            customer_group='b2c',
            currency='EUR',
            shipping_amount=Decimal('5.99'),
            shipping_snapshot={'method': 'DHL', 'code': 'dhl_express'},
            payment_snapshot={'method': 'Credit Card', 'code': 'cc'},
            cart_subtotal=Decimal('50.00'),
            order_total=Decimal('55.99'),
            item_count=5,
        )

        # Create order from cart
        self._create_b2c_price()
        add_item(cart, self.product, quantity=1)
        order = create_order_from_cart(cart)

        # Apply checkout snapshot
        apply_checkout_snapshot_to_order(order, checkout)
        order.refresh_from_db()

        # Verify snapshots transferred
        self.assertEqual(order.shipping_amount, Decimal('5.99'))
        self.assertEqual(order.shipping_snapshot['method'], 'DHL')
        self.assertEqual(order.payment_snapshot['method'], 'Credit Card')

        # Verify checkout_snapshot created
        self.assertEqual(order.checkout_snapshot['checkout_id'], checkout.pk)
        self.assertEqual(order.checkout_snapshot['customer_group'], 'b2c')
        self.assertEqual(order.checkout_snapshot['currency'], 'EUR')

        # Verify total_amount includes shipping
        self.assertEqual(
            order.total_amount,
            order.subtotal_amount + Decimal('5.99')
        )


class OrderAdminImmutabilityTests(TestCase):
    """AB 13: Tests for Order and OrderItem Admin read-only field protection."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='order_user',
            email='order@example.local',
            password='orderpass1234',
        )
        self.category = ProductCategory.objects.create(
            name='Gel',
            slug='gel',
        )
        self.product = Product.objects.create(
            category=self.category,
            name='Builder Gel',
            slug='builder-gel',
            product_type=Product.ProductType.GEL,
        )

    def test_order_admin_shipping_amount_readonly(self):
        """Verify shipping_amount is in OrderAdmin readonly_fields."""
        from apps.orders.admin import OrderAdmin
        admin_instance = OrderAdmin(Order, None)
        self.assertIn('shipping_amount', admin_instance.readonly_fields)

    def test_order_admin_shipping_snapshot_readonly(self):
        """Verify shipping_snapshot is in OrderAdmin readonly_fields."""
        from apps.orders.admin import OrderAdmin
        admin_instance = OrderAdmin(Order, None)
        self.assertIn('shipping_snapshot', admin_instance.readonly_fields)

    def test_order_admin_payment_snapshot_readonly(self):
        """Verify payment_snapshot is in OrderAdmin readonly_fields."""
        from apps.orders.admin import OrderAdmin
        admin_instance = OrderAdmin(Order, None)
        self.assertIn('payment_snapshot', admin_instance.readonly_fields)

    def test_order_admin_checkout_snapshot_readonly(self):
        """Verify checkout_snapshot is in OrderAdmin readonly_fields."""
        from apps.orders.admin import OrderAdmin
        admin_instance = OrderAdmin(Order, None)
        self.assertIn('checkout_snapshot', admin_instance.readonly_fields)

    def test_order_admin_total_amount_readonly(self):
        """Verify total_amount is in OrderAdmin readonly_fields."""
        from apps.orders.admin import OrderAdmin
        admin_instance = OrderAdmin(Order, None)
        self.assertIn('total_amount', admin_instance.readonly_fields)

    def test_order_item_admin_quantity_readonly(self):
        """Verify quantity is in OrderItemAdmin readonly_fields."""
        from apps.orders.admin import OrderItemAdmin
        admin_instance = OrderItemAdmin(OrderItem, None)
        self.assertIn('quantity', admin_instance.readonly_fields)

    def test_order_item_admin_snapshots_readonly(self):
        """Verify snapshot fields are in OrderItemAdmin readonly_fields."""
        from apps.orders.admin import OrderItemAdmin
        admin_instance = OrderItemAdmin(OrderItem, None)
        snapshot_fields = [
            'product_id_snapshot',
            'variant_id_snapshot',
            'price_id_snapshot',
        ]
        for field in snapshot_fields:
            self.assertIn(field, admin_instance.readonly_fields,
                         f"{field} should be readonly in OrderItemAdmin")

    def test_order_item_admin_price_fields_readonly(self):
        """Verify price fields are in OrderItemAdmin readonly_fields."""
        from apps.orders.admin import OrderItemAdmin
        admin_instance = OrderItemAdmin(OrderItem, None)
        price_fields = [
            'unit_amount',
            'line_total',
            'currency',
            'tax_rate',
            'price_includes_tax',
        ]
        for field in price_fields:
            self.assertIn(field, admin_instance.readonly_fields,
                         f"{field} should be readonly in OrderItemAdmin")
