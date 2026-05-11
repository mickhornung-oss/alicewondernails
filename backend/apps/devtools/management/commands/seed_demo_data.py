from django.core.management.base import BaseCommand
from django.db import transaction
from apps.catalog.models import ProductCategory, Product, ProductVariant
from apps.pricing.models import ProductPrice
from apps.shipping.models import ShippingZone, ShippingMethod
from apps.payments.models import PaymentMethod
from apps.legal.models import LegalDocument, LegalDocumentVersion
from apps.consent.models import ConsentCategory


class Command(BaseCommand):
    """
    Seed database with realistic demo data for local development.
    
    This command is IDEMPOTENT:
    - Can be run multiple times without creating duplicates
    - Skips existing data based on unique fields (slug, code)
    - Prints clear summary of created vs. skipped items
    
    IMPORTANT:
    - No --force flag (no data deletion)
    - No test users, addresses, or orders
    - Demo data only for catalog, pricing, shipping, payments, legal, consent
    - All legal documents marked as DEMO PLACEHOLDER - NOT FOR PRODUCTION
    """
    
    help = 'Seed database with demo data for local development (idempotent, no data deletion)'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting demo data seed (idempotent mode)...\n'))
        
        with transaction.atomic():
            stats = {
                'categories': {'created': 0, 'skipped': 0},
                'products': {'created': 0, 'skipped': 0},
                'variants': {'created': 0, 'skipped': 0},
                'prices': {'created': 0, 'skipped': 0},
                'zones': {'created': 0, 'skipped': 0},
                'methods': {'created': 0, 'skipped': 0},
                'payment_methods': {'created': 0, 'skipped': 0},
                'legal_docs': {'created': 0, 'skipped': 0},
                'legal_versions': {'created': 0, 'skipped': 0},
                'consent_categories': {'created': 0, 'skipped': 0},
            }
            
            # Seed categories
            stats['categories'] = self._seed_categories()
            
            # Seed products and variants
            stats['products'] = self._seed_products()
            
            # Seed pricing
            stats['prices'] = self._seed_pricing()
            
            # Seed shipping
            stats['zones'] = self._seed_shipping_zones()
            stats['methods'] = self._seed_shipping_methods()
            
            # Seed payment methods
            stats['payment_methods'] = self._seed_payment_methods()
            
            # Seed legal documents
            legal_stats = self._seed_legal_documents()
            stats['legal_docs'] = legal_stats['docs']
            stats['legal_versions'] = legal_stats['versions']
            
            # Seed consent categories
            stats['consent_categories'] = self._seed_consent_categories()
        
        # Print summary
        self._print_summary(stats)
    
    def _seed_categories(self):
        """Seed product categories."""
        categories_data = [
            {
                'name': 'Nail Colors',
                'slug': 'nail-colors',
                'description': 'Gel colors, polishes, and color-based nail products'
            },
            {
                'name': 'Care Products',
                'slug': 'care-products',
                'description': 'Nail care and maintenance products'
            },
            {
                'name': 'Sets & Bundles',
                'slug': 'sets-bundles',
                'description': 'Curated product sets and bundles'
            },
            {
                'name': 'Accessories',
                'slug': 'accessories',
                'description': 'Nail accessories and tools'
            },
        ]
        
        created, skipped = 0, 0
        for data in categories_data:
            obj, was_created = ProductCategory.objects.get_or_create(
                slug=data['slug'],
                defaults={'name': data['name'], 'description': data.get('description', '')}
            )
            if was_created:
                created += 1
                self.stdout.write(f"  ✓ Created category: {obj.name}")
            else:
                skipped += 1
                self.stdout.write(f"  - Skipped category (exists): {obj.name}")
        
        return {'created': created, 'skipped': skipped}
    
    def _seed_products(self):
        """Seed products and variants."""
        # Get categories
        nail_colors_cat = ProductCategory.objects.get(slug='nail-colors')
        care_cat = ProductCategory.objects.get(slug='care-products')
        bundles_cat = ProductCategory.objects.get(slug='sets-bundles')
        
        products_data = [
            {
                'category': nail_colors_cat,
                'name': 'Gel Color - Rose Gold',
                'slug': 'gel-color-rose-gold',
                'product_type': 'gel',
                'visibility': 'public',
                'variants': [
                    {'name': '5ml Standard', 'sku': 'GEL-RG-5ML', 'is_default': True},
                    {'name': '10ml XL', 'sku': 'GEL-RG-10ML', 'is_default': False},
                ]
            },
            {
                'category': nail_colors_cat,
                'name': 'Polish Classic - Red',
                'slug': 'polish-classic-red',
                'product_type': 'nail_polish',
                'visibility': 'public',
                'variants': [
                    {'name': '15ml', 'sku': 'POLISH-RED-15ML', 'is_default': True},
                ]
            },
            {
                'category': nail_colors_cat,
                'name': 'Polish Pro - Azure',
                'slug': 'polish-pro-azure',
                'product_type': 'nail_polish',
                'visibility': 'b2c_only',
                'variants': [
                    {'name': '15ml', 'sku': 'POLISH-AZURE-15ML', 'is_default': True},
                ]
            },
            {
                'category': care_cat,
                'name': 'Nail Oil - Premium',
                'slug': 'nail-oil-premium',
                'product_type': 'care',
                'visibility': 'public',
                'variants': [
                    {'name': '30ml', 'sku': 'OIL-PREM-30ML', 'is_default': True},
                ]
            },
            {
                'category': care_cat,
                'name': 'Nail Primer',
                'slug': 'nail-primer',
                'product_type': 'care',
                'visibility': 'public',
                'variants': [
                    {'name': '10ml', 'sku': 'PRIMER-10ML', 'is_default': True},
                ]
            },
            {
                'category': bundles_cat,
                'name': 'Starter Set',
                'slug': 'starter-set',
                'product_type': 'set',
                'visibility': 'b2c_only',
                'variants': [
                    {'name': 'Complete', 'sku': 'STARTER-SET-001', 'is_default': True},
                ]
            },
            {
                'category': bundles_cat,
                'name': 'B2B Wholesale Kit',
                'slug': 'b2b-wholesale-kit',
                'product_type': 'set',
                'visibility': 'b2b_only',
                'variants': [
                    {'name': '50pcs', 'sku': 'B2B-KIT-50', 'is_default': True},
                ]
            },
            {
                'category': care_cat,
                'name': 'Nail Strengthener',
                'slug': 'nail-strengthener',
                'product_type': 'care',
                'visibility': 'public',
                'variants': [
                    {'name': '12ml', 'sku': 'STRENGTH-12ML', 'is_default': True},
                ]
            },
        ]
        
        products_created, products_skipped = 0, 0
        variants_created, variants_skipped = 0, 0
        
        for prod_data in products_data:
            variants = prod_data.pop('variants')
            
            product, was_created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults={
                    'category': prod_data['category'],
                    'name': prod_data['name'],
                    'product_type': prod_data['product_type'],
                    'visibility': prod_data['visibility'],
                    'is_active': True,
                }
            )
            
            if was_created:
                products_created += 1
                self.stdout.write(f"  ✓ Created product: {product.name}")
            else:
                products_skipped += 1
                self.stdout.write(f"  - Skipped product (exists): {product.name}")
            
            # Seed variants
            for var_data in variants:
                variant, was_created = ProductVariant.objects.get_or_create(
                    sku=var_data['sku'],
                    defaults={
                        'product': product,
                        'name': var_data['name'],
                        'is_default': var_data.get('is_default', False),
                        'is_active': True,
                    }
                )
                
                if was_created:
                    variants_created += 1
                else:
                    variants_skipped += 1
        
        self.stdout.write(f"  Variants: {variants_created} created, {variants_skipped} skipped\n")
        
        return {
            'created': products_created,
            'skipped': products_skipped
        }
    
    def _seed_pricing(self):
        """Seed product prices for B2C and B2B."""
        pricing_data = [
            {'sku': 'GEL-RG-5ML', 'b2c': 12.99, 'b2b': 8.50},
            {'sku': 'GEL-RG-10ML', 'b2c': 19.99, 'b2b': 13.00},
            {'sku': 'POLISH-RED-15ML', 'b2c': 9.99, 'b2b': 6.50},
            {'sku': 'POLISH-AZURE-15ML', 'b2c': 10.99, 'b2b': None},  # b2c_only
            {'sku': 'OIL-PREM-30ML', 'b2c': 18.99, 'b2b': 12.00},
            {'sku': 'PRIMER-10ML', 'b2c': 8.99, 'b2b': 5.50},
            {'sku': 'STARTER-SET-001', 'b2c': 49.99, 'b2b': None},  # b2c_only
            {'sku': 'B2B-KIT-50', 'b2c': None, 'b2b': 125.00},  # b2b_only
            {'sku': 'STRENGTH-12ML', 'b2c': 11.99, 'b2b': 7.50},
        ]
        
        created, skipped = 0, 0
        
        for price_data in pricing_data:
            variant = ProductVariant.objects.filter(sku=price_data['sku']).first()
            if not variant:
                self.stdout.write(self.style.WARNING(f"  ! Variant not found: {price_data['sku']}"))
                continue
            
            product = variant.product
            
            # B2C price
            if price_data['b2c'] is not None:
                price_obj, was_created = ProductPrice.objects.get_or_create(
                    product=product,
                    variant=variant,
                    customer_group='b2c',
                    defaults={
                        'amount': price_data['b2c'],
                        'currency': 'EUR',
                        'tax_rate': 19.00,
                        'price_includes_tax': True,
                        'is_active': True,
                    }
                )
                if was_created:
                    created += 1
                else:
                    skipped += 1
            
            # B2B price
            if price_data['b2b'] is not None:
                price_obj, was_created = ProductPrice.objects.get_or_create(
                    product=product,
                    variant=variant,
                    customer_group='b2b',
                    defaults={
                        'amount': price_data['b2b'],
                        'currency': 'EUR',
                        'tax_rate': 19.00,
                        'price_includes_tax': True,
                        'is_active': True,
                    }
                )
                if was_created:
                    created += 1
                else:
                    skipped += 1
        
        self.stdout.write(f"  Prices: {created} created, {skipped} skipped\n")
        return {'created': created, 'skipped': skipped}
    
    def _seed_shipping_zones(self):
        """Seed shipping zones."""
        zones_data = [
            {
                'name': 'Germany Standard',
                'code': 'de_std',
                'countries': ['DE'],
            },
            {
                'name': 'EU Extended',
                'code': 'eu_ext',
                'countries': ['AT', 'CH', 'NL', 'BE', 'FR', 'IT'],
            },
        ]
        
        created, skipped = 0, 0
        for zone_data in zones_data:
            zone, was_created = ShippingZone.objects.get_or_create(
                code=zone_data['code'],
                defaults={
                    'name': zone_data['name'],
                    'countries': zone_data['countries'],
                    'is_active': True,
                }
            )
            if was_created:
                created += 1
                self.stdout.write(f"  ✓ Created zone: {zone.name}")
            else:
                skipped += 1
                self.stdout.write(f"  - Skipped zone (exists): {zone.name}")
        
        return {'created': created, 'skipped': skipped}
    
    def _seed_shipping_methods(self):
        """Seed shipping methods."""
        methods_data = [
            {
                'zone_code': 'de_std',
                'name': 'Standard (2-3 days)',
                'code': 'standard_de',
                'base_price_b2c': 4.99,
                'base_price_b2b': 3.50,
                'min_days': 2,
                'max_days': 3,
            },
            {
                'zone_code': 'de_std',
                'name': 'Express (next day)',
                'code': 'express_de',
                'base_price_b2c': 9.99,
                'base_price_b2b': 6.50,
                'min_days': 1,
                'max_days': 1,
            },
            {
                'zone_code': 'de_std',
                'name': 'Overnight',
                'code': 'overnight_de',
                'base_price_b2c': 14.99,
                'base_price_b2b': 10.00,
                'min_days': 0,
                'max_days': 1,
            },
            {
                'zone_code': 'eu_ext',
                'name': 'Standard EU (3-5 days)',
                'code': 'standard_eu',
                'base_price_b2c': 8.99,
                'base_price_b2b': 5.50,
                'min_days': 3,
                'max_days': 5,
            },
            {
                'zone_code': 'eu_ext',
                'name': 'Express EU (2 days)',
                'code': 'express_eu',
                'base_price_b2c': 14.99,
                'base_price_b2b': 9.99,
                'min_days': 2,
                'max_days': 2,
            },
        ]
        
        created, skipped = 0, 0
        
        for method_data in methods_data:
            zone = ShippingZone.objects.get(code=method_data['zone_code'])
            
            # Create two methods: one for B2C, one for B2B (or one for "all")
            for customer_group in ['b2c', 'b2b']:
                price_key = f'base_price_{customer_group}'
                base_price = method_data.get(price_key)
                
                if base_price is None:
                    continue
                
                method, was_created = ShippingMethod.objects.get_or_create(
                    code=f"{method_data['code']}_{customer_group}",
                    defaults={
                        'zone': zone,
                        'name': method_data['name'],
                        'customer_group': customer_group,
                        'base_price': base_price,
                        'currency': 'EUR',
                        'estimated_min_days': method_data.get('min_days'),
                        'estimated_max_days': method_data.get('max_days'),
                        'is_active': True,
                    }
                )
                
                if was_created:
                    created += 1
                else:
                    skipped += 1
        
        self.stdout.write(f"  Shipping methods: {created} created, {skipped} skipped\n")
        return {'created': created, 'skipped': skipped}
    
    def _seed_payment_methods(self):
        """Seed payment methods."""
        methods_data = [
            {
                'name': 'Bank Transfer',
                'code': 'bank_transfer',
                'provider': 'bank_transfer',
            },
            {
                'name': 'Invoice',
                'code': 'invoice',
                'provider': 'invoice',
            },
            {
                'name': 'PayPal',
                'code': 'paypal',
                'provider': 'paypal',
            },
            {
                'name': 'Credit Card',
                'code': 'credit_card',
                'provider': 'stripe',
            },
        ]
        
        created, skipped = 0, 0
        
        for method_data in methods_data:
            method, was_created = PaymentMethod.objects.get_or_create(
                code=method_data['code'],
                defaults={
                    'name': method_data['name'],
                    'provider': method_data['provider'],
                    'customer_group': 'all',
                    'is_active': True,
                }
            )
            
            if was_created:
                created += 1
                self.stdout.write(f"  ✓ Created payment method: {method.name}")
            else:
                skipped += 1
                self.stdout.write(f"  - Skipped payment method (exists): {method.name}")
        
        return {'created': created, 'skipped': skipped}
    
    def _seed_legal_documents(self):
        """Seed legal documents and versions."""
        docs_data = [
            {
                'document_type': 'terms_of_service',
                'target_group': 'all',
                'title': 'Terms of Service',
                'slug': 'terms-of-service',
                'version': '1.0',
                'content': '''**DEMO PLACEHOLDER - NOT FOR PRODUCTION**

Alice Wonder Nails Terms of Service

This is a demo placeholder for Terms of Service.
Replace with actual legal terms before going to production.

Last updated: [current date]
Effective: [current date]
'''
            },
            {
                'document_type': 'privacy_policy',
                'target_group': 'all',
                'title': 'Privacy Policy',
                'slug': 'privacy-policy',
                'version': '1.0',
                'content': '''**DEMO PLACEHOLDER - NOT FOR PRODUCTION**

Alice Wonder Nails Privacy Policy

This is a demo placeholder for Privacy Policy.
Replace with actual privacy policy before going to production.

Last updated: [current date]
Effective: [current date]
'''
            },
            {
                'document_type': 'withdrawal_policy',
                'target_group': 'all',
                'title': 'Right of Withdrawal',
                'slug': 'withdrawal-policy',
                'version': '1.0',
                'content': '''**DEMO PLACEHOLDER - NOT FOR PRODUCTION**

Alice Wonder Nails Right of Withdrawal

This is a demo placeholder for Right of Withdrawal / Widerrufsrecht.
Replace with actual withdrawal policy before going to production.

Last updated: [current date]
Effective: [current date]
'''
            },
            {
                'document_type': 'impressum',
                'target_group': 'all',
                'title': 'Impressum',
                'slug': 'impressum',
                'version': '1.0',
                'content': '''**DEMO PLACEHOLDER - NOT FOR PRODUCTION**

Alice Wonder Nails Impressum

This is a demo placeholder for Impressum (Legal Information).
Replace with actual business information before going to production.

Last updated: [current date]
Effective: [current date]
'''
            },
        ]
        
        docs_created, docs_skipped = 0, 0
        versions_created, versions_skipped = 0, 0
        
        for doc_data in docs_data:
            doc, was_created = LegalDocument.objects.get_or_create(
                document_type=doc_data['document_type'],
                defaults={
                    'target_group': doc_data['target_group'],
                    'title': doc_data['title'],
                    'slug': doc_data['slug'],
                }
            )
            
            if was_created:
                docs_created += 1
                self.stdout.write(f"  ✓ Created document: {doc.title}")
            else:
                docs_skipped += 1
                self.stdout.write(f"  - Skipped document (exists): {doc.title}")
            
            # Create version
            version, was_created = LegalDocumentVersion.objects.get_or_create(
                document=doc,
                version=doc_data['version'],
                defaults={
                    'status': 'active',
                    'content': doc_data['content'],
                }
            )
            
            if was_created:
                versions_created += 1
            else:
                versions_skipped += 1
        
        self.stdout.write(f"  Legal versions: {versions_created} created, {versions_skipped} skipped\n")
        
        return {
            'docs': {'created': docs_created, 'skipped': docs_skipped},
            'versions': {'created': versions_created, 'skipped': versions_skipped}
        }
    
    def _seed_consent_categories(self):
        """Seed consent categories."""
        categories_data = [
            {
                'key': 'newsletter',
                'name': 'Newsletter',
                'description': 'Subscribe to our newsletter for updates and promotions',
                'is_required': False,
            },
            {
                'key': 'analytics',
                'name': 'Analytics',
                'description': 'Allow analytics to understand how you use our website',
                'is_required': False,
            },
            {
                'key': 'marketing',
                'name': 'Marketing',
                'description': 'Allow marketing cookies for personalized content',
                'is_required': False,
            },
            {
                'key': 'terms_accept',
                'name': 'Terms & Conditions',
                'description': 'Accept Terms of Service and Privacy Policy',
                'is_required': True,
            },
        ]
        
        created, skipped = 0, 0
        
        for cat_data in categories_data:
            category, was_created = ConsentCategory.objects.get_or_create(
                key=cat_data['key'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data.get('description', ''),
                    'is_required': cat_data['is_required'],
                    'is_active': True,
                }
            )
            
            if was_created:
                created += 1
                self.stdout.write(f"  ✓ Created category: {category.name}")
            else:
                skipped += 1
                self.stdout.write(f"  - Skipped category (exists): {category.name}")
        
        return {'created': created, 'skipped': skipped}
    
    def _print_summary(self, stats):
        """Print summary of seeding operations."""
        self.stdout.write('\n' + self.style.SUCCESS('=== SEED SUMMARY ===\n'))
        
        total_created = 0
        total_skipped = 0
        
        for entity, counts in stats.items():
            if isinstance(counts, dict):
                created = counts.get('created', 0)
                skipped = counts.get('skipped', 0)
                total_created += created
                total_skipped += skipped
                
                created_str = self.style.SUCCESS(f"{created} created")
                skipped_str = self.style.WARNING(f"{skipped} skipped") if skipped > 0 else f"{skipped} skipped"
                
                self.stdout.write(f"{entity:.<40} {created_str} | {skipped_str}")
        
        self.stdout.write('\n' + '-' * 80)
        self.stdout.write(f"{'TOTAL':.<40} {self.style.SUCCESS(str(total_created))} created | {self.style.WARNING(str(total_skipped))} skipped\n")
        
        self.stdout.write(self.style.SUCCESS('✓ Demo data seed completed successfully!\n'))
        self.stdout.write('IMPORTANT: All legal documents are marked as DEMO PLACEHOLDER.')
        self.stdout.write('Replace with actual content before going to production.\n')
