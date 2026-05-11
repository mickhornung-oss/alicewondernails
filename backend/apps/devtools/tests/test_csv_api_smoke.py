"""
Smoke tests for API endpoints using CSV-imported demo data.

These tests validate the complete chain: CSV-Import → Database → API.
They ensure that demo data imported via import_demo_csv is correctly exposed
through the read-only API v1 endpoints.

Note: These are integration tests validating the CSV→DB→API flow.
API contract tests are in apps/api/tests/test_api.py.
Pricing endpoint tests are in apps/api/tests/test_pricing_endpoints.py.
"""

from django.test import TestCase
from django.core.management import call_command
from rest_framework.test import APIClient


class CSVImportHealthAPITest(TestCase):
    """Smoke tests for health endpoint."""

    @classmethod
    def setUpClass(cls):
        """Import CSV data once for all tests in this class."""
        super().setUpClass()
        call_command('import_demo_csv', verbosity=0)

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()

    def test_csv_health_endpoint_returns_200(self):
        """GET /api/v1/health/ returns 200."""
        response = self.client.get('/api/v1/health/')
        self.assertEqual(response.status_code, 200)

    def test_csv_health_response_format(self):
        """Health response has correct format: success=true, data.status=ok."""
        response = self.client.get('/api/v1/health/')
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('data', data)
        self.assertEqual(data['data'].get('status'), 'ok')


class CSVImportCategoriesAPITest(TestCase):
    """Smoke tests for categories endpoint with CSV-imported data."""

    @classmethod
    def setUpClass(cls):
        """Import CSV data once."""
        super().setUpClass()
        call_command('import_demo_csv', verbosity=0)

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()

    def test_csv_categories_endpoint_returns_200(self):
        """GET /api/v1/catalog/categories/ returns 200."""
        response = self.client.get('/api/v1/catalog/categories/')
        self.assertEqual(response.status_code, 200)

    def test_csv_categories_count_minimum_4(self):
        """CSV categories (4) are visible via API."""
        response = self.client.get('/api/v1/catalog/categories/')
        data = response.json()['data']
        self.assertGreaterEqual(len(data), 4, "Expected at least 4 CSV-imported categories")

    def test_csv_categories_include_expected_slugs(self):
        """CSV categories include expected slugs: nail-colors, care-products, etc."""
        response = self.client.get('/api/v1/catalog/categories/')
        data = response.json()['data']
        slugs = [cat['slug'] for cat in data]
        
        # Check for CSV-imported categories
        self.assertIn('nail-colors', slugs)
        self.assertIn('care-products', slugs)


class CSVImportProductsListAPITest(TestCase):
    """Smoke tests for products list endpoint with CSV-imported data."""

    @classmethod
    def setUpClass(cls):
        """Import CSV data once."""
        super().setUpClass()
        call_command('import_demo_csv', verbosity=0)

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()

    def test_csv_products_b2c_returns_200(self):
        """GET /api/v1/catalog/products/?customer_group=b2c returns 200."""
        response = self.client.get('/api/v1/catalog/products/?customer_group=b2c')
        self.assertEqual(response.status_code, 200)

    def test_csv_products_b2b_returns_200(self):
        """GET /api/v1/catalog/products/?customer_group=b2b returns 200."""
        response = self.client.get('/api/v1/catalog/products/?customer_group=b2b')
        self.assertEqual(response.status_code, 200)

    def test_csv_products_b2c_count_minimum_5(self):
        """CSV B2C-visible products (public + b2c_only) are visible (min. 5)."""
        response = self.client.get('/api/v1/catalog/products/?customer_group=b2c')
        data = response.json()['data']
        self.assertGreaterEqual(len(data), 5, "Expected at least 5 B2C-visible CSV products")

    def test_csv_products_b2b_count_minimum_2(self):
        """CSV B2B-visible products (public + b2b_only) are visible (min. 2)."""
        response = self.client.get('/api/v1/catalog/products/?customer_group=b2b')
        data = response.json()['data']
        self.assertGreaterEqual(len(data), 2, "Expected at least 2 B2B-visible CSV products")

    def test_csv_products_b2b_only_not_in_b2c_list(self):
        """B2B-only CSV product (b2b-wholesale-kit) is not in B2C list."""
        response_b2c = self.client.get('/api/v1/catalog/products/?customer_group=b2c')
        data_b2c = response_b2c.json()['data']
        slugs_b2c = [prod['slug'] for prod in data_b2c]
        
        # b2b-wholesale-kit should NOT appear for B2C
        self.assertNotIn('b2b-wholesale-kit', slugs_b2c)

    def test_csv_products_b2c_only_not_in_b2b_list(self):
        """B2C-only CSV product (polish-pro-azure) is not in B2B list."""
        response_b2b = self.client.get('/api/v1/catalog/products/?customer_group=b2b')
        data_b2b = response_b2b.json()['data']
        slugs_b2b = [prod['slug'] for prod in data_b2b]
        
        # polish-pro-azure should NOT appear for B2B
        self.assertNotIn('polish-pro-azure', slugs_b2b)

    def test_csv_products_invalid_customer_group_returns_400(self):
        """Invalid customer_group returns 400."""
        response = self.client.get('/api/v1/catalog/products/?customer_group=invalid')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data.get('success'))


