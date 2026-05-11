import pytest
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
import uuid

from apps.catalog.models import ProductCategory, Product
from apps.shipping.models import ShippingZone, ShippingMethod
from apps.payments.models import PaymentMethod
from apps.legal.models import LegalDocument, LegalDocumentVersion

User = get_user_model()


class HealthCheckAPITest(TestCase):
    """Tests for health check endpoint."""
    
    def setUp(self):
        self.client = Client()
    
    def test_health_check_returns_200(self):
        """Test health endpoint returns 200."""
        response = self.client.get('/api/v1/health/')
        assert response.status_code == 200
    
    def test_health_check_has_success_true(self):
        """Test health response has success=true."""
        response = self.client.get('/api/v1/health/')
        data = response.json()
        assert data['success'] is True
    
    def test_health_check_has_data(self):
        """Test health response has data with status, service, version."""
        response = self.client.get('/api/v1/health/')
        data = response.json()
        assert 'data' in data
        assert data['data']['status'] == 'ok'
        assert data['data']['service'] == 'alice-wonder-nails-api'
        assert data['data']['version'] == 'v1'
        assert data['data']['environment'] == 'local-dev'
    
    def test_health_check_no_secrets(self):
        """Test health response contains no secrets or env values."""
        response = self.client.get('/api/v1/health/')
        data = response.json()
        response_str = str(data).lower()
        assert 'secret' not in response_str
        assert 'password' not in response_str
        assert 'key' not in response_str.split('version')[0]  # version is ok


class CatalogCategoriesAPITest(TestCase):
    """Tests for catalog categories endpoint."""
    
    def setUp(self):
        self.client = Client()
        self.category = ProductCategory.objects.create(
            name='Test Category',
            slug='test-category',
            sort_order=1
        )
    
    def test_categories_returns_200(self):
        """Test categories endpoint returns 200."""
        response = self.client.get('/api/v1/catalog/categories/')
        assert response.status_code == 200
    
    def test_categories_has_success_true(self):
        """Test categories response has success=true."""
        response = self.client.get('/api/v1/catalog/categories/')
        data = response.json()
        assert data['success'] is True
    
    def test_categories_returns_categories(self):
        """Test categories response contains category data."""
        response = self.client.get('/api/v1/catalog/categories/')
        data = response.json()
        assert 'data' in data
        assert len(data['data']) >= 1
        category = data['data'][0]
        assert 'id' in category
        assert 'name' in category
        assert 'slug' in category


class CatalogProductsAPITest(TestCase):
    """Tests for catalog products endpoint."""
    
    def setUp(self):
        self.client = Client()
        self.category = ProductCategory.objects.create(
            name='Test Category',
            slug='test-category',
        )
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            slug='test-product',
            product_type=Product.ProductType.GEL,
            is_active=True,
            visibility=Product.Visibility.PUBLIC,
        )
    
    def test_products_returns_200(self):
        """Test products endpoint returns 200."""
        response = self.client.get('/api/v1/catalog/products/')
        assert response.status_code == 200
    
    def test_products_has_success_true(self):
        """Test products response has success=true."""
        response = self.client.get('/api/v1/catalog/products/')
        data = response.json()
        assert data['success'] is True
    
    def test_products_returns_products(self):
        """Test products response contains product data."""
        response = self.client.get('/api/v1/catalog/products/')
        data = response.json()
        assert 'data' in data
        assert len(data['data']) >= 1
        product = data['data'][0]
        assert 'id' in product
        assert 'name' in product
        assert 'slug' in product
    
    def test_products_accepts_customer_group_b2c(self):
        """Test products endpoint accepts customer_group=b2c."""
        response = self.client.get('/api/v1/catalog/products/?customer_group=b2c')
        assert response.status_code == 200
    
    def test_products_accepts_customer_group_b2b(self):
        """Test products endpoint accepts customer_group=b2b."""
        response = self.client.get('/api/v1/catalog/products/?customer_group=b2b')
        assert response.status_code == 200
    
    def test_products_rejects_invalid_customer_group(self):
        """Test products endpoint rejects invalid customer_group."""
        response = self.client.get('/api/v1/catalog/products/?customer_group=invalid')
        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
        assert 'error' in data


class CatalogProductDetailAPITest(TestCase):
    """Tests for catalog product detail endpoint."""
    
    def setUp(self):
        self.client = Client()
        self.category = ProductCategory.objects.create(
            name='Test Category',
            slug='test-category',
        )
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            slug='test-product',
            product_type=Product.ProductType.GEL,
            is_active=True,
            visibility=Product.Visibility.PUBLIC,
        )
    
    def test_product_detail_returns_200(self):
        """Test product detail endpoint returns 200 for existing product."""
        response = self.client.get(f'/api/v1/catalog/products/{self.product.slug}/')
        assert response.status_code == 200
    
    def test_product_detail_has_success_true(self):
        """Test product detail response has success=true."""
        response = self.client.get(f'/api/v1/catalog/products/{self.product.slug}/')
        data = response.json()
        assert data['success'] is True
    
    def test_product_detail_returns_404_for_missing_product(self):
        """Test product detail endpoint returns 404 for non-existent product."""
        response = self.client.get('/api/v1/catalog/products/nonexistent-product/')
        assert response.status_code == 404
        data = response.json()
        assert data['success'] is False
    
    def test_product_detail_returns_product_data(self):
        """Test product detail response contains product data."""
        response = self.client.get(f'/api/v1/catalog/products/{self.product.slug}/')
        data = response.json()
        product = data['data']
        assert product['id'] == self.product.id
        assert product['name'] == self.product.name
        assert product['slug'] == self.product.slug


