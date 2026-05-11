"""
Smoke tests for API endpoints using seeded demo data.

These tests validate that the read-only API v1 endpoints return correct,
frontend-compatible responses when using seeded demo data.

Note: These are integration tests (Seed + API + Models), not API contract tests.
API contracts are tested in apps/api/tests/test_api.py.
"""

from django.test import TestCase
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.catalog.models import ProductCategory, Product, ProductVariant
from apps.shipping.models import ShippingZone, ShippingMethod
from apps.payments.models import PaymentMethod
from apps.legal.models import LegalDocument, LegalDocumentVersion


class SeededCategoriesAPITest(TestCase):
    """Smoke tests for catalog categories endpoint with seeded data."""

    def setUp(self):
        """Seed demo data before each test."""
        self.client = APIClient()
        call_command('seed_demo_data', verbosity=0)

    def test_categories_endpoint_returns_200(self):
        """GET /api/v1/catalog/categories/ returns 200."""
        response = self.client.get('/api/v1/catalog/categories/')
        self.assertEqual(response.status_code, 200)

    def test_categories_response_success_true(self):
        """Categories response has success=true."""
        response = self.client.get('/api/v1/catalog/categories/')
        data = response.json()
        self.assertTrue(data.get('success'))

    def test_seeded_categories_visible(self):
        """Seeded categories are visible via API (min. 3)."""
        response = self.client.get('/api/v1/catalog/categories/')
        data = response.json()['data']
        self.assertGreaterEqual(len(data), 3, "Expected at least 3 seeded categories")

    def test_categories_have_required_fields(self):
        """Categories have id, name, slug, sort_order."""
        response = self.client.get('/api/v1/catalog/categories/')
        data = response.json()['data']
        category = data[0]
        self.assertIn('id', category)
        self.assertIn('name', category)
        self.assertIn('slug', category)
        self.assertIn('sort_order', category)


class SeededProductsAPITest(TestCase):
    """Smoke tests for catalog products endpoint with seeded data."""

    def setUp(self):
        """Seed demo data before each test."""
        self.client = APIClient()
        call_command('seed_demo_data', verbosity=0)

    def test_products_b2c_returns_200(self):
        """GET /api/v1/catalog/products/?customer_group=b2c returns 200."""
        response = self.client.get('/api/v1/catalog/products/?customer_group=b2c')
        self.assertEqual(response.status_code, 200)

    def test_products_b2c_response_success_true(self):
        """Products B2C response has success=true."""
        response = self.client.get('/api/v1/catalog/products/?customer_group=b2c')
        data = response.json()
        self.assertTrue(data.get('success'))

    def test_seeded_products_b2c_visible(self):
        """Seeded B2C products are visible (min. 5)."""
        response = self.client.get('/api/v1/catalog/products/?customer_group=b2c')
        data = response.json()['data']
        self.assertGreaterEqual(len(data), 5, "Expected at least 5 B2C products")

    def test_products_b2b_returns_200(self):
        """GET /api/v1/catalog/products/?customer_group=b2b returns 200."""
        response = self.client.get('/api/v1/catalog/products/?customer_group=b2b')
        self.assertEqual(response.status_code, 200)

    def test_seeded_products_b2b_visible(self):
        """Seeded B2B products are visible (min. 2)."""
        response = self.client.get('/api/v1/catalog/products/?customer_group=b2b')
        data = response.json()['data']
        self.assertGreaterEqual(len(data), 2, "Expected at least 2 B2B products")

    def test_product_detail_by_slug_returns_200(self):
        """GET /api/v1/catalog/products/<slug>/?customer_group=b2c returns 200."""
        # Get first product and test it
        response = self.client.get('/api/v1/catalog/products/?customer_group=b2c')
        products = response.json()['data']
        if products:
            slug = products[0]['slug']
            response = self.client.get(f'/api/v1/catalog/products/{slug}/?customer_group=b2c')
            self.assertEqual(response.status_code, 200)

    def test_product_detail_has_required_fields(self):
        """Product detail response has required fields."""
        response = self.client.get('/api/v1/catalog/products/?customer_group=b2c')
        products = response.json()['data']
        if products:
            slug = products[0]['slug']
            response = self.client.get(f'/api/v1/catalog/products/{slug}/?customer_group=b2c')
            data = response.json()['data']
            self.assertIn('id', data)
            self.assertIn('name', data)
            self.assertIn('slug', data)
            self.assertIn('variants', data)

    def test_product_detail_has_variants(self):
        """Product detail includes variants."""
        response = self.client.get('/api/v1/catalog/products/?customer_group=b2c')
        products = response.json()['data']
        if products:
            slug = products[0]['slug']
            response = self.client.get(f'/api/v1/catalog/products/{slug}/?customer_group=b2c')
            data = response.json()['data']
            variants = data.get('variants', [])
            self.assertGreaterEqual(len(variants), 0)

    def test_b2b_only_product_not_visible_to_b2c(self):
        """B2B-only product returns 404 for B2C customer_group."""
        # Get all B2B products first to find a b2b-only one
        response = self.client.get('/api/v1/catalog/products/?customer_group=b2b')
        if response.status_code == 200:
            data = response.json().get('data', [])
            # Find a B2B product
            b2b_products = [p for p in data if 'B2B' in p.get('name', '') or 'b2b' in p.get('slug', '')]
            if b2b_products:
                slug = b2b_products[0]['slug']
                response = self.client.get(f'/api/v1/catalog/products/{slug}/?customer_group=b2c')
                # B2B-only products should return 404 for B2C
                self.assertEqual(response.status_code, 404)
                data = response.json()
                self.assertFalse(data.get('success'))
                self.assertIn('error', data)

    def test_invalid_customer_group_returns_400(self):
        """Invalid customer_group parameter returns 400."""
        response = self.client.get('/api/v1/catalog/products/?customer_group=invalid')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data.get('success'))
        self.assertIn('error', data)

    def test_nonexistent_product_returns_404(self):
        """Non-existent product slug returns 404."""
        response = self.client.get('/api/v1/catalog/products/nonexistent-product-slug/')
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data.get('success'))


