from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.cart.models import Cart, CartItem
from apps.cart.services import (
    CartError,
    add_item,
    calculate_cart,
    clear_cart,
    get_or_create_cart,
    remove_item,
    update_item_quantity,
)
from apps.catalog.models import Product, ProductCategory, ProductVariant
from apps.pricing.models import ProductPrice


User = get_user_model()


class CartTestBase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='cart_user',
            email='cart@example.local',
            password='cartpass1234',
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


class CartModelTests(CartTestBase):
    def test_cart_for_user_can_be_created(self):
        cart = Cart.objects.create(user=self.user)

        self.assertEqual(cart.user, self.user)
        self.assertEqual(cart.customer_group, Cart.CustomerGroup.B2C)
        self.assertEqual(cart.status, Cart.Status.ACTIVE)
        self.assertEqual(cart.currency, 'EUR')

    def test_cart_with_session_key_can_be_created(self):
        cart = Cart.objects.create(session_key='abc123')

        self.assertIsNone(cart.user)
        self.assertEqual(cart.session_key, 'abc123')

    def test_cart_without_user_or_session_key_is_invalid(self):
        cart = Cart(user=None, session_key='')

        with self.assertRaises(ValidationError):
            cart.full_clean()

    def test_cart_default_customer_group_is_b2c(self):
        cart = Cart.objects.create(user=self.user)

        self.assertEqual(cart.customer_group, Cart.CustomerGroup.B2C)

    def test_cart_default_status_is_active(self):
        cart = Cart.objects.create(user=self.user)

        self.assertEqual(cart.status, Cart.Status.ACTIVE)

    def test_str_is_meaningful(self):
        cart = Cart.objects.create(user=self.user)

        self.assertIn('user=', str(cart))
        self.assertIn('b2c', str(cart))


class CartItemModelTests(CartTestBase):
    def setUp(self):
        super().setUp()
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_item_can_be_created(self):
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
        )

        self.assertEqual(item.cart, self.cart)
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 2)

    def test_quantity_default_is_one(self):
        item = CartItem.objects.create(cart=self.cart, product=self.product)

        self.assertEqual(item.quantity, 1)

    def test_quantity_zero_is_invalid(self):
        item = CartItem(cart=self.cart, product=self.product, quantity=0)

        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_variant_must_belong_to_product(self):
        item = CartItem(
            cart=self.cart,
            product=self.other_product,
            variant=self.variant,
        )

        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_duplicate_cart_product_variant_is_prevented(self):
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            variant=self.variant,
            quantity=1,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CartItem.objects.create(
                    cart=self.cart,
                    product=self.product,
                    variant=self.variant,
                    quantity=1,
                )

    def test_str_is_meaningful(self):
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            variant=self.variant,
            quantity=3,
        )

        self.assertEqual(str(item), 'Builder Gel / Rose x 3')