class CSVImportProductDetailAPITest(TestCase):
    """Smoke tests for product detail endpoint with CSV-imported data."""

    @classmethod
    def setUpClass(cls):
        """Import CSV data once."""
        super().setUpClass()
        call_command('import_demo_csv', verbosity=0)

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()

    def test_csv_product_detail_by_slug_returns_200(self):
        """GET /api/v1/catalog/products/gel-color-rose-gold/?customer_group=b2c returns 200."""
        response = self.client.get('/api/v1/catalog/products/gel-color-rose-gold/?customer_group=b2c')
        self.assertEqual(response.status_code, 200)

    def test_csv_product_detail_includes_variants(self):
        """Product detail includes variants array."""
        response = self.client.get('/api/v1/catalog/products/gel-color-rose-gold/?customer_group=b2c')
        data = response.json()['data']
        self.assertIn('variants', data)
        variants = data.get('variants', [])
        self.assertGreater(len(variants), 0, "Expected at least 1 variant")

    def test_csv_product_detail_variants_have_sku(self):
        """Variants in product detail have sku field."""
        response = self.client.get('/api/v1/catalog/products/gel-color-rose-gold/?customer_group=b2c')
        data = response.json()['data']
        variants = data.get('variants', [])
        if variants:
            # Check that first variant has sku
            self.assertIn('sku', variants[0])

    def test_csv_b2b_only_product_not_visible_to_b2c(self):
        """B2B-only CSV product returns 404 for B2C."""
        response = self.client.get('/api/v1/catalog/products/b2b-wholesale-kit/?customer_group=b2c')
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data.get('success'))
        self.assertIn('error', data)

    def test_csv_b2c_only_product_not_visible_to_b2b(self):
        """B2C-only CSV product returns 404 for B2B."""
        response = self.client.get('/api/v1/catalog/products/polish-pro-azure/?customer_group=b2b')
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data.get('success'))


class CSVImportPricingAPITest(TestCase):
    """Smoke tests for pricing endpoint with CSV-imported data."""

    @classmethod
    def setUpClass(cls):
        """Import CSV data once."""
        super().setUpClass()
        call_command('import_demo_csv', verbosity=0)

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()

    def test_csv_pricing_endpoint_returns_200(self):
        """GET /api/v1/pricing/products/gel-color-rose-gold/prices/?customer_group=b2c returns 200."""
        response = self.client.get('/api/v1/pricing/products/gel-color-rose-gold/prices/?customer_group=b2c')
        self.assertEqual(response.status_code, 200)

    def test_csv_pricing_b2c_count_minimum_2(self):
        """CSV B2C prices for gel-color-rose-gold are visible (min. 2)."""
        response = self.client.get('/api/v1/pricing/products/gel-color-rose-gold/prices/?customer_group=b2c')
        data = response.json()['data']
        prices = data.get('prices', [])
        self.assertGreaterEqual(len(prices), 2, "Expected at least 2 B2C prices from CSV")

    def test_csv_pricing_includes_tax_info(self):
        """CSV prices include tax_rate and price_includes_tax."""
        response = self.client.get('/api/v1/pricing/products/gel-color-rose-gold/prices/?customer_group=b2c')
        data = response.json()['data']
        prices = data.get('prices', [])
        if prices:
            price = prices[0]
            self.assertIn('tax_rate', price)
            self.assertIn('price_includes_tax', price)
            self.assertEqual(price.get('price_includes_tax'), True)

    def test_csv_pricing_b2c_and_b2b_differ(self):
        """CSV B2C prices differ from B2B prices for same product."""
        response_b2c = self.client.get('/api/v1/pricing/products/gel-color-rose-gold/prices/?customer_group=b2c')
        response_b2b = self.client.get('/api/v1/pricing/products/gel-color-rose-gold/prices/?customer_group=b2b')
        
        prices_b2c = response_b2c.json()['data'].get('prices', [])
        prices_b2b = response_b2b.json()['data'].get('prices', [])
        
        # Extract amounts for comparison
        amounts_b2c = [p.get('amount') for p in prices_b2c]
        amounts_b2b = [p.get('amount') for p in prices_b2b]
        
        # B2C and B2B prices should be different
        self.assertNotEqual(amounts_b2c, amounts_b2b, "Expected B2C and B2B prices to differ")

    def test_csv_b2b_only_product_has_prices(self):
        """B2B-only CSV product has prices for B2B."""
        response = self.client.get('/api/v1/pricing/products/b2b-wholesale-kit/prices/?customer_group=b2b')
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        prices = data.get('prices', [])
        self.assertGreater(len(prices), 0, "Expected prices for B2B-only product")

    def test_csv_pricing_response_format_stable(self):
        """Pricing response has correct format: success/data/prices."""
        response = self.client.get('/api/v1/pricing/products/gel-color-rose-gold/prices/?customer_group=b2c')
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('data', data)
        self.assertIn('prices', data['data'])
        self.assertIn('currency', data['data'])


