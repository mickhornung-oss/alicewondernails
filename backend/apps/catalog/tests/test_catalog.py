import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase, override_settings

from apps.catalog.models import (
    Product,
    ProductCategory,
    ProductImage,
    ProductVariant,
)


class ProductCategoryModelTest(TestCase):
    def test_category_can_be_created(self):
        category = ProductCategory.objects.create(name='Gel', slug='gel')

        self.assertEqual(str(category), 'Gel')
        self.assertTrue(category.is_active)

    def test_slug_is_unique(self):
        ProductCategory.objects.create(name='Gel', slug='gel')

        with self.assertRaises(IntegrityError):
            ProductCategory.objects.create(name='Gel 2', slug='gel')

    def test_parent_category_works(self):
        parent = ProductCategory.objects.create(name='Colors', slug='colors')
        child = ProductCategory.objects.create(
            name='Red',
            slug='red',
            parent=parent,
        )

        self.assertEqual(child.parent, parent)


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(name='Polish', slug='polish')

    def create_product(self, **overrides):
        data = {
            'category': self.category,
            'name': 'Wonder Red',
            'slug': 'wonder-red',
            'product_type': Product.ProductType.NAIL_POLISH,
            'visibility': Product.Visibility.PUBLIC,
        }
        data.update(overrides)
        return Product.objects.create(**data)

    def test_product_can_be_created(self):
        product = self.create_product(collection_name='Wonder Collection')

        self.assertEqual(str(product), 'Wonder Red')
        self.assertEqual(product.collection_name, 'Wonder Collection')

    def test_product_type_choices_work(self):
        choices = {choice for choice, label in Product.ProductType.choices}

        self.assertEqual(
            choices,
            {'nail_polish', 'gel', 'care', 'accessory', 'set', 'other'},
        )

    def test_visibility_choices_work(self):
        choices = {choice for choice, label in Product.Visibility.choices}

        self.assertEqual(choices, {'public', 'b2c_only', 'b2b_only', 'hidden'})

    def test_public_is_visible_for_b2c_and_b2b(self):
        product = self.create_product(visibility=Product.Visibility.PUBLIC)

        self.assertTrue(product.is_visible_for_b2c)
        self.assertTrue(product.is_visible_for_b2b)

    def test_b2c_only_is_only_visible_for_b2c(self):
        product = self.create_product(
            slug='b2c-product',
            visibility=Product.Visibility.B2C_ONLY,
        )

        self.assertTrue(product.is_visible_for_b2c)
        self.assertFalse(product.is_visible_for_b2b)

    def test_b2b_only_is_only_visible_for_b2b(self):
        product = self.create_product(
            slug='b2b-product',
            visibility=Product.Visibility.B2B_ONLY,
        )

        self.assertFalse(product.is_visible_for_b2c)
        self.assertTrue(product.is_visible_for_b2b)

    def test_hidden_is_not_visible(self):
        product = self.create_product(
            slug='hidden-product',
            visibility=Product.Visibility.HIDDEN,
        )

        self.assertFalse(product.is_visible_for_b2c)
        self.assertFalse(product.is_visible_for_b2b)

    def test_product_has_no_price_fields(self):
        field_names = {field.name for field in Product._meta.get_fields()}

        self.assertFalse({'price', 'b2c_price', 'b2b_price'} & field_names)


class ProductVariantModelTest(TestCase):
    def setUp(self):
        category = ProductCategory.objects.create(name='Gel', slug='gel')
        self.product = Product.objects.create(
            category=category,
            name='Wonder Gel',
            slug='wonder-gel',
            product_type=Product.ProductType.GEL,
        )

    def test_variant_can_be_created(self):
        variant = ProductVariant.objects.create(
            product=self.product,
            name='Ruby Red',
            sku='AWN-RUBY-001',
            color_name='Ruby Red',
            color_code='#AA0000',
            finish='glossy',
            size_label='10ml',
            is_default=True,
        )

        self.assertEqual(variant.sku, 'AWN-RUBY-001')
        self.assertEqual(variant.color_name, 'Ruby Red')
        self.assertEqual(variant.color_code, '#AA0000')
        self.assertTrue(variant.is_default)
        self.assertEqual(str(variant), 'Wonder Gel - Ruby Red')


class ProductImageModelTest(TestCase):
    def setUp(self):
        category = ProductCategory.objects.create(name='Care', slug='care')
        self.product = Product.objects.create(
            category=category,
            name='Wonder Care',
            slug='wonder-care',
            product_type=Product.ProductType.CARE,
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            name='Default',
            sku='AWN-CARE-001',
        )

    def test_product_image_can_be_created(self):
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                upload = SimpleUploadedFile(
                    'product.txt',
                    b'fake image content',
                    content_type='text/plain',
                )
                image = ProductImage.objects.create(
                    product=self.product,
                    image=upload,
                    alt_text='Wonder Care bottle',
                    is_primary=True,
                )

                self.assertEqual(image.product, self.product)
                self.assertIsNone(image.variant)
                self.assertTrue(image.is_primary)
                self.assertIn('Wonder Care', str(image))

    def test_product_image_can_reference_variant(self):
        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                upload = SimpleUploadedFile(
                    'variant.txt',
                    b'fake image content',
                    content_type='text/plain',
                )
                image = ProductImage.objects.create(
                    product=self.product,
                    variant=self.variant,
                    image=upload,
                    alt_text='Variant image',
                )

                self.assertEqual(image.variant, self.variant)