class ShippingMethodsAPITest(TestCase):
    """Tests for shipping methods endpoint."""
    
    def setUp(self):
        self.client = Client()
        self.zone = ShippingZone.objects.create(
            name='Germany',
            code='DE',
            countries=['DE'],
            is_active=True,
        )
        self.method = ShippingMethod.objects.create(
            zone=self.zone,
            name='Standard Shipping',
            code='standard',
            customer_group='b2c',
            base_price='5.00',
            currency='EUR',
            is_active=True,
        )
    
    def test_shipping_methods_returns_200(self):
        """Test shipping methods endpoint returns 200."""
        response = self.client.get('/api/v1/shipping/methods/')
        assert response.status_code == 200
    
    def test_shipping_methods_has_success_true(self):
        """Test shipping methods response has success=true."""
        response = self.client.get('/api/v1/shipping/methods/')
        data = response.json()
        assert data['success'] is True
    
    def test_shipping_methods_accepts_customer_group_b2c(self):
        """Test shipping methods endpoint accepts customer_group=b2c."""
        response = self.client.get('/api/v1/shipping/methods/?customer_group=b2c')
        assert response.status_code == 200
    
    def test_shipping_methods_rejects_invalid_customer_group(self):
        """Test shipping methods endpoint rejects invalid customer_group."""
        response = self.client.get('/api/v1/shipping/methods/?customer_group=invalid')
        assert response.status_code == 400


class PaymentMethodsAPITest(TestCase):
    """Tests for payment methods endpoint."""
    
    def setUp(self):
        self.client = Client()
        self.method = PaymentMethod.objects.create(
            name='Credit Card',
            code='credit-card',
            provider='stripe',
            customer_group='b2c',
            is_active=True,
        )
    
    def test_payment_methods_returns_200(self):
        """Test payment methods endpoint returns 200."""
        response = self.client.get('/api/v1/payments/methods/')
        assert response.status_code == 200
    
    def test_payment_methods_has_success_true(self):
        """Test payment methods response has success=true."""
        response = self.client.get('/api/v1/payments/methods/')
        data = response.json()
        assert data['success'] is True
    
    def test_payment_methods_accepts_customer_group_b2c(self):
        """Test payment methods endpoint accepts customer_group=b2c."""
        response = self.client.get('/api/v1/payments/methods/?customer_group=b2c')
        assert response.status_code == 200
    
    def test_payment_methods_rejects_invalid_customer_group(self):
        """Test payment methods endpoint rejects invalid customer_group."""
        response = self.client.get('/api/v1/payments/methods/?customer_group=invalid')
        assert response.status_code == 400


class LegalActiveAPITest(TestCase):
    """Tests for legal active documents endpoint."""
    
    def setUp(self):
        self.client = Client()
    
    def test_legal_active_returns_200(self):
        """Test legal active endpoint returns 200."""
        response = self.client.get('/api/v1/legal/active/')
        assert response.status_code == 200
    
    def test_legal_active_has_success_true(self):
        """Test legal active response has success=true."""
        response = self.client.get('/api/v1/legal/active/')
        data = response.json()
        assert data['success'] is True
    
    def test_legal_active_accepts_customer_group_b2c(self):
        """Test legal active endpoint accepts customer_group=b2c."""
        response = self.client.get('/api/v1/legal/active/?customer_group=b2c')
        assert response.status_code == 200
    
    def test_legal_active_rejects_invalid_customer_group(self):
        """Test legal active endpoint rejects invalid customer_group."""
        response = self.client.get('/api/v1/legal/active/?customer_group=invalid')
        assert response.status_code == 400


class APIBoundariesTest(TestCase):
    """Tests for API boundaries and restrictions."""
    
    def setUp(self):
        self.client = Client()
    
    def test_post_not_allowed_on_health(self):
        """Test POST is not allowed on health endpoint."""
        response = self.client.post('/api/v1/health/')
        assert response.status_code in [405, 400]  # Method not allowed or bad request
    
    def test_post_not_allowed_on_products(self):
        """Test POST is not allowed on products endpoint."""
        response = self.client.post('/api/v1/catalog/products/')
        assert response.status_code in [405, 400]
    
    def test_post_not_allowed_on_shipping(self):
        """Test POST is not allowed on shipping endpoint."""
        response = self.client.post('/api/v1/shipping/methods/')
        assert response.status_code in [405, 400]
    
    def test_post_not_allowed_on_payments(self):
        """Test POST is not allowed on payments endpoint."""
        response = self.client.post('/api/v1/payments/methods/')
        assert response.status_code in [405, 400]
