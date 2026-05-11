from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Health check
    path('v1/health/', views.health, name='health'),
    
    # Catalog endpoints (read-only)
    path('v1/catalog/categories/', views.catalog_categories, name='catalog-categories'),
    path('v1/catalog/products/', views.catalog_products, name='catalog-products'),
    path('v1/catalog/products/<slug:slug>/', views.catalog_product_detail, name='catalog-product-detail'),
    
    # Shipping endpoints (read-only)
    path('v1/shipping/methods/', views.shipping_methods, name='shipping-methods'),
    
    # Payment endpoints (read-only)
    path('v1/payments/methods/', views.payment_methods, name='payment-methods'),
    
    # Legal endpoints (read-only)
    path('v1/legal/active/', views.legal_active, name='legal-active'),
    
    # Pricing endpoints (read-only, v1.1 extension)
    path('v1/pricing/products/<slug:slug>/prices/', views.pricing_products_by_slug, name='pricing-products-prices'),
]
