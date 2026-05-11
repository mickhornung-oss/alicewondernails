from django.contrib.postgres.fields import ArrayField
from django.db import models


# Customer group choices for ShippingMethod
CUSTOMER_GROUP_CHOICES = [
    ('all', 'All (B2C and B2B)'),
    ('b2c', 'B2C'),
    ('b2b', 'B2B'),
]

SHIPPING_CUSTOMER_GROUP_CHOICES = [
    ('b2c', 'B2C'),
    ('b2b', 'B2B'),
]


class ShippingZone(models.Model):
    """
    Versandzone oder Versandlandgruppe, z. B. Deutschland, EU, International.
    Enthält Ländercodes und bestimmt, welche Versandmethoden verfügbar sind.
    """
    
    name = models.CharField(
        max_length=120,
        help_text='Name der Versandzone (z.B. Deutschland, EU, International)'
    )
    
    code = models.CharField(
        max_length=32,
        unique=True,
        help_text='Eindeutiger Code der Zone (z.B. DE, EU, INT)'
    )
    
    countries = ArrayField(
        models.CharField(max_length=3),
        default=list,
        blank=True,
        help_text='ISO-Ländercodes (z.B. ["DE", "AT", "CH"])'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Zone ist aktiv und wird für Versandberechnung berücksichtigt'
    )
    
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text='Sortierreihenfolge'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Shipping Zone'
        verbose_name_plural = 'Shipping Zones'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class ShippingMethod(models.Model):
    """
    Konkrete Versandmethode, z. B. Standardversand Deutschland, B2B Paketversand.
    Verbunden mit einer Zone und hat ein Basis-Versandentgelt.
    """
    
    zone = models.ForeignKey(
        ShippingZone,
        on_delete=models.PROTECT,
        related_name='shipping_methods',
        help_text='Versandzone dieser Methode'
    )
    
    name = models.CharField(
        max_length=120,
        help_text='Name der Versandmethode (z.B. Standardversand, Expressversand)'
    )
    
    code = models.CharField(
        max_length=64,
        unique=True,
        help_text='Eindeutiger Code (z.B. standard_de, express_de)'
    )
    
    customer_group = models.CharField(
        max_length=10,
        choices=CUSTOMER_GROUP_CHOICES,
        default='all',
        help_text='Kundengruppe: all, b2c oder b2b'
    )
    
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text='Basis-Versandkosten'
    )
    
    currency = models.CharField(
        max_length=3,
        default='EUR',
        help_text='Währung (ISO 4217 Code)'
    )
    
    estimated_min_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Minimale geschätzte Liefertage'
    )
    
    estimated_max_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Maximale geschätzte Liefertage'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Methode ist aktiv'
    )
    
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text='Sortierreihenfolge'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Shipping Method'
        verbose_name_plural = 'Shipping Methods'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(base_price__gte=0),
                name='shipping_method_base_price_non_negative'
            ),
            models.CheckConstraint(
                condition=models.Q(estimated_max_days__isnull=True) | 
                          models.Q(estimated_min_days__isnull=True) |
                          models.Q(estimated_max_days__gte=models.F('estimated_min_days')),
                name='shipping_method_estimated_days_valid'
            ),
        ]
        indexes = [
            models.Index(fields=['zone', 'is_active']),
            models.Index(fields=['code']),
            models.Index(fields=['customer_group']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.zone.code})"


class ShippingRateSnapshot(models.Model):
    """
    Technische Snapshot-Vorbereitung für spätere Orders/Checkout.
    
    Speichert eine Momentaufnahme einer Versandmethode und deren Kosten.
    Diese Snapshots sind eigenständig stabil und werden später beim Checkout
    und in Orders referenziert.
    """
    
    method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rate_snapshots',
        help_text='Referenz zur Versandmethode (kann gelöscht werden)'
    )
    
    method_code = models.CharField(
        max_length=64,
        help_text='Code der Versandmethode (Snapshot, unveränderlich)'
    )
    
    method_name = models.CharField(
        max_length=120,
        help_text='Name der Versandmethode (Snapshot, unveränderlich)'
    )
    
    zone_code = models.CharField(
        max_length=32,
        help_text='Code der Versandzone (Snapshot, unveränderlich)'
    )
    
    zone_name = models.CharField(
        max_length=120,
        help_text='Name der Versandzone (Snapshot, unveränderlich)'
    )
    
    customer_group = models.CharField(
        max_length=10,
        choices=SHIPPING_CUSTOMER_GROUP_CHOICES,
        help_text='Kundengruppe bei Snapshot-Erstellung'
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Versandkosten-Betrag des Snapshots'
    )
    
    currency = models.CharField(
        max_length=3,
        default='EUR',
        help_text='Währung'
    )
    
    estimated_min_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Minimale geschätzte Liefertage (Snapshot)'
    )
    
    estimated_max_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Maximale geschätzte Liefertage (Snapshot)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Shipping Rate Snapshot'
        verbose_name_plural = 'Shipping Rate Snapshots'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gte=0),
                name='shipping_snapshot_amount_non_negative'
            ),
        ]
        indexes = [
            models.Index(fields=['method_code']),
            models.Index(fields=['customer_group']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.method_name} ({self.zone_name}) - {self.amount} {self.currency}"
