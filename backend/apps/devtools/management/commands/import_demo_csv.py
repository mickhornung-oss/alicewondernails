"""
Import demo data from CSV files.

This command imports demo data from CSV files for local development.
It is idempotent and supports upsert (create/update/skip).

Usage:
    python manage.py import_demo_csv --settings=config.settings.local
    python manage.py import_demo_csv --settings=config.settings.local --source backend/data/imports/demo
"""

import csv
import os
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.catalog.models import ProductCategory, Product, ProductVariant
from apps.pricing.models import ProductPrice
from apps.shipping.models import ShippingZone, ShippingMethod
from apps.payments.models import PaymentMethod
from apps.legal.models import LegalDocument, LegalDocumentVersion
from apps.consent.models import ConsentCategory


class Command(BaseCommand):
    """
    Import demo data from CSV files.
    
    Supports idempotent upsert with create/update/skip counting.
    """
    
    help = 'Import demo data from CSV files (idempotent, upsert-capable)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            default='backend/data/imports/demo',
            help='Path to directory containing CSV files (default: backend/data/imports/demo)',
        )
    
    def handle(self, *args, **options):
        source_dir = options['source']
        
        # Resolve path relative to project root (ROOT_DIR) if not absolute
        if not os.path.isabs(source_dir):
            from config.settings.base import ROOT_DIR
            source_dir = os.path.join(str(ROOT_DIR), source_dir)
            source_dir = os.path.normpath(source_dir)
        
        # Validate directory exists
        if not os.path.isdir(source_dir):
            raise CommandError(f'Source directory not found: {source_dir}')
        
        self.stdout.write(self.style.SUCCESS('Starting CSV import (idempotent mode)...\n'))
        
        # Initialize stats
        stats = {
            'categories': {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0},
            'shipping_zones': {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0},
            'payment_methods': {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0},
            'legal_documents': {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0},
            'products': {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0},
            'variants': {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0},
            'prices': {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0},
            'shipping_methods': {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0},
            'legal_versions': {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0},
            'consent_categories': {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0},
        }
        
        try:
            with transaction.atomic():
                # Import in dependency order
                stats['categories'] = self._import_categories(source_dir)
                stats['shipping_zones'] = self._import_shipping_zones(source_dir)
                stats['payment_methods'] = self._import_payment_methods(source_dir)
                stats['legal_documents'] = self._import_legal_documents(source_dir)
                stats['products'] = self._import_products(source_dir)
                stats['variants'] = self._import_variants(source_dir)
                stats['prices'] = self._import_prices(source_dir)
                stats['shipping_methods'] = self._import_shipping_methods(source_dir)
                stats['legal_versions'] = self._import_legal_versions(source_dir)
                stats['consent_categories'] = self._import_consent_categories(source_dir)
        except CommandError as e:
            # Transaction rolls back automatically
            self.stdout.write(self.style.ERROR(f'\n✗ Import aborted: {str(e)}'))
            raise
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Unexpected error: {str(e)}'))
            raise CommandError(str(e))
        
        # Print summary
        self._print_summary(stats)
    
    # ========== Import Methods ==========
    
    def _import_categories(self, source_dir):
        """Import ProductCategory from categories_demo.csv"""
        filepath = os.path.join(source_dir, 'categories_demo.csv')
        if not os.path.exists(filepath):
            raise CommandError(f'File not found: {filepath}')
        
        stats = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                try:
                    self._validate_required_fields(row, ['name', 'slug'], filepath, row_num)
                    
                    obj, created, updated = self._upsert_with_change_detection(
                        ProductCategory,
                        {'slug': row['slug'].strip()},
                        {
                            'name': row['name'].strip(),
                            'description': row.get('description', '').strip(),
                        }
                    )
                    
                    if created:
                        stats['created'] += 1
                        self.stdout.write(f"  ✓ Created: {obj.name}")
                    elif updated:
                        stats['updated'] += 1
                        self.stdout.write(f"  ~ Updated: {obj.name}")
                    else:
                        stats['skipped'] += 1
                
                except Exception as e:
                    stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f"  ✗ Row {row_num}: {str(e)}"))
                    raise CommandError(f'ProductCategory import failed at row {row_num}: {str(e)}')
        
        self.stdout.write(f"ProductCategory: {stats['created']} created, {stats['updated']} updated, {stats['skipped']} skipped\n")
        return stats
    
    def _import_shipping_zones(self, source_dir):
        """Import ShippingZone from shipping_zones_demo.csv"""
        filepath = os.path.join(source_dir, 'shipping_zones_demo.csv')
        if not os.path.exists(filepath):
            raise CommandError(f'File not found: {filepath}')
        
        stats = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                try:
                    self._validate_required_fields(row, ['name', 'code'], filepath, row_num)
                    
                    # Parse countries list
                    countries_str = row.get('countries', '').strip()
                    countries = [c.strip() for c in countries_str.split(',') if c.strip()] if countries_str else []
                    
                    obj, created, updated = self._upsert_with_change_detection(
                        ShippingZone,
                        {'code': row['code'].strip()},
                        {
                            'name': row['name'].strip(),
                            'countries': countries,
                            'is_active': True,
                        }
                    )
                    
                    if created:
                        stats['created'] += 1
                        self.stdout.write(f"  ✓ Created: {obj.name}")
                    elif updated:
                        stats['updated'] += 1
                        self.stdout.write(f"  ~ Updated: {obj.name}")
                    else:
                        stats['skipped'] += 1
                
                except Exception as e:
                    stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f"  ✗ Row {row_num}: {str(e)}"))
                    raise CommandError(f'ShippingZone import failed at row {row_num}: {str(e)}')
        
        self.stdout.write(f"ShippingZone: {stats['created']} created, {stats['updated']} updated, {stats['skipped']} skipped\n")
        return stats
    
    def _import_payment_methods(self, source_dir):
        """Import PaymentMethod from payment_methods_demo.csv"""
        filepath = os.path.join(source_dir, 'payment_methods_demo.csv')
        if not os.path.exists(filepath):
            raise CommandError(f'File not found: {filepath}')
        
        stats = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                try:
                    self._validate_required_fields(row, ['name', 'code', 'provider'], filepath, row_num)
                    
                    customer_group = row.get('customer_group', 'all').strip()
                    if customer_group not in ['all', 'b2c', 'b2b']:
                        raise ValueError(f'Invalid customer_group: {customer_group}')

                    is_active_raw = row.get('is_active', 'true').strip().lower()
                    is_active = is_active_raw in {'true', '1', 'yes', 'y', 'ja'}

                    obj, created, updated = self._upsert_with_change_detection(
                        PaymentMethod,
                        {'code': row['code'].strip()},
                        {
                            'name': row['name'].strip(),
                            'provider': row['provider'].strip(),
                            'customer_group': customer_group,
                            'is_active': is_active,
                        }
                    )
                    
                    if created:
                        stats['created'] += 1
                        self.stdout.write(f"  ✓ Created: {obj.name}")
                    elif updated:
                        stats['updated'] += 1
                        self.stdout.write(f"  ~ Updated: {obj.name}")
                    else:
                        stats['skipped'] += 1
                
                except Exception as e:
                    stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f"  ✗ Row {row_num}: {str(e)}"))
                    raise CommandError(f'PaymentMethod import failed at row {row_num}: {str(e)}')
        
        self.stdout.write(f"PaymentMethod: {stats['created']} created, {stats['updated']} updated, {stats['skipped']} skipped\n")
        return stats
    
    def _import_legal_documents(self, source_dir):
        """Import LegalDocument from legal_documents_demo.csv"""
        filepath = os.path.join(source_dir, 'legal_documents_demo.csv')
        if not os.path.exists(filepath):
            raise CommandError(f'File not found: {filepath}')
        
        stats = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                try:
                    self._validate_required_fields(row, ['document_type', 'title'], filepath, row_num)
                    
                    target_group = row.get('target_group', 'all').strip()
                    
                    obj, created, updated = self._upsert_with_change_detection(
                        LegalDocument,
                        {'document_type': row['document_type'].strip()},
                        {
                            'title': row['title'].strip(),
                            'target_group': target_group,
                            'slug': row.get('slug', row['document_type']).strip(),
                        }
                    )
                    
                    if created:
                        stats['created'] += 1
                        self.stdout.write(f"  ✓ Created: {obj.title}")
                    elif updated:
                        stats['updated'] += 1
                        self.stdout.write(f"  ~ Updated: {obj.title}")
                    else:
                        stats['skipped'] += 1
                
                except Exception as e:
                    stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f"  ✗ Row {row_num}: {str(e)}"))
                    raise CommandError(f'LegalDocument import failed at row {row_num}: {str(e)}')
        
        self.stdout.write(f"LegalDocument: {stats['created']} created, {stats['updated']} updated, {stats['skipped']} skipped\n")
        return stats
    
    def _import_products(self, source_dir):
        """Import Product from products_demo.csv"""
        filepath = os.path.join(source_dir, 'products_demo.csv')
        if not os.path.exists(filepath):
            raise CommandError(f'File not found: {filepath}')
        
        stats = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                try:
                    self._validate_required_fields(row, ['name', 'slug', 'category_slug', 'product_type', 'visibility'], filepath, row_num)
                    
                    # Validate foreign key
                    try:
                        category = ProductCategory.objects.get(slug=row['category_slug'].strip())
                    except ProductCategory.DoesNotExist:
                        raise ValueError(f"ProductCategory with slug '{row['category_slug']}' not found")
                    
                    # Validate enums
                    product_type = row['product_type'].strip()
                    visibility = row['visibility'].strip()
                    
                    if product_type not in ['gel', 'nail_polish', 'care', 'accessory', 'set', 'other']:
                        raise ValueError(f'Invalid product_type: {product_type}')
                    
                    if visibility not in ['public', 'b2c_only', 'b2b_only', 'hidden']:
                        raise ValueError(f'Invalid visibility: {visibility}')
                    
                    obj, created, updated = self._upsert_with_change_detection(
                        Product,
                        {'slug': row['slug'].strip()},
                        {
                            'name': row['name'].strip(),
                            'category': category,
                            'product_type': product_type,
                            'visibility': visibility,
                            'short_description': row.get('short_description', '').strip(),
                            'description': row.get('description', '').strip(),
                            'is_active': True,
                        }
                    )
                    
                    if created:
                        stats['created'] += 1
                        self.stdout.write(f"  ✓ Created: {obj.name}")
                    elif updated:
                        stats['updated'] += 1
                        self.stdout.write(f"  ~ Updated: {obj.name}")
                    else:
                        stats['skipped'] += 1
                
                except Exception as e:
                    stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f"  ✗ Row {row_num}: {str(e)}"))
                    raise CommandError(f'Product import failed at row {row_num}: {str(e)}')
        
        self.stdout.write(f"Product: {stats['created']} created, {stats['updated']} updated, {stats['skipped']} skipped\n")
        return stats
    
    def _import_variants(self, source_dir):
        """Import ProductVariant from variants_demo.csv"""
        filepath = os.path.join(source_dir, 'variants_demo.csv')
        if not os.path.exists(filepath):
            raise CommandError(f'File not found: {filepath}')
        
        stats = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                try:
                    self._validate_required_fields(row, ['product_slug', 'name'], filepath, row_num)
                    
                    # Validate foreign key
                    try:
                        product = Product.objects.get(slug=row['product_slug'].strip())
                    except Product.DoesNotExist:
                        raise ValueError(f"Product with slug '{row['product_slug']}' not found")
                    
                    sku = row.get('sku', '').strip() or None
                    is_default_str = row.get('is_default', 'FALSE').strip().upper()
                    is_default = is_default_str == 'TRUE'
                    
                    # Create or update by product + sku (or product + name if no sku)
                    if sku:
                        obj, created, updated = self._upsert_with_change_detection(
                            ProductVariant,
                            {'sku': sku},
                            {
                                'product': product,
                                'name': row['name'].strip(),
                                'is_default': is_default,
                                'is_active': True,
                            }
                        )
                    else:
                        # For no-SKU variants, need custom logic
                        try:
                            obj = ProductVariant.objects.get(product=product, name=row['name'].strip())
                            changed = False
                            if obj.is_default != is_default or obj.is_active != True:
                                obj.is_default = is_default
                                obj.is_active = True
                                obj.save()
                                changed = True
                            created = False
                            updated = changed
                        except ProductVariant.DoesNotExist:
                            obj = ProductVariant.objects.create(
                                product=product,
                                name=row['name'].strip(),
                                is_default=is_default,
                                is_active=True
                            )
                            created = True
                            updated = False
                    
                    if created:
                        stats['created'] += 1
                        self.stdout.write(f"  ✓ Created: {product.name} - {obj.name}")
                    elif updated:
                        stats['updated'] += 1
                        self.stdout.write(f"  ~ Updated: {product.name} - {obj.name}")
                    else:
                        stats['skipped'] += 1
                
                except Exception as e:
                    stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f"  ✗ Row {row_num}: {str(e)}"))
                    raise CommandError(f'ProductVariant import failed at row {row_num}: {str(e)}')
        
        self.stdout.write(f"ProductVariant: {stats['created']} created, {stats['updated']} updated, {stats['skipped']} skipped\n")
        return stats
    
    def _import_prices(self, source_dir):
        """Import ProductPrice from prices_demo.csv"""
        filepath = os.path.join(source_dir, 'prices_demo.csv')
        if not os.path.exists(filepath):
            raise CommandError(f'File not found: {filepath}')
        
        stats = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                try:
                    self._validate_required_fields(row, ['product_slug', 'customer_group', 'amount'], filepath, row_num)
                    
                    # Validate foreign keys
                    try:
                        product = Product.objects.get(slug=row['product_slug'].strip())
                    except Product.DoesNotExist:
                        raise ValueError(f"Product with slug '{row['product_slug']}' not found")
                    
                    variant_sku = row.get('variant_sku', '').strip() or None
                    variant = None
                    if variant_sku:
                        try:
                            variant = ProductVariant.objects.get(sku=variant_sku)
                            if variant.product_id != product.id:
                                raise ValueError(f"Variant '{variant_sku}' does not belong to product '{row['product_slug']}'")
                        except ProductVariant.DoesNotExist:
                            raise ValueError(f"ProductVariant with sku '{variant_sku}' not found")
                    
                    customer_group = row['customer_group'].strip()
                    if customer_group not in ['b2c', 'b2b']:
                        raise ValueError(f'Invalid customer_group: {customer_group}')
                    
                    # Parse decimal amount
                    try:
                        amount = Decimal(row['amount'].strip())
                    except (InvalidOperation, ValueError):
                        raise ValueError(f"Invalid amount: {row['amount']}")
                    
                    if amount <= 0:
                        raise ValueError(f"Amount must be > 0, got {amount}")
                    
                    currency = row.get('currency', 'EUR').strip()
                    tax_rate_str = row.get('tax_rate', '19.00').strip()
                    price_includes_tax_str = row.get('price_includes_tax', 'TRUE').strip().upper()
                    
                    try:
                        tax_rate = Decimal(tax_rate_str)
                    except (InvalidOperation, ValueError):
                        raise ValueError(f"Invalid tax_rate: {tax_rate_str}")
                    
                    price_includes_tax = price_includes_tax_str == 'TRUE'
                    
                    # Custom upsert for compound key (product, variant, customer_group)
                    lookup = {
                        'product': product,
                        'variant': variant,
                        'customer_group': customer_group,
                    }
                    
                    try:
                        obj = ProductPrice.objects.get(**lookup)
                        # Object exists, check if any fields changed
                        changed = False
                        if obj.amount != amount or obj.currency != currency or obj.tax_rate != tax_rate or obj.price_includes_tax != price_includes_tax or obj.is_active != True:
                            obj.amount = amount
                            obj.currency = currency
                            obj.tax_rate = tax_rate
                            obj.price_includes_tax = price_includes_tax
                            obj.is_active = True
                            obj.save()
                            changed = True
                        created = False
                        updated = changed
                    except ProductPrice.DoesNotExist:
                        obj = ProductPrice.objects.create(
                            product=product,
                            variant=variant,
                            customer_group=customer_group,
                            amount=amount,
                            currency=currency,
                            tax_rate=tax_rate,
                            price_includes_tax=price_includes_tax,
                            is_active=True
                        )
                        created = True
                        updated = False
                    
                    if created:
                        stats['created'] += 1
                        variant_label = f" / {variant.name}" if variant else ""
                        self.stdout.write(f"  ✓ Created: {product.name}{variant_label} - {customer_group} - {amount} {currency}")
                    elif updated:
                        stats['updated'] += 1
                        variant_label = f" / {variant.name}" if variant else ""
                        self.stdout.write(f"  ~ Updated: {product.name}{variant_label} - {customer_group} - {amount} {currency}")
                    else:
                        stats['skipped'] += 1
                
                except Exception as e:
                    stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f"  ✗ Row {row_num}: {str(e)}"))
                    raise CommandError(f'ProductPrice import failed at row {row_num}: {str(e)}')
        
        self.stdout.write(f"ProductPrice: {stats['created']} created, {stats['updated']} updated, {stats['skipped']} skipped\n")
        return stats
    
    def _import_shipping_methods(self, source_dir):
        """Import ShippingMethod from shipping_methods_demo.csv"""
        filepath = os.path.join(source_dir, 'shipping_methods_demo.csv')
        if not os.path.exists(filepath):
            raise CommandError(f'File not found: {filepath}')
        
        stats = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                try:
                    self._validate_required_fields(row, ['name', 'code', 'zone_code', 'customer_group', 'base_price'], filepath, row_num)
                    
                    # Validate foreign key
                    try:
                        zone = ShippingZone.objects.get(code=row['zone_code'].strip())
                    except ShippingZone.DoesNotExist:
                        raise ValueError(f"ShippingZone with code '{row['zone_code']}' not found")
                    
                    customer_group = row['customer_group'].strip()
                    if customer_group not in ['b2c', 'b2b', 'all']:
                        raise ValueError(f'Invalid customer_group: {customer_group}')
                    
                    # Parse base_price
                    try:
                        base_price = Decimal(row['base_price'].strip())
                    except (InvalidOperation, ValueError):
                        raise ValueError(f"Invalid base_price: {row['base_price']}")
                    
                    if base_price < 0:
                        raise ValueError(f"base_price must be >= 0, got {base_price}")
                    
                    currency = row.get('currency', 'EUR').strip()
                    min_days = row.get('estimated_min_days', '').strip()
                    max_days = row.get('estimated_max_days', '').strip()
                    
                    defaults = {
                        'name': row['name'].strip(),
                        'zone': zone,
                        'customer_group': customer_group,
                        'base_price': base_price,
                        'currency': currency,
                        'is_active': True,
                    }
                    
                    if min_days:
                        defaults['estimated_min_days'] = int(min_days)
                    if max_days:
                        defaults['estimated_max_days'] = int(max_days)
                    
                    obj, created, updated = self._upsert_with_change_detection(
                        ShippingMethod,
                        {'code': row['code'].strip()},
                        defaults
                    )
                    
                    if created:
                        stats['created'] += 1
                        self.stdout.write(f"  ✓ Created: {obj.name}")
                    elif updated:
                        stats['updated'] += 1
                        self.stdout.write(f"  ~ Updated: {obj.name}")
                    else:
                        stats['skipped'] += 1
                
                except Exception as e:
                    stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f"  ✗ Row {row_num}: {str(e)}"))
                    raise CommandError(f'ShippingMethod import failed at row {row_num}: {str(e)}')
        
        self.stdout.write(f"ShippingMethod: {stats['created']} created, {stats['updated']} updated, {stats['skipped']} skipped\n")
        return stats
    
    def _import_legal_versions(self, source_dir):
        """Import LegalDocumentVersion from legal_versions_demo.csv"""
        filepath = os.path.join(source_dir, 'legal_versions_demo.csv')
        if not os.path.exists(filepath):
            raise CommandError(f'File not found: {filepath}')
        
        stats = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                try:
                    self._validate_required_fields(row, ['document_type', 'version', 'content'], filepath, row_num)
                    
                    # Validate foreign key
                    try:
                        document = LegalDocument.objects.get(document_type=row['document_type'].strip())
                    except LegalDocument.DoesNotExist:
                        raise ValueError(f"LegalDocument with document_type '{row['document_type']}' not found")
                    
                    status = row.get('status', 'active').strip()
                    
                    # Custom upsert for compound key (document, version)
                    lookup = {
                        'document': document,
                        'version': row['version'].strip(),
                    }
                    
                    try:
                        obj = LegalDocumentVersion.objects.get(**lookup)
                        # Object exists, check if any fields changed
                        changed = False
                        if obj.status != status or obj.content != row['content'].strip():
                            obj.status = status
                            obj.content = row['content'].strip()
                            obj.save()
                            changed = True
                        created = False
                        updated = changed
                    except LegalDocumentVersion.DoesNotExist:
                        obj = LegalDocumentVersion.objects.create(
                            document=document,
                            version=row['version'].strip(),
                            status=status,
                            content=row['content'].strip()
                        )
                        created = True
                        updated = False
                    
                    if created:
                        stats['created'] += 1
                        self.stdout.write(f"  ✓ Created: {document.title} v{obj.version}")
                    elif updated:
                        stats['updated'] += 1
                        self.stdout.write(f"  ~ Updated: {document.title} v{obj.version}")
                    else:
                        stats['skipped'] += 1
                
                except Exception as e:
                    stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f"  ✗ Row {row_num}: {str(e)}"))
                    raise CommandError(f'LegalDocumentVersion import failed at row {row_num}: {str(e)}')
        
        self.stdout.write(f"LegalDocumentVersion: {stats['created']} created, {stats['updated']} updated, {stats['skipped']} skipped\n")
        return stats
    
    def _import_consent_categories(self, source_dir):
        """Import ConsentCategory from consent_categories_demo.csv"""
        filepath = os.path.join(source_dir, 'consent_categories_demo.csv')
        if not os.path.exists(filepath):
            raise CommandError(f'File not found: {filepath}')
        
        stats = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                try:
                    self._validate_required_fields(row, ['key', 'name'], filepath, row_num)
                    
                    is_required_str = row.get('is_required', 'FALSE').strip().upper()
                    is_required = is_required_str == 'TRUE'
                    
                    obj, created, updated = self._upsert_with_change_detection(
                        ConsentCategory,
                        {'key': row['key'].strip()},
                        {
                            'name': row['name'].strip(),
                            'description': row.get('description', '').strip(),
                            'is_required': is_required,
                            'is_active': True,
                        }
                    )
                    
                    if created:
                        stats['created'] += 1
                        self.stdout.write(f"  ✓ Created: {obj.name}")
                    elif updated:
                        stats['updated'] += 1
                        self.stdout.write(f"  ~ Updated: {obj.name}")
                    else:
                        stats['skipped'] += 1
                
                except Exception as e:
                    stats['errors'] += 1
                    self.stdout.write(self.style.ERROR(f"  ✗ Row {row_num}: {str(e)}"))
                    raise CommandError(f'ConsentCategory import failed at row {row_num}: {str(e)}')
        
        self.stdout.write(f"ConsentCategory: {stats['created']} created, {stats['updated']} updated, {stats['skipped']} skipped\n")
        return stats
    
    # ========== Utilities ==========
    
    def _upsert_with_change_detection(self, model, unique_lookup, defaults):
        """
        Upsert with real change detection.
        
        Returns: (obj, created, updated)
            - created: True if new object
            - updated: True if object exists and fields changed
            - False for both if object exists but no changes
        """
        try:
            obj = model.objects.get(**unique_lookup)
            # Object exists, check if any fields changed
            changed = False
            for field, value in defaults.items():
                if getattr(obj, field) != value:
                    changed = True
                    setattr(obj, field, value)
            
            if changed:
                obj.save()
                return obj, False, True  # existing, updated
            else:
                return obj, False, False  # existing, not updated
        except model.DoesNotExist:
            # Create new object
            obj = model.objects.create(**unique_lookup, **defaults)
            return obj, True, False  # created, not updated
    
    def _validate_required_fields(self, row, required_fields, filepath, row_num):
        """Validate that all required fields are present and non-empty"""
        for field in required_fields:
            value = row.get(field, '').strip()
            if not value:
                raise ValueError(f"Required field '{field}' is empty in {filepath} at row {row_num}")
    
    def _print_summary(self, stats):
        """Print import summary"""
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('=== CSV IMPORT SUMMARY ===\n'))
        
        total_created = 0
        total_updated = 0
        total_skipped = 0
        total_errors = 0
        
        for entity, s in stats.items():
            created = s['created']
            updated = s['updated']
            skipped = s['skipped']
            errors = s['errors']
            
            total_created += created
            total_updated += updated
            total_skipped += skipped
            total_errors += errors
            
            status_str = f"{entity}".ljust(30)
            if errors:
                self.stdout.write(
                    self.style.ERROR(
                        f"{status_str} {created} created | {updated} updated | {skipped} skipped | {errors} errors"
                    )
                )
            else:
                self.stdout.write(f"{status_str} {created} created | {updated} updated | {skipped} skipped")
        
        self.stdout.write('\n' + '=' * 80)
        if total_errors:
            self.stdout.write(
                self.style.ERROR(
                    f"Total: {total_created} created | {total_updated} updated | {total_skipped} skipped | {total_errors} errors"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"[OK] Total: {total_created} created | {total_updated} updated | {total_skipped} skipped"
                )
            )
        self.stdout.write('=' * 80)
