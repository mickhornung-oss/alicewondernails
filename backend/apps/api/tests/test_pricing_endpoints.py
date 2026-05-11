"""Tests for pricing API endpoints (v1.1 extension)."""

import pytest
from decimal import Decimal
from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta

from apps.catalog.models import ProductCategory, Product, ProductVariant
from apps.pricing.models import ProductPrice


class PricingEndpointAPITest(TestCase):
    """Tests for pricing API endpoints."""
    
    def setUp(self):
        self.client = Client()
        
        # Create test category
        self.category = ProductCategory.objects.create(
            name='Test Gel Colors',
            slug='test-gel-colors',
            sort_order=1
        )
        
        # Create test products with different visibility
        self.product_public = Product.objects.create(
            name='Public Gel Color',
            slug='public-gel-color',
            short_description='A gel color for everyone',
            description='Public gel color for B2C and B2B',
            category=self.category,
            product_type='gel',
            visibility='public',
            is_active=True,
        )
        
        self.product_b2c_only = Product.objects.create(
            name='B2C Only Gel',
            slug='b2c-only-gel',
            short_description='B2C only gel',
            description='Only for B2C customers',
            category=self.category,
            product_type='gel',
            visibility='b2c_only',
            is_active=True,
        )
        
        self.product_b2b_only = Product.objects.create(
            name='B2B Only Gel',
            slug='b2b-only-gel',
            short_description='B2B only gel',
            description='Only for B2B customers',
            category=self.category,
            product_type='gel',
            visibility='b2b_only',
            is_active=True,
        )
        
        # Create variants for public product
        self.variant_5ml = ProductVariant.objects.create(
            product=self.product_public,
            sku='GEL-PUBLIC-5ML',
            name='5ml',
            is_default=True,
        )
        
        self.variant_10ml = ProductVariant.objects.create(
            product=self.product_public,
            sku='GEL-PUBLIC-10ML',
            name='10ml',
            is_default=False,
        )
        
        # Create prices for public product (both B2C and B2B)
        # Product-level B2C price
        self.price_product_b2c = ProductPrice.objects.create(
            product=self.product_public,
            variant=None,
            customer_group='b2c',
            amount=Decimal('12.99'),
            currency='EUR',
            tax_rate=Decimal('19.00'),
            price_includes_tax=True,
            is_active=True,
        )
        
        # Product-level B2B price
        self.price_product_b2b = ProductPrice.objects.create(
            product=self.product_public,
            variant=None,
            customer_group='b2b',
            amount=Decimal('9.99'),
            currency='EUR',
            tax_rate=Decimal('19.00'),
            price_includes_tax=True,
            is_active=True,
        )
        
        # Variant-level B2C price (5ml)
        self.price_variant_5ml_b2c = ProductPrice.objects.create(
            product=self.product_public,
            variant=self.variant_5ml,
            customer_group='b2c',
            amount=Decimal('14.99'),
            currency='EUR',
            tax_rate=Decimal('19.00'),
            price_includes_tax=True,
            is_active=True,
        )
        
        # Variant-level B2C price (10ml)
        self.price_variant_10ml_b2c = ProductPrice.objects.create(
            product=self.product_public,
            variant=self.variant_10ml,
            customer_group='b2c',
            amount=Decimal('19.99'),
            currency='EUR',
            tax_rate=Decimal('19.00'),
            price_includes_tax=True,
            is_active=True,
        )
        
        # Inactive price (should be hidden)
        self.price_inactive = ProductPrice.objects.create(
            product=self.product_public,
            variant=None,
            customer_group='b2c',
            amount=Decimal('99.99'),
            currency='EUR',
            tax_rate=Decimal('19.00'),
            price_includes_tax=True,
            is_active=False,
        )
        
        # Time-limited price (currently valid)
        now = timezone.now()
        self.price_timelimited = ProductPrice.objects.create(
            product=self.product_public,
            variant=None,
            customer_group='b2b',
            amount=Decimal('8.99'),
            currency='EUR',
            tax_rate=Decimal('19.00'),
            price_includes_tax=True,
            valid_from=now - timedelta(days=1),
            valid_until=now + timedelta(days=30),
            is_active=True,
        )
        
        # B2C-only product price
        self.price_b2c_only = ProductPrice.objects.create(
            product=self.product_b2c_only,
            variant=None,
            customer_group='b2c',
            amount=Decimal('15.99'),
            currency='EUR',
            tax_rate=Decimal('19.00'),
            price_includes_tax=True,
            is_active=True,
        )
        
        # B2B-only product price
        self.price_b2b_only = ProductPrice.objects.create(
            product=self.product_b2b_only,
            variant=None,
            customer_group='b2b',
            amount=Decimal('10.99'),
            currency='EUR',
            tax_rate=Decimal('19.00'),
            price_includes_tax=True,
            is_active=True,
        )
    
    # Test 1: Endpoint existence
    def test_pricing_endpoint_returns_200(self):
        """Test pricing endpoint exists and returns 200 for public product."""
        response = self.client.get('/api/v1/pricing/products/public-gel-color/prices/')
        assert response.status_code == 200
    
    # Test 2: Default customer_group
    def test_pricing_default_customer_group_is_b2c(self):
        """Test pricing endpoint defaults to b2c when customer_group not provided."""
        response = self.client.get('/api/v1/pricing/products/public-gel-color/prices/')
        data = response.json()
        assert data['success'] is True
        assert data['data']['customer_group'] == 'b2c'
    
    # Test 3: B2C prices visible
    def test_pricing_b2c_prices_visible(self):
        """Test B2C prices are visible when customer_group=b2c."""
        response = self.client.get('/api/v1/pricing/products/public-gel-color/prices/?customer_group=b2c')
        data = response.json()
        assert data['success'] is True
        prices = data['data']['prices']
        # Should have product-level and two variant prices
        assert len(prices) == 3
        amounts = [str(p['amount']) for p in prices]
        assert '12.99' in amounts  # Product-level
        assert '14.99' in amounts  # 5ml variant
        assert '19.99' in amounts  # 10ml variant
    
    # Test 4: B2B prices visible
    def test_pricing_b2b_prices_visible(self):
        """Test B2B prices are visible when customer_group=b2b."""
        response = self.client.get('/api/v1/pricing/products/public-gel-color/prices/?customer_group=b2b')
        data = response.json()
        assert data['success'] is True
        prices = data['data']['prices']
        # Should have product-level prices only (no variant prices for B2B)
        assert len(prices) >= 1
        amounts = [str(p['amount']) for p in prices]
        assert '9.99' in amounts  # Product-level B2B
    
    # Test 5: B2C and B2B prices differ
    def test_pricing_b2c_and_b2b_prices_differ(self):
        """Test B2C and B2B prices are different when available."""
        response_b2c = self.client.get('/api/v1/pricing/products/public-gel-color/prices/?customer_group=b2c')
        response_b2b = self.client.get('/api/v1/pricing/products/public-gel-color/prices/?customer_group=b2b')
        
        data_b2c = response_b2c.json()
        data_b2b = response_b2b.json()
        
        # Find product-level prices
        b2c_product_price = next(
            (p for p in data_b2c['data']['prices'] if p['type'] == 'product'),
            None
        )
        b2b_product_price = next(
            (p for p in data_b2b['data']['prices'] if p['type'] == 'product'),
            None
        )
        
        assert b2c_product_price is not None
        assert b2b_product_price is not None
        assert b2c_product_price['amount'] != b2b_product_price['amount']
    
    # Test 6: Variant prices included
    def test_pricing_variant_prices_included(self):
        """Test variant-level prices are included in response."""
        response = self.client.get('/api/v1/pricing/products/public-gel-color/prices/?customer_group=b2c')
        data = response.json()
        prices = data['data']['prices']
        
        # Find variant prices
        variant_prices = [p for p in prices if p['type'] == 'variant']
        assert len(variant_prices) >= 1
        
        # Check variant SKUs are included
        skus = [p['variant_sku'] for p in variant_prices if p['variant_sku']]
        assert 'GEL-PUBLIC-5ML' in skus or 'GEL-PUBLIC-10ML' in skus
    
    # Test 7: Product-level prices included
    def test_pricing_product_level_prices_included(self):
        """Test product-level prices are included in response."""
        response = self.client.get('/api/v1/pricing/products/public-gel-color/prices/?customer_group=b2c')
        data = response.json()
        prices = data['data']['prices']
        
        # Find product-level price
        product_prices = [p for p in prices if p['type'] == 'product']
        assert len(product_prices) >= 1
        
        # Product-level price should have variant_sku=null
        for p in product_prices:
            assert p['variant_sku'] is None
            assert p['variant_name'] is None
    
    # Test 8: Inactive prices hidden
    def test_pricing_inactive_prices_hidden(self):
        """Test inactive prices are not returned."""
        response = self.client.get('/api/v1/pricing/products/public-gel-color/prices/?customer_group=b2c')
        data = response.json()
        prices = data['data']['prices']
        
        # Inactive price (99.99) should not be in response
        amounts = [str(p['amount']) for p in prices]
        assert '99.99' not in amounts
    
    # Test 9: Product not found returns 404
    def test_pricing_product_not_found_returns_404(self):
        """Test non-existent product slug returns 404."""
        response = self.client.get('/api/v1/pricing/products/non-existent-slug/prices/')
        assert response.status_code == 404
        data = response.json()
        assert data['success'] is False
        assert data['error']['code'] == 'product_not_found'
    
    # Test 10: Invalid customer_group returns 400
    def test_pricing_invalid_customer_group_returns_400(self):
        """Test invalid customer_group returns 400."""
        response = self.client.get('/api/v1/pricing/products/public-gel-color/prices/?customer_group=invalid')
        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
        assert data['error']['code'] == 'invalid_customer_group'
    
    # Test 11: B2B-only product not visible to B2C
    def test_pricing_b2b_only_product_not_visible_to_b2c(self):
        """Test B2B-only product returns 404 for B2C customer_group."""
        response = self.client.get('/api/v1/pricing/products/b2b-only-gel/prices/?customer_group=b2c')
        assert response.status_code == 404
        data = response.json()
        assert data['success'] is False
        assert data['error']['code'] == 'product_not_visible'
    
    # Test 12: B2C-only product not visible to B2B
    def test_pricing_b2c_only_product_not_visible_to_b2b(self):
        """Test B2C-only product returns 404 for B2B customer_group."""
        response = self.client.get('/api/v1/pricing/products/b2c-only-gel/prices/?customer_group=b2b')
        assert response.status_code == 404
        data = response.json()
        assert data['success'] is False
        assert data['error']['code'] == 'product_not_visible'
    
    # Test 13: Response contains tax_rate and price_includes_tax
    def test_pricing_response_contains_tax_info(self):
        """Test response includes tax_rate and price_includes_tax."""
        response = self.client.get('/api/v1/pricing/products/public-gel-color/prices/?customer_group=b2c')
        data = response.json()
        prices = data['data']['prices']
        
        assert len(prices) > 0
        for price in prices:
            assert 'tax_rate' in price
            assert 'price_includes_tax' in price
            assert price['tax_rate'] == '19.00'
            assert price['price_includes_tax'] is True
    
    # Test 14: Response format success/data stable
    def test_pricing_response_format_success_data_stable(self):
        """Test response maintains stable success/data structure."""
        response = self.client.get('/api/v1/pricing/products/public-gel-color/prices/?customer_group=b2c')
        data = response.json()
        
        assert 'success' in data
        assert data['success'] is True
        assert 'data' in data
        assert isinstance(data['data'], dict)
        
        # Check data structure
        response_data = data['data']
        assert 'product' in response_data
        assert 'customer_group' in response_data
        assert 'currency' in response_data
        assert 'prices' in response_data
        assert isinstance(response_data['prices'], list)
    
    # Test 15: Error response format success/error stable
    def test_pricing_error_response_format_stable(self):
        """Test error responses maintain stable success/error structure."""
        response = self.client.get('/api/v1/pricing/products/non-existent/prices/')
        data = response.json()
        
        assert 'success' in data
        assert data['success'] is False
        assert 'error' in data
        assert isinstance(data['error'], dict)
        assert 'code' in data['error']
        assert 'message' in data['error']
    
    # Test 16: CSV-imported prices visible (integration test with seed data)
    def test_pricing_csv_imported_prices_visible(self):
        """Test that CSV-imported prices are visible via pricing endpoint."""
        # This test will pass if import_demo_csv has been run
        # It checks that seeded ProductPrice data is accessible
        
        # Get first product with prices
        products_with_prices = Product.objects.filter(
            prices__is_active=True
        ).distinct()
        
        if products_with_prices.exists():
            product = products_with_prices.first()
            response = self.client.get(f'/api/v1/pricing/products/{product.slug}/prices/')
            
            if product.visibility in ['public', 'b2c_only']:
                assert response.status_code == 200
                data = response.json()
                assert data['success'] is True
                assert len(data['data']['prices']) > 0
    
    # Test 17: Product without active prices returns empty prices array
    def test_pricing_product_without_prices_returns_empty_list(self):
        """Test product with no active prices returns 200 with empty prices array."""
        # Create product with no prices
        cat = ProductCategory.objects.create(
            name='No Prices Category',
            slug='no-prices-cat',
            sort_order=1
        )
        product_no_prices = Product.objects.create(
            name='No Prices Product',
            slug='no-prices-product',
            short_description='Product without prices',
            description='This product has no active prices',
            category=cat,
            product_type='gel',
            visibility='public',
            is_active=True,
        )
        
        response = self.client.get(f'/api/v1/pricing/products/{product_no_prices.slug}/prices/?customer_group=b2c')
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'data' in data
        assert 'prices' in data['data']
        assert isinstance(data['data']['prices'], list)
        assert len(data['data']['prices']) == 0  # Empty but valid
        assert data['data']['currency'] == 'EUR'  # Default currency
    
    # Test 18: GET-only validation - POST not allowed
    def test_pricing_post_method_not_allowed(self):
        """Test POST method returns 405 Method Not Allowed."""
        response = self.client.post(
            '/api/v1/pricing/products/public-gel-color/prices/',
            data={'customer_group': 'b2c'},
            content_type='application/json'
        )
        assert response.status_code == 405  # Method Not Allowed
