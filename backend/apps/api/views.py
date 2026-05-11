from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK
from django.utils import timezone

from apps.catalog.models import ProductCategory, Product
from apps.shipping.services import get_available_shipping_methods
from apps.payments.services import get_available_payment_methods
from apps.legal.services import get_active_document_version

from .serializers import (
    HealthSerializer,
    ProductCategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ShippingMethodSerializer,
    PaymentMethodSerializer,
    LegalDocumentVersionSerializer,
)
from .pricing_serializers import (
    ProductPriceSerializer,
)


def api_response_success(data, status=HTTP_200_OK):
    """Helper to format successful API response."""
    return Response({
        'success': True,
        'data': data
    }, status=status)


def api_response_error(code, message, status=HTTP_400_BAD_REQUEST):
    """Helper to format error API response."""
    return Response({
        'success': False,
        'error': {
            'code': code,
            'message': message
        }
    }, status=status)


@api_view(['GET'])
def health(request):
    """
    Health check endpoint.
    
    Returns:
        - status: "ok"
        - service name
        - API version
        - environment (local-dev)
    """
    data = {
        'status': 'ok',
        'service': 'alice-wonder-nails-api',
        'version': 'v1',
        'environment': 'local-dev',
    }
    serializer = HealthSerializer(data)
    return api_response_success(serializer.data)


@api_view(['GET'])
def catalog_categories(request):
    """
    Get list of product categories.
    
    Returns:
        List of active categories with id, name, slug, sort_order
    """
    try:
        categories = ProductCategory.objects.all().order_by('sort_order', 'name')
        serializer = ProductCategorySerializer(categories, many=True)
        return api_response_success(serializer.data)
    except Exception as e:
        return api_response_error('catalog_error', f'Failed to fetch categories: {str(e)}')