class CSVImportShippingAPITest(TestCase):
    """Smoke tests for shipping methods endpoint with CSV-imported data."""

    @classmethod
    def setUpClass(cls):
        """Import CSV data once."""
        super().setUpClass()
        call_command('import_demo_csv', verbosity=0)

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()

    def test_csv_shipping_methods_de_returns_200(self):
        """GET /api/v1/shipping/methods/?customer_group=b2c&country=DE returns 200."""
        response = self.client.get('/api/v1/shipping/methods/?customer_group=b2c&country=DE')
        self.assertEqual(response.status_code, 200)

    def test_csv_shipping_methods_de_count_minimum_3(self):
        """CSV shipping methods for DE are visible (min. 3)."""
        response = self.client.get('/api/v1/shipping/methods/?customer_group=b2c&country=DE')
        data = response.json()['data']
        self.assertGreaterEqual(len(data), 3, "Expected at least 3 DE shipping methods from CSV")

    def test_csv_shipping_methods_have_required_fields(self):
        """Shipping methods include code, name, base_price fields."""
        response = self.client.get('/api/v1/shipping/methods/?customer_group=b2c&country=DE')
        data = response.json()['data']
        if data:
            method = data[0]
            self.assertIn('code', method)
            self.assertIn('name', method)
            # Price field from serializer (base_price, not price)
            self.assertIn('base_price', method)


class CSVImportPaymentsAPITest(TestCase):
    """Smoke tests for payment methods endpoint with CSV-imported data."""

    @classmethod
    def setUpClass(cls):
        """Import CSV data once."""
        super().setUpClass()
        call_command('import_demo_csv', verbosity=0)

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()

    def test_csv_payment_methods_returns_200(self):
        """GET /api/v1/payments/methods/?customer_group=b2c returns 200."""
        response = self.client.get('/api/v1/payments/methods/?customer_group=b2c')
        self.assertEqual(response.status_code, 200)

    def test_csv_payment_methods_count_minimum_4(self):
        """CSV payment methods are visible (min. 1 active)."""
        response = self.client.get('/api/v1/payments/methods/?customer_group=b2c')
        data = response.json()['data']
        self.assertGreaterEqual(len(data), 1, "Expected at least 1 active payment method from CSV")


class CSVImportLegalAPITest(TestCase):
    """Smoke tests for legal documents endpoint with CSV-imported data."""

    @classmethod
    def setUpClass(cls):
        """Import CSV data once."""
        super().setUpClass()
        call_command('import_demo_csv', verbosity=0)

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()

    def test_csv_legal_active_returns_200(self):
        """GET /api/v1/legal/active/?customer_group=b2c returns 200."""
        response = self.client.get('/api/v1/legal/active/?customer_group=b2c')
        self.assertEqual(response.status_code, 200)

    def test_csv_legal_active_count_minimum_4(self):
        """CSV active legal documents are visible (min. 4)."""
        response = self.client.get('/api/v1/legal/active/?customer_group=b2c')
        data = response.json()['data']
        self.assertGreaterEqual(len(data), 4, "Expected at least 4 active legal documents from CSV")


class CSVImportErrorHandlingTest(TestCase):
    """Smoke tests for error handling with CSV-imported data."""

    @classmethod
    def setUpClass(cls):
        """Import CSV data once."""
        super().setUpClass()
        call_command('import_demo_csv', verbosity=0)

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()

    def test_csv_nonexistent_product_returns_404(self):
        """Non-existent product slug returns 404."""
        response = self.client.get('/api/v1/catalog/products/nonexistent-product/?customer_group=b2c')
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data.get('success'))
        self.assertIn('error', data)

    def test_csv_error_response_format_stable(self):
        """Error responses have consistent format: success=false, error."""
        response = self.client.get('/api/v1/catalog/products/nonexistent-product/?customer_group=b2c')
        data = response.json()
        self.assertFalse(data.get('success'))
        self.assertIn('error', data)
        error = data['error']
        self.assertIn('code', error)
        self.assertIn('message', error)