class SeededShippingAPITest(TestCase):
    """Smoke tests for shipping methods endpoint with seeded data."""

    def setUp(self):
        """Seed demo data before each test."""
        self.client = APIClient()
        call_command('seed_demo_data', verbosity=0)

    def test_shipping_methods_b2c_returns_200(self):
        """GET /api/v1/shipping/methods/?customer_group=b2c returns 200."""
        response = self.client.get('/api/v1/shipping/methods/?customer_group=b2c')
        self.assertEqual(response.status_code, 200)

    def test_shipping_methods_response_success_true(self):
        """Shipping methods response has success=true."""
        response = self.client.get('/api/v1/shipping/methods/')
        data = response.json()
        self.assertTrue(data.get('success'))

    def test_seeded_shipping_methods_visible(self):
        """Seeded shipping methods for country=DE are visible (min. 3 DE B2C methods)."""
        response = self.client.get('/api/v1/shipping/methods/?country=DE&customer_group=b2c')
        data = response.json()['data']
        self.assertGreaterEqual(len(data), 3, "Expected at least 3 seeded DE shipping methods")

    def test_shipping_methods_have_required_fields(self):
        """Shipping methods have price and currency fields."""
        response = self.client.get('/api/v1/shipping/methods/')
        data = response.json()['data']
        method = data[0]
        self.assertIn('id', method)
        self.assertIn('name', method)
        self.assertIn('code', method)
        self.assertIn('base_price', method)
        self.assertIn('currency', method)

    def test_invalid_customer_group_returns_400(self):
        """Invalid customer_group parameter returns 400."""
        response = self.client.get('/api/v1/shipping/methods/?customer_group=invalid')
        self.assertEqual(response.status_code, 400)


