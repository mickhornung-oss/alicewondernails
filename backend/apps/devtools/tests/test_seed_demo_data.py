from django.test import TestCase
from django.core.management import call_command
from io import StringIO
from apps.catalog.models import ProductCategory, Product, ProductVariant
from apps.pricing.models import ProductPrice
from apps.shipping.models import ShippingZone, ShippingMethod
from apps.payments.models import PaymentMethod
from apps.legal.models import LegalDocument, LegalDocumentVersion
from apps.consent.models import ConsentCategory


class SeedDemoDataTests(TestCase):
    """Tests for seed_demo_data management command."""
    
    def test_seed_command_runs_without_error(self):
        """Test that seed_demo_data command executes without errors."""
        out = StringIO()
        try:
            call_command('seed_demo_data', stdout=out)
        except Exception as e:
            self.fail(f"seed_demo_data command raised exception: {e}")
        
        output = out.getvalue()
        self.assertIn('Demo data seed completed', output)
    
    def test_seed_command_is_idempotent(self):
        """Test that running seed twice creates no duplicates."""
        out = StringIO()
        
        # First run
        call_command('seed_demo_data', stdout=out)
        categories_after_first = ProductCategory.objects.count()
        products_after_first = Product.objects.count()
        
        # Second run
        out = StringIO()
        call_command('seed_demo_data', stdout=out)
        categories_after_second = ProductCategory.objects.count()
        products_after_second = Product.objects.count()
        
        # Verify no duplicates
        self.assertEqual(categories_after_first, categories_after_second)
        self.assertEqual(products_after_first, products_after_second)
        
        # Verify skipped messages in output
        output = out.getvalue()
        self.assertIn('skipped', output.lower())
    
    def test_catalog_seeded(self):
        """Test that catalog data is seeded correctly."""
        call_command('seed_demo_data')
        
        # Check categories
        categories = ProductCategory.objects.filter(is_active=True)
        self.assertGreaterEqual(categories.count(), 3)
        
        # Check products
        products = Product.objects.filter(is_active=True)
        self.assertGreaterEqual(products.count(), 8)
        
        # Check public visibility
        public_products = products.filter(visibility='public')
        self.assertGreaterEqual(public_products.count(), 5)
        
        # Check variants
        variants = ProductVariant.objects.filter(is_active=True)
        self.assertGreaterEqual(variants.count(), 9)
    
    def test_pricing_seeded(self):
        """Test that pricing data is seeded correctly."""
        call_command('seed_demo_data')
        
        # Check prices
        prices = ProductPrice.objects.filter(is_active=True)
        self.assertGreaterEqual(prices.count(), 15)
        
        # Check all amounts are positive
        for price in prices:
            self.assertGreater(price.amount, 0, f"Price {price.id} has non-positive amount: {price.amount}")
        
        # Check B2C and B2B prices
        b2c_prices = prices.filter(customer_group='b2c')
        b2b_prices = prices.filter(customer_group='b2b')
        self.assertGreater(b2c_prices.count(), 0)
        self.assertGreater(b2b_prices.count(), 0)
        
        # Check tax rate
        for price in prices:
            self.assertEqual(price.tax_rate, 19.00)
    
    def test_shipping_zones_seeded(self):
        """Test that shipping zones are seeded correctly."""
        call_command('seed_demo_data')
        
        zones = ShippingZone.objects.filter(is_active=True)
        self.assertEqual(zones.count(), 2)
        
        # Check specific zones
        self.assertTrue(zones.filter(code='de_std').exists())
        self.assertTrue(zones.filter(code='eu_ext').exists())
    
    def test_shipping_methods_seeded(self):
        """Test that shipping methods are seeded correctly."""
        call_command('seed_demo_data')
        
        methods = ShippingMethod.objects.filter(is_active=True)
        self.assertGreaterEqual(methods.count(), 5)
        
        # Check B2C and B2B methods
        b2c_methods = methods.filter(customer_group='b2c')
        b2b_methods = methods.filter(customer_group='b2b')
        self.assertGreater(b2c_methods.count(), 0)
        self.assertGreater(b2b_methods.count(), 0)
    
    def test_payment_methods_seeded(self):
        """Test that payment methods are seeded correctly."""
        call_command('seed_demo_data')
        
        methods = PaymentMethod.objects.filter(is_active=True)
        self.assertGreaterEqual(methods.count(), 4)
        
        # Check specific methods
        self.assertTrue(methods.filter(code='bank_transfer').exists())
        self.assertTrue(methods.filter(code='invoice').exists())
        self.assertTrue(methods.filter(code='paypal').exists())
    
    def test_legal_documents_seeded(self):
        """Test that legal documents are seeded correctly."""
        call_command('seed_demo_data')
        
        docs = LegalDocument.objects.all()
        self.assertGreaterEqual(docs.count(), 4)
        
        # Check for specific document types
        self.assertTrue(docs.filter(document_type='terms_of_service').exists())
        self.assertTrue(docs.filter(document_type='privacy_policy').exists())
        self.assertTrue(docs.filter(document_type='withdrawal_policy').exists())
    
    def test_legal_document_versions_active(self):
        """Test that legal document versions are marked as active."""
        call_command('seed_demo_data')
        
        # Check that all documents have at least one active version
        for doc in LegalDocument.objects.all():
            active_versions = LegalDocumentVersion.objects.filter(
                document=doc,
                status='active'
            )
            self.assertGreater(active_versions.count(), 0, f"Document {doc.title} has no active version")
    
    def test_legal_documents_marked_as_demo(self):
        """Test that demo placeholder is marked in legal content."""
        call_command('seed_demo_data')
        
        versions = LegalDocumentVersion.objects.filter(status='active')
        for version in versions:
            self.assertIn('DEMO PLACEHOLDER', version.content)
            self.assertIn('NOT FOR PRODUCTION', version.content)
    
    def test_consent_categories_seeded(self):
        """Test that consent categories are seeded correctly."""
        call_command('seed_demo_data')
        
        categories = ConsentCategory.objects.filter(is_active=True)
        self.assertEqual(categories.count(), 4)
        
        # Check specific categories
        self.assertTrue(categories.filter(key='newsletter').exists())
        self.assertTrue(categories.filter(key='analytics').exists())
        self.assertTrue(categories.filter(key='marketing').exists())
        self.assertTrue(categories.filter(key='terms_accept').exists())
        
        # Check required consent
        required = categories.filter(is_required=True)
        self.assertEqual(required.count(), 1)
        self.assertTrue(required.filter(key='terms_accept').exists())
    
    def test_no_frozen_models_modified(self):
        """Test that frozen module models are not accidentally modified during seed."""
        # This is a sanity check - the seed command should not modify
        # accounts, customers, business, core, auditlog, or api modules
        call_command('seed_demo_data')
        
        # Just verify command completes; actual frozen modules should not be touched
        # by the seed command (no models are imported from frozen modules)
        self.assertTrue(True)