@api_view(['GET'])
def catalog_products(request):
    """
    Get list of products.
    
    Query parameters:
        - customer_group: 'b2c' or 'b2b' (default: b2c)
        - category: category slug (optional)
    
    Returns:
        List of products with id, name, slug, description, category, variants
    """
    customer_group = request.query_params.get('customer_group', 'b2c')
    category_slug = request.query_params.get('category')
    
    # Validate customer_group
    if customer_group not in ['b2c', 'b2b']:
        return api_response_error(
            'invalid_customer_group',
            f'customer_group must be "b2c" or "b2b", got "{customer_group}"',
            status=HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get base queryset
        products = Product.objects.filter(is_active=True).prefetch_related('variants')
        
        # Filter by category if provided
        if category_slug:
            products = products.filter(category__slug=category_slug)
        
        # Filter by customer group visibility based on visibility field
        if customer_group == 'b2c':
            products = products.filter(visibility__in=['public', 'b2c_only'])
        elif customer_group == 'b2b':
            products = products.filter(visibility__in=['public', 'b2b_only'])
        
        serializer = ProductListSerializer(products, many=True)
        return api_response_success(serializer.data)
    except Exception as e:
        return api_response_error('catalog_error', f'Failed to fetch products: {str(e)}')


@api_view(['GET'])
def catalog_product_detail(request, slug):
    """
    Get product detail by slug.
    
    Parameters:
        - slug: product slug
    
    Query parameters:
        - customer_group: 'b2c' or 'b2b' (default: b2c)
    
    Returns:
        Product with id, name, slug, description, category, variants
    """
    customer_group = request.query_params.get('customer_group', 'b2c')
    
    # Validate customer_group
    if customer_group not in ['b2c', 'b2b']:
        return api_response_error(
            'invalid_customer_group',
            f'customer_group must be "b2c" or "b2b", got "{customer_group}"',
            status=HTTP_400_BAD_REQUEST
        )
    
    try:
        product = Product.objects.get(slug=slug, is_active=True)
        
        # Check visibility for customer group
        if customer_group == 'b2c':
            if product.visibility not in ['public', 'b2c_only']:
                return api_response_error(
                    'product_not_visible',
                    f'Product not visible for customer group: {customer_group}',
                    status=HTTP_404_NOT_FOUND
                )
        elif customer_group == 'b2b':
            if product.visibility not in ['public', 'b2b_only']:
                return api_response_error(
                    'product_not_visible',
                    f'Product not visible for customer group: {customer_group}',
                    status=HTTP_404_NOT_FOUND
                )
        
        serializer = ProductDetailSerializer(product)
        return api_response_success(serializer.data)
    except Product.DoesNotExist:
        return api_response_error(
            'product_not_found',
            f'Product with slug "{slug}" not found',
            status=HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return api_response_error('catalog_error', f'Failed to fetch product: {str(e)}')


@api_view(['GET'])
def shipping_methods(request):
    """
    Get available shipping methods.
    
    Query parameters:
        - country: country code (default: DE)
        - customer_group: 'b2c' or 'b2b' (default: b2c)
    
    Returns:
        List of shipping methods with id, name, code, customer_group, base_price, currency, etc.
    """
    country = request.query_params.get('country', 'DE')
    customer_group = request.query_params.get('customer_group', 'b2c')
    
    # Validate customer_group
    if customer_group not in ['b2c', 'b2b']:
        return api_response_error(
            'invalid_customer_group',
            f'customer_group must be "b2c" or "b2b", got "{customer_group}"',
            status=HTTP_400_BAD_REQUEST
        )
    
    try:
        methods = get_available_shipping_methods(
            country_code=country,
            customer_group=customer_group,
        )
        serializer = ShippingMethodSerializer(methods, many=True)
        return api_response_success(serializer.data)
    except Exception as e:
        return api_response_error('shipping_error', f'Failed to fetch shipping methods: {str(e)}')


@api_view(['GET'])
def payment_methods(request):
    """
    Get available payment methods.
    
    Query parameters:
        - customer_group: 'b2c' or 'b2b' (default: b2c)
    
    Returns:
        List of payment methods with id, name, code, provider, customer_group, description
    """
    customer_group = request.query_params.get('customer_group', 'b2c')
    
    # Validate customer_group
    if customer_group not in ['b2c', 'b2b']:
        return api_response_error(
            'invalid_customer_group',
            f'customer_group must be "b2c" or "b2b", got "{customer_group}"',
            status=HTTP_400_BAD_REQUEST
        )
    
    try:
        methods = get_available_payment_methods(customer_group=customer_group)
        serializer = PaymentMethodSerializer(methods, many=True)
        return api_response_success(serializer.data)
    except Exception as e:
        return api_response_error('payment_error', f'Failed to fetch payment methods: {str(e)}')


@api_view(['GET'])
def legal_active(request):
    """
    Get active legal documents (metadata only).
    
    Query parameters:
        - customer_group: 'b2c' or 'b2b' (default: b2c)
    
    Returns:
        List of active legal documents with document_type, title, version, target_group, effective_from
    """
    customer_group = request.query_params.get('customer_group', 'b2c')
    
    # Validate customer_group
    if customer_group not in ['b2c', 'b2b']:
        return api_response_error(
            'invalid_customer_group',
            f'customer_group must be "b2c" or "b2b", got "{customer_group}"',
            status=HTTP_400_BAD_REQUEST
        )
    
    try:
        from apps.legal.models import LegalDocument, LegalDocumentVersion
        
        # Get active document versions for target group
        active_versions = LegalDocumentVersion.objects.filter(
            status='active',
            document__target_group__in=['all', customer_group]
        ).select_related('document')
        
        serializer = LegalDocumentVersionSerializer(active_versions, many=True)
        return api_response_success(serializer.data)
    except Exception as e:
        return api_response_error('legal_error', f'Failed to fetch legal documents: {str(e)}')


@api_view(['GET'])
def pricing_products_by_slug(request, slug):
    """
    Get available prices for a product.
    
    URL parameters:
        - slug: product slug
    
    Query parameters:
        - customer_group: 'b2c' or 'b2b' (default: b2c)
    
    Returns:
        Product metadata with all active prices for the given customer_group.
        Includes product-level and variant-level prices.
    
    Errors:
        - 400: Invalid customer_group
        - 404: Product not found or not visible for customer_group
    """
    customer_group = request.query_params.get('customer_group', 'b2c')
    
    # Validate customer_group
    if customer_group not in ['b2c', 'b2b']:
        return api_response_error(
            'invalid_customer_group',
            f'customer_group must be "b2c" or "b2b", got "{customer_group}"',
            status=HTTP_400_BAD_REQUEST
        )
    
    try:
        from apps.pricing.models import ProductPrice
        from django.db.models import Q, F, Case, When, Value, BooleanField
        
        # Get product by slug
        try:
            product = Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return api_response_error(
                'product_not_found',
                f'Product with slug "{slug}" not found',
                status=HTTP_404_NOT_FOUND
            )
        
        # Check product visibility for customer_group
        if customer_group == 'b2c':
            if product.visibility not in ['public', 'b2c_only']:
                return api_response_error(
                    'product_not_visible',
                    f'Product not visible for customer group: {customer_group}',
                    status=HTTP_404_NOT_FOUND
                )
        elif customer_group == 'b2b':
            if product.visibility not in ['public', 'b2b_only']:
                return api_response_error(
                    'product_not_visible',
                    f'Product not visible for customer group: {customer_group}',
                    status=HTTP_404_NOT_FOUND
                )
        
        # Get active prices for this product and customer_group
        now = timezone.now()
        
        prices = ProductPrice.objects.filter(
            product=product,
            customer_group=customer_group,
            is_active=True,
        ).filter(
            Q(valid_from__isnull=True) | Q(valid_from__lte=now),
            Q(valid_until__isnull=True) | Q(valid_until__gte=now),
        ).select_related('variant')
        
        # Sort in Python: product-level prices first, then by variant sku/name
        prices_list = list(prices)
        prices_list.sort(key=lambda p: (
            p.variant_id is not None,  # False (0) comes before True (1), so product-level first
            p.variant.sku if p.variant_id else '',
            p.variant.name if p.variant_id else '',
        ))
        
        # Determine currency from first price or default
        currency = prices_list[0].currency if prices_list else 'EUR'
        
        # Serialize prices
        serializer = ProductPriceSerializer(prices_list, many=True)
        price_data = serializer.data
        
        # Build response data
        response_data = {
            'product': {
                'slug': product.slug,
                'name': product.name,
            },
            'customer_group': customer_group,
            'currency': currency,
            'prices': price_data,
        }
        
        return api_response_success(response_data)
    
    except Exception as e:
        return api_response_error('pricing_error', f'Failed to fetch prices: {str(e)}')