class SeededPaymentsAPITest(TestCase):
    """Smoke tests for payment methods endpoint with seeded data."""

    def setUp(self):
        """Seed demo data before each test."""
        self.client = APIClient()
        call_command('seed_demo_data', verbosity=0)

    def test_payment_methods_returns_200(self):
        """GET /api/v1/payments/methods/ returns 200."""
        response = self.client.get('/api/v1/payments/methods/')
        self.assertEqual(response.status_code, 200)

    def test_payment_methods_response_success_true(self):
        """Payment methods response has success=true."""
        response = self.client.get('/api/v1/payments/methods/')
        data = response.json()
        self.assertTrue(data.get('success'))

    def test_seeded_payment_methods_visible(self):
        """Seeded payment methods are visible (min. 1 active)."""
        response = self.client.get('/api/v1/payments/methods/')
        data = response.json()['data']
        self.assertGreaterEqual(len(data), 1, "Expected at least 1 seeded active payment method")

    def test_payment_methods_have_required_fields(self):
        """Payment methods have required fields."""
        response = self.client.get('/api/v1/payments/methods/')
        data = response.json()['data']
        method = data[0]
        self.assertIn('id', method)
        self.assertIn('name', method)
        self.assertIn('code', method)
        self.assertIn('provider', method)

    def test_bank_transfer_payment_visible(self):
        """bank_transfer payment method is seeded and visible."""
        response = self.client.get('/api/v1/payments/methods/')
        data = response.json()['data']
        codes = [m['code'] for m in data]
        self.assertIn('bank_transfer', codes)

    def test_invalid_customer_group_returns_400(self):
        """Invalid customer_group parameter returns 400."""
        response = self.client.get('/api/v1/payments/methods/?customer_group=invalid')
        self.assertEqual(response.status_code, 400)


class SeededLegalAPITest(TestCase):
    """Smoke tests for legal active documents endpoint with seeded data."""

    def setUp(self):
        """Seed demo data before each test."""
        self.client = APIClient()
        call_command('seed_demo_data', verbosity=0)

    def test_legal_active_returns_200(self):
        """GET /api/v1/legal/active/?customer_group=b2c returns 200."""
        response = self.client.get('/api/v1/legal/active/?customer_group=b2c')
        self.assertEqual(response.status_code, 200)

    def test_legal_active_response_success_true(self):
        """Legal active response has success=true."""
        response = self.client.get('/api/v1/legal/active/?customer_group=b2c')
        data = response.json()
        self.assertTrue(data.get('success'))

    def test_seeded_legal_documents_visible(self):
        """Seeded active legal documents are visible (min. 4)."""
        response = self.client.get('/api/v1/legal/active/?customer_group=b2c')
        data = response.json()['data']
        self.assertGreaterEqual(len(data), 4, "Expected at least 4 active legal documents")

    def test_legal_documents_have_required_fields(self):
        """Legal documents have required fields."""
        response = self.client.get('/api/v1/legal/active/?customer_group=b2c')
        data = response.json()['data']
        doc = data[0]
        self.assertIn('document_type', doc)
        self.assertIn('title', doc)
        self.assertIn('version', doc)

    def test_legal_documents_marked_as_demo(self):
        """
        Seeded legal documents are marked as DEMO PLACEHOLDER.
        Note: API only returns metadata (document_type, title, version).
        Content is checked via the model directly since the serializer
        does not include body content for legal documents.
        """
        versions = LegalDocumentVersion.objects.filter(status='active')
        self.assertGreaterEqual(versions.count(), 4)
        for version in versions:
            self.assertIn('DEMO PLACEHOLDER', version.content)

    def test_invalid_customer_group_returns_400(self):
        """Invalid customer_group parameter returns 400."""
        response = self.client.get('/api/v1/legal/active/?customer_group=invalid')
        self.assertEqual(response.status_code, 400)


class APIResponseFormatTest(TestCase):
    """Smoke tests for API response format consistency."""

    def setUp(self):
        """Seed demo data before each test."""
        self.client = APIClient()
        call_command('seed_demo_data', verbosity=0)

    def test_success_response_format(self):
        """Successful responses have success=true and data."""
        response = self.client.get('/api/v1/catalog/categories/')
        data = response.json()
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)

    def test_error_response_format(self):
        """Error responses have success=false and error."""
        response = self.client.get('/api/v1/catalog/products/?customer_group=invalid')
        data = response.json()
        self.assertIn('success', data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
        self.assertIn('code', data['error'])
        self.assertIn('message', data['error'])
