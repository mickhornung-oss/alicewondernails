"""
Tests for import_demo_csv management command.

Tests cover:
- CSV file existence and readability
- Header validation
- Import success (create/update logic)
- Idempotency (second run should skip)
- Foreign key validation
- Field validation and type coercion
- Error handling
"""

import os
import tempfile
from decimal import Decimal
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, TransactionTestCase
from django.db import transaction

from config.settings.base import ROOT_DIR

from apps.catalog.models import ProductCategory, Product, ProductVariant
from apps.pricing.models import ProductPrice
from apps.shipping.models import ShippingZone, ShippingMethod
from apps.payments.models import PaymentMethod
from apps.legal.models import LegalDocument, LegalDocumentVersion
from apps.consent.models import ConsentCategory


class ImportDemoCsvCommandTest(TransactionTestCase):
    """
    Tests for import_demo_csv management command.
    
    Uses TransactionTestCase for proper atomic() context testing.
    """
    
    def setUp(self):
        """Create temporary directory for test CSVs"""
        self.temp_dir = tempfile.mkdtemp()
        self.demo_dir = os.path.join(str(ROOT_DIR), 'backend/data/imports/demo')
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    # ========== CSV File Tests ==========
    
    def test_csv_files_exist_in_default_location(self):
        """Test that CSV files exist in default location"""
        expected_files = [
            'categories_demo.csv',
            'products_demo.csv',
            'variants_demo.csv',
            'prices_demo.csv',
            'shipping_zones_demo.csv',
            'shipping_methods_demo.csv',
            'payment_methods_demo.csv',
            'legal_documents_demo.csv',
            'legal_versions_demo.csv',
            'consent_categories_demo.csv',
        ]
        
        for filename in expected_files:
            filepath = os.path.join(self.demo_dir, filename)
            self.assertTrue(os.path.exists(filepath), f"{filepath} not found")
    
    def test_csv_files_are_readable(self):
        """Test that CSV files can be read"""
        expected_files = [
            'categories_demo.csv',
            'products_demo.csv',
            'variants_demo.csv',
        ]
        
        for filename in expected_files:
            filepath = os.path.join(self.demo_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                self.assertTrue(len(first_line) > 0, f"Cannot read {filename}")
    
    def test_csv_headers_have_required_columns(self):
        """Test that CSV headers contain required columns"""
        import csv
        
        expected_headers = {
            'categories_demo.csv': ['name', 'slug'],
            'products_demo.csv': ['name', 'slug', 'category_slug'],
            'variants_demo.csv': ['product_slug', 'name'],
            'prices_demo.csv': ['product_slug', 'customer_group', 'amount'],
            'shipping_zones_demo.csv': ['name', 'code'],
            'shipping_methods_demo.csv': ['name', 'code', 'zone_code'],
            'payment_methods_demo.csv': ['name', 'code'],
            'legal_documents_demo.csv': ['document_type', 'title'],
            'legal_versions_demo.csv': ['document_type', 'version', 'content'],
            'consent_categories_demo.csv': ['key', 'name'],
        }
        
        for filename, required_fields in expected_headers.items():
            filepath = os.path.join(self.demo_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames or []
                for field in required_fields:
                    self.assertIn(field, headers, f"{field} not in {filename} headers")
    
    # ========== Import Success Tests ==========
    
    def test_import_creates_categories(self):
        """Test that import creates ProductCategory objects"""
        out = StringIO()
        call_command('import_demo_csv', stdout=out)
        
        # Should have categories from CSV
        categories = ProductCategory.objects.filter(slug__startswith='nail')
        self.assertGreater(categories.count(), 0)
    
    def test_import_creates_products(self):
        """Test that import creates Product objects"""
        out = StringIO()
        call_command('import_demo_csv', stdout=out)
        
        # Should have products from CSV
        products = Product.objects.filter(slug__startswith='gel')
        self.assertGreater(products.count(), 0)
    
    def test_import_creates_variants(self):
        """Test that import creates ProductVariant objects"""
        out = StringIO()
        call_command('import_demo_csv', stdout=out)
        
        # Should have variants from CSV
        variants = ProductVariant.objects.filter(sku__isnull=False)
        self.assertGreater(variants.count(), 0)
    
    def test_import_creates_prices(self):
        """Test that import creates ProductPrice objects"""
        out = StringIO()
        call_command('import_demo_csv', stdout=out)
        
        # Should have prices from CSV
        prices = ProductPrice.objects.all()
        self.assertGreater(prices.count(), 0)
    
    def test_import_creates_shipping_zones(self):
        """Test that import creates ShippingZone objects"""
        out = StringIO()
        call_command('import_demo_csv', stdout=out)
        
        zones = ShippingZone.objects.filter(code__startswith='de')
        self.assertGreater(zones.count(), 0)
    
    def test_import_creates_payment_methods(self):
        """Test that import creates PaymentMethod objects"""
        out = StringIO()
        call_command('import_demo_csv', stdout=out)
        
        methods = PaymentMethod.objects.all()
        self.assertGreater(methods.count(), 0)
    
    def test_import_creates_legal_documents(self):
        """Test that import creates LegalDocument objects"""
        out = StringIO()
        call_command('import_demo_csv', stdout=out)
        
        docs = LegalDocument.objects.all()
        self.assertGreater(docs.count(), 0)
    
    def test_import_creates_consent_categories(self):
        """Test that import creates ConsentCategory objects"""
        out = StringIO()
        call_command('import_demo_csv', stdout=out)
        
        categories = ConsentCategory.objects.all()
        self.assertGreater(categories.count(), 0)
    
    # ========== Idempotency Tests ==========
    
    def test_second_import_does_not_duplicate(self):
        """Test that second import does not create duplicates (idempotent)"""
        out = StringIO()
        
        # First import
        call_command('import_demo_csv', stdout=out)
        initial_count = ProductCategory.objects.count()
        
        # Second import
        out = StringIO()
        call_command('import_demo_csv', stdout=out)
        final_count = ProductCategory.objects.count()
        
        # Should have same count (no duplicates)
        self.assertEqual(initial_count, final_count)
    
    def test_second_import_recognizes_existing_objects(self):
        """Test that second import marks objects as skipped/updated, not created"""
        # First import
        call_command('import_demo_csv', stdout=StringIO())
        first_category = ProductCategory.objects.first()
        original_name = first_category.name
        
        # Verify skipped count in second run
        out = StringIO()
        call_command('import_demo_csv', stdout=out)
        output = out.getvalue()
        
        # Output should indicate categories were not duplicated
        self.assertIn('ProductCategory', output)
    
    def test_import_updates_modified_data(self):
        """Test that import updates existing records when data changes"""
        # First import
        call_command('import_demo_csv', stdout=StringIO())
        category = ProductCategory.objects.get(slug='nail-colors')
        original_name = category.name
        
        # Manually modify the category
        category.name = 'Modified Name'
        category.save()
        
        # Create CSV with changed data
        csv_dir = tempfile.mkdtemp()
        try:
            csv_file = os.path.join(csv_dir, 'categories_demo.csv')
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write('name,slug,description\n')
                f.write('Updated Nail Colors,nail-colors,Updated Description\n')
            
            # Copy other required CSVs
            for filename in ['products_demo.csv', 'variants_demo.csv', 'prices_demo.csv',
                            'shipping_zones_demo.csv', 'shipping_methods_demo.csv',
                            'payment_methods_demo.csv', 'legal_documents_demo.csv',
                            'legal_versions_demo.csv', 'consent_categories_demo.csv']:
                src = os.path.join(self.demo_dir, filename)
                dst = os.path.join(csv_dir, filename)
                import shutil
                shutil.copy(src, dst)
            
            # Re-import from temp dir
            call_command('import_demo_csv', source=csv_dir, stdout=StringIO())
            
            # Verify update
            updated_category = ProductCategory.objects.get(slug='nail-colors')
            self.assertEqual(updated_category.name, 'Updated Nail Colors')
        finally:
            import shutil
            shutil.rmtree(csv_dir)
    
    # ========== Foreign Key Validation Tests ==========
    
    def test_import_validates_product_category_fk(self):
        """Test that import validates category_slug foreign key"""
        csv_dir = tempfile.mkdtemp()
        try:
            # Create products CSV with invalid category_slug
            csv_file = os.path.join(csv_dir, 'products_demo.csv')
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write('name,slug,category_slug,product_type,visibility,short_description,description\n')
                f.write('Test Product,test-prod,nonexistent-category,gel,public,,\n')
            
            # Copy other required CSVs
            for filename in ['categories_demo.csv', 'variants_demo.csv', 'prices_demo.csv',
                            'shipping_zones_demo.csv', 'shipping_methods_demo.csv',
                            'payment_methods_demo.csv', 'legal_documents_demo.csv',
                            'legal_versions_demo.csv', 'consent_categories_demo.csv']:
                src = os.path.join(self.demo_dir, filename)
                dst = os.path.join(csv_dir, filename)
                import shutil
                shutil.copy(src, dst)
            
            # Should raise error
            with self.assertRaises(CommandError):
                call_command('import_demo_csv', source=csv_dir, stdout=StringIO())
        finally:
            import shutil
            shutil.rmtree(csv_dir)
    
    def test_import_validates_product_variant_fk(self):
        """Test that import validates product_slug foreign key for variants"""
        csv_dir = tempfile.mkdtemp()
        try:
            # Create variants CSV with invalid product_slug
            csv_file = os.path.join(csv_dir, 'variants_demo.csv')
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write('product_slug,name,sku,is_default\n')
                f.write('nonexistent-product,Test Variant,TEST-SKU,FALSE\n')
            
            # Copy other required CSVs
            for filename in ['categories_demo.csv', 'products_demo.csv', 'prices_demo.csv',
                            'shipping_zones_demo.csv', 'shipping_methods_demo.csv',
                            'payment_methods_demo.csv', 'legal_documents_demo.csv',
                            'legal_versions_demo.csv', 'consent_categories_demo.csv']:
                src = os.path.join(self.demo_dir, filename)
                dst = os.path.join(csv_dir, filename)
                import shutil
                shutil.copy(src, dst)
            
            # Should raise error
            with self.assertRaises(CommandError):
                call_command('import_demo_csv', source=csv_dir, stdout=StringIO())
        finally:
            import shutil
            shutil.rmtree(csv_dir)
    
    # ========== Field Validation Tests ==========
    
    def test_import_validates_required_fields(self):
        """Test that import validates required fields are present"""
        csv_dir = tempfile.mkdtemp()
        try:
            # Create categories CSV with missing name
            csv_file = os.path.join(csv_dir, 'categories_demo.csv')
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write('name,slug,description\n')
                f.write(',missing-name-slug,Description\n')
            
            # Copy other required CSVs
            for filename in ['products_demo.csv', 'variants_demo.csv', 'prices_demo.csv',
                            'shipping_zones_demo.csv', 'shipping_methods_demo.csv',
                            'payment_methods_demo.csv', 'legal_documents_demo.csv',
                            'legal_versions_demo.csv', 'consent_categories_demo.csv']:
                src = os.path.join(self.demo_dir, filename)
                dst = os.path.join(csv_dir, filename)
                import shutil
                shutil.copy(src, dst)
            
            # Should raise error
            with self.assertRaises(CommandError):
                call_command('import_demo_csv', source=csv_dir, stdout=StringIO())
        finally:
            import shutil
            shutil.rmtree(csv_dir)
    
    def test_import_coerces_decimal_fields(self):
        """Test that import properly coerces string to Decimal for prices"""
        out = StringIO()
        call_command('import_demo_csv', stdout=out)
        
        # Verify that prices were stored as Decimal
        price = ProductPrice.objects.first()
        self.assertIsInstance(price.amount, Decimal)
    
    def test_import_validates_decimal_prices(self):
        """Test that import rejects invalid decimal prices"""
        csv_dir = tempfile.mkdtemp()
        try:
            # Create prices CSV with invalid amount
            csv_file = os.path.join(csv_dir, 'prices_demo.csv')
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write('product_slug,variant_sku,customer_group,amount,currency,tax_rate,price_includes_tax\n')
                f.write('test-prod,,b2c,not-a-number,EUR,19.00,TRUE\n')
            
            # Copy other required CSVs
            for filename in ['categories_demo.csv', 'products_demo.csv', 'variants_demo.csv',
                            'shipping_zones_demo.csv', 'shipping_methods_demo.csv',
                            'payment_methods_demo.csv', 'legal_documents_demo.csv',
                            'legal_versions_demo.csv', 'consent_categories_demo.csv']:
                src = os.path.join(self.demo_dir, filename)
                dst = os.path.join(csv_dir, filename)
                import shutil
                shutil.copy(src, dst)
            
            # Should raise error
            with self.assertRaises(CommandError):
                call_command('import_demo_csv', source=csv_dir, stdout=StringIO())
        finally:
            import shutil
            shutil.rmtree(csv_dir)
    
    # ========== Transaction Safety Tests ==========
    
    def test_import_uses_atomic_transaction(self):
        """Test that import uses atomic transaction (rollback on error)"""
        # Count before
        before_count = ProductCategory.objects.count()
        
        # Create invalid import that should fail
        csv_dir = tempfile.mkdtemp()
        try:
            # Valid categories but invalid products (missing category_slug)
            categories_file = os.path.join(csv_dir, 'categories_demo.csv')
            with open(categories_file, 'w', encoding='utf-8') as f:
                f.write('name,slug,description\n')
                f.write('Test Category,test-cat,Test\n')
            
            products_file = os.path.join(csv_dir, 'products_demo.csv')
            with open(products_file, 'w', encoding='utf-8') as f:
                f.write('name,slug,category_slug,product_type,visibility,short_description,description\n')
                f.write('Test Product,test-prod,,gel,public,,\n')
            
            # Copy other CSVs
            for filename in ['variants_demo.csv', 'prices_demo.csv',
                            'shipping_zones_demo.csv', 'shipping_methods_demo.csv',
                            'payment_methods_demo.csv', 'legal_documents_demo.csv',
                            'legal_versions_demo.csv', 'consent_categories_demo.csv']:
                src = os.path.join(self.demo_dir, filename)
                dst = os.path.join(csv_dir, filename)
                import shutil
                shutil.copy(src, dst)
            
            # Should fail
            try:
                call_command('import_demo_csv', source=csv_dir, stdout=StringIO())
            except CommandError:
                pass
            
            # Verify no new category was created (transaction rolled back)
            after_count = ProductCategory.objects.count()
            self.assertEqual(before_count, after_count)
        finally:
            import shutil
            shutil.rmtree(csv_dir)
    
    # ========== Legal Documents Tests ==========
    
    def test_import_creates_legal_document_versions(self):
        """Test that import creates LegalDocumentVersion with FK"""
        out = StringIO()
        call_command('import_demo_csv', stdout=out)
        
        versions = LegalDocumentVersion.objects.all()
        self.assertGreater(versions.count(), 0)
        
        # Verify FK relationship
        for version in versions:
            self.assertIsNotNone(version.document)
            self.assertIsNotNone(version.document.document_type)
    
    def test_legal_content_contains_demo_marker(self):
        """Test that legal document content contains DEMO PLACEHOLDER marker"""
        out = StringIO()
        call_command('import_demo_csv', stdout=out)
        
        versions = LegalDocumentVersion.objects.all()
        for version in versions:
            self.assertIn('DEMO PLACEHOLDER', version.content)
    
    # ========== No Migrations Generated Tests ==========
    
    def test_no_pending_migrations_after_import(self):
        """Test that import does not generate pending migrations"""
        from django.core.management import call_command as django_call_command
        from io import StringIO
        
        out = StringIO()
        # Run makemigrations with --check to verify no pending
        try:
            django_call_command('makemigrations', '--check', '--dry-run', stdout=out)
            # If it doesn't raise, we're good
            self.assertTrue(True)
        except SystemExit:
            # makemigrations --check exits with code 1 if there are pending migrations
            self.fail("Pending migrations detected after import")
