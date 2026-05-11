from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.catalog.models import Product, ProductCategory, ProductVariant
from apps.pricing.models import ProductPrice
from apps.pricing.services import (
    PriceNotFound,
    build_price_snapshot,
    get_active_price,
)


class PricingTestCase(TestCase):
    def setUp(self):
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

    def create_price(self, **overrides):
        data = {
            'product': self.product,
            'customer_group': ProductPrice.CustomerGroup.B2C,
            'amount': Decimal('9.99'),
        }
        data.update(overrides)
        return ProductPrice.objects.create(**data)


class ProductPriceModelTests(PricingTestCase):
    def test_b2c_price_can_be_created(self):
        price = self.create_price(customer_group=ProductPrice.CustomerGroup.B2C)

        self.assertEqual(price.customer_group, ProductPrice.CustomerGroup.B2C)
        self.assertEqual(price.amount, Decimal('9.99'))

    def test_b2b_price_can_be_created(self):
        price = self.create_price(
            customer_group=ProductPrice.CustomerGroup.B2B,
            amount=Decimal('7.50'),
        )

        self.assertEqual(price.customer_group, ProductPrice.CustomerGroup.B2B)
        self.assertEqual(price.amount, Decimal('7.50'))

    def test_product_price_can_be_created(self):
        price = self.create_price()

        self.assertEqual(price.product, self.product)
        self.assertIsNone(price.variant)

    def test_variant_price_can_be_created(self):
        price = self.create_price(variant=self.variant)

        self.assertEqual(price.product, self.product)
        self.assertEqual(price.variant, self.variant)

    def test_amount_must_not_be_negative(self):
        price = ProductPrice(
            product=self.product,
            customer_group=ProductPrice.CustomerGroup.B2C,
            amount=Decimal('-0.01'),
        )

        with self.assertRaises(ValidationError):
            price.full_clean()

    def test_tax_rate_must_not_be_negative(self):
        price = ProductPrice(
            product=self.product,
            customer_group=ProductPrice.CustomerGroup.B2C,
            amount=Decimal('9.99'),
            tax_rate=Decimal('-1.00'),
        )

        with self.assertRaises(ValidationError):
            price.full_clean()

    def test_valid_until_before_valid_from_is_invalid(self):
        now = timezone.now()
        price = ProductPrice(
            product=self.product,
            customer_group=ProductPrice.CustomerGroup.B2C,
            amount=Decimal('9.99'),
            valid_from=now,
            valid_until=now - timezone.timedelta(days=1),
        )

        with self.assertRaises(ValidationError):
            price.full_clean()

    def test_variant_must_belong_to_product(self):
        other_product = Product.objects.create(
            category=self.category,
            name='Top Coat',
            slug='top-coat',
            product_type=Product.ProductType.CARE,
        )
        price = ProductPrice(
            product=other_product,
            variant=self.variant,
            customer_group=ProductPrice.CustomerGroup.B2C,
            amount=Decimal('9.99'),
        )

        with self.assertRaises(ValidationError):
            price.full_clean()

    def test_str_is_meaningful(self):
        price = self.create_price(
            variant=self.variant,
            customer_group=ProductPrice.CustomerGroup.B2B,
            amount=Decimal('7.50'),
        )

        self.assertEqual(str(price), 'Builder Gel / Rose - b2b - 7.50 EUR')

    def test_catalog_models_do_not_get_price_fields(self):
        product_fields = {field.name for field in Product._meta.fields}
        variant_fields = {field.name for field in ProductVariant._meta.fields}

        self.assertFalse({'price', 'b2c_price', 'b2b_price'} & product_fields)
        self.assertFalse({'price', 'b2c_price', 'b2b_price'} & variant_fields)


class PricingServiceTests(PricingTestCase):
    def test_get_active_price_finds_b2c_product_price(self):
        price = self.create_price(customer_group=ProductPrice.CustomerGroup.B2C)

        result = get_active_price(
            self.product,
            ProductPrice.CustomerGroup.B2C,
        )

        self.assertEqual(result, price)

    def test_get_active_price_finds_b2b_product_price(self):
        price = self.create_price(
            customer_group=ProductPrice.CustomerGroup.B2B,
            amount=Decimal('7.50'),
        )

        result = get_active_price(
            self.product,
            ProductPrice.CustomerGroup.B2B,
        )

        self.assertEqual(result, price)

    def test_variant_specific_price_is_preferred(self):
        product_price = self.create_price(amount=Decimal('9.99'))
        variant_price = self.create_price(
            variant=self.variant,
            amount=Decimal('8.99'),
        )

        result = get_active_price(
            self.product,
            ProductPrice.CustomerGroup.B2C,
            variant=self.variant,
        )

        self.assertNotEqual(result, product_price)
        self.assertEqual(result, variant_price)

    def test_falls_back_to_product_price_without_variant_price(self):
        price = self.create_price(amount=Decimal('9.99'))

        result = get_active_price(
            self.product,
            ProductPrice.CustomerGroup.B2C,
            variant=self.variant,
        )

        self.assertEqual(result, price)

    def test_inactive_price_is_ignored(self):
        self.create_price(is_active=False)

        with self.assertRaises(PriceNotFound):
            get_active_price(self.product, ProductPrice.CustomerGroup.B2C)

    def test_price_outside_validity_period_is_ignored(self):
        now = timezone.now()
        self.create_price(
            valid_from=now - timezone.timedelta(days=10),
            valid_until=now - timezone.timedelta(days=1),
        )

        with self.assertRaises(PriceNotFound):
            get_active_price(
                self.product,
                ProductPrice.CustomerGroup.B2C,
                at=now,
            )

    def test_price_not_found_is_raised_when_no_price_exists(self):
        with self.assertRaises(PriceNotFound):
            get_active_price(self.product, ProductPrice.CustomerGroup.B2C)

    def test_newer_valid_price_is_preferred(self):
        now = timezone.now()
        older = self.create_price(
            amount=Decimal('9.99'),
            valid_from=now - timezone.timedelta(days=10),
        )
        newer = self.create_price(
            amount=Decimal('8.99'),
            valid_from=now - timezone.timedelta(days=1),
        )

        result = get_active_price(
            self.product,
            ProductPrice.CustomerGroup.B2C,
            at=now,
        )

        self.assertNotEqual(result, older)
        self.assertEqual(result, newer)

    def test_build_price_snapshot_contains_expected_fields(self):
        price = self.create_price(
            variant=self.variant,
            customer_group=ProductPrice.CustomerGroup.B2B,
            amount=Decimal('7.50'),
        )

        snapshot = build_price_snapshot(price)

        self.assertEqual(snapshot['product_id'], self.product.id)
        self.assertEqual(snapshot['variant_id'], self.variant.id)
        self.assertEqual(snapshot['product_name'], 'Builder Gel')
        self.assertEqual(snapshot['variant_name'], 'Rose')
        self.assertEqual(snapshot['customer_group'], ProductPrice.CustomerGroup.B2B)
        self.assertEqual(snapshot['amount'], Decimal('7.50'))
        self.assertEqual(snapshot['currency'], 'EUR')
        self.assertEqual(snapshot['tax_rate'], Decimal('19.00'))
        self.assertTrue(snapshot['price_includes_tax'])
        self.assertEqual(snapshot['price_id'], price.id)