class CartServiceTests(CartTestBase):
    def test_get_or_create_cart_creates_new_active_cart(self):
        cart = get_or_create_cart(user=self.user)

        self.assertEqual(cart.user, self.user)
        self.assertEqual(cart.status, Cart.Status.ACTIVE)
        self.assertEqual(cart.customer_group, Cart.CustomerGroup.B2C)

    def test_get_or_create_cart_returns_existing_active_cart(self):
        first = get_or_create_cart(user=self.user)
        second = get_or_create_cart(user=self.user)

        self.assertEqual(first.pk, second.pk)

    def test_get_or_create_cart_with_session_key(self):
        cart = get_or_create_cart(session_key='sess-1')

        self.assertEqual(cart.session_key, 'sess-1')
        self.assertIsNone(cart.user)

    def test_get_or_create_cart_requires_user_or_session_key(self):
        with self.assertRaises(CartError):
            get_or_create_cart()

    def test_add_item_creates_new_position(self):
        cart = get_or_create_cart(user=self.user)
        item = add_item(cart, self.product, quantity=2)

        self.assertEqual(item.quantity, 2)
        self.assertEqual(cart.items.count(), 1)

    def test_add_item_increases_quantity_for_existing_position(self):
        cart = get_or_create_cart(user=self.user)
        add_item(cart, self.product, quantity=2)
        add_item(cart, self.product, quantity=3)

        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 5)

    def test_add_item_rejects_zero_quantity(self):
        cart = get_or_create_cart(user=self.user)

        with self.assertRaises(CartError):
            add_item(cart, self.product, quantity=0)

    def test_add_item_rejects_variant_not_belonging_to_product(self):
        cart = get_or_create_cart(user=self.user)

        with self.assertRaises(CartError):
            add_item(cart, self.other_product, variant=self.variant)

    def test_update_item_quantity_sets_quantity(self):
        cart = get_or_create_cart(user=self.user)
        item = add_item(cart, self.product, quantity=1)

        update_item_quantity(item, 7)
        item.refresh_from_db()

        self.assertEqual(item.quantity, 7)

    def test_update_item_quantity_zero_raises(self):
        cart = get_or_create_cart(user=self.user)
        item = add_item(cart, self.product, quantity=1)

        with self.assertRaises(CartError):
            update_item_quantity(item, 0)

    def test_remove_item_deletes_position(self):
        cart = get_or_create_cart(user=self.user)
        item = add_item(cart, self.product, quantity=1)

        remove_item(item)

        self.assertEqual(cart.items.count(), 0)

    def test_clear_cart_empties_cart(self):
        cart = get_or_create_cart(user=self.user)
        add_item(cart, self.product, quantity=1)
        add_item(cart, self.other_product, quantity=2)

        clear_cart(cart)

        self.assertEqual(cart.items.count(), 0)


class CartCalculationTests(CartTestBase):
    def _create_price(self, **overrides):
        data = {
            'product': self.product,
            'customer_group': ProductPrice.CustomerGroup.B2C,
            'amount': Decimal('9.99'),
        }
        data.update(overrides)
        return ProductPrice.objects.create(**data)

    def test_calculate_cart_with_b2c_price(self):
        self._create_price(amount=Decimal('9.99'))
        cart = get_or_create_cart(user=self.user)
        add_item(cart, self.product, quantity=2)

        result = calculate_cart(cart)

        self.assertEqual(result['customer_group'], Cart.CustomerGroup.B2C)
        self.assertEqual(result['currency'], 'EUR')
        self.assertEqual(result['item_count'], 2)
        self.assertEqual(result['subtotal'], Decimal('19.98'))
        self.assertEqual(len(result['lines']), 1)
        self.assertEqual(result['lines'][0]['unit_amount'], Decimal('9.99'))
        self.assertEqual(result['lines'][0]['line_total'], Decimal('19.98'))

    def test_calculate_cart_with_b2b_price(self):
        self._create_price(
            customer_group=ProductPrice.CustomerGroup.B2B,
            amount=Decimal('7.50'),
        )
        cart = get_or_create_cart(
            user=self.user,
            customer_group=Cart.CustomerGroup.B2B,
        )
        add_item(cart, self.product, quantity=3)

        result = calculate_cart(cart)

        self.assertEqual(result['customer_group'], Cart.CustomerGroup.B2B)
        self.assertEqual(result['subtotal'], Decimal('22.50'))

    def test_calculate_cart_prefers_variant_price(self):
        self._create_price(amount=Decimal('9.99'))
        self._create_price(variant=self.variant, amount=Decimal('8.99'))
        cart = get_or_create_cart(user=self.user)
        add_item(cart, self.product, variant=self.variant, quantity=2)

        result = calculate_cart(cart)

        self.assertEqual(result['lines'][0]['unit_amount'], Decimal('8.99'))
        self.assertEqual(result['subtotal'], Decimal('17.98'))

    def test_calculate_cart_falls_back_to_product_price(self):
        self._create_price(amount=Decimal('9.99'))
        cart = get_or_create_cart(user=self.user)
        add_item(cart, self.product, variant=self.variant, quantity=1)

        result = calculate_cart(cart)

        self.assertEqual(result['lines'][0]['unit_amount'], Decimal('9.99'))
        self.assertEqual(result['subtotal'], Decimal('9.99'))

    def test_calculate_cart_raises_when_price_missing(self):
        cart = get_or_create_cart(user=self.user)
        add_item(cart, self.product, quantity=1)

        with self.assertRaises(CartError):
            calculate_cart(cart)
