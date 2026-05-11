from django.db import models
from django.contrib.postgres.fields import ArrayField
from decimal import Decimal


PAYMENT_METHOD_PROVIDER_CHOICES = [
    ("manual", "Manual"),
    ("bank_transfer", "Bank Transfer"),
    ("invoice", "Invoice"),
    ("paypal", "PayPal"),
    ("stripe", "Stripe"),
    ("other", "Other"),
]

PAYMENT_METHOD_CUSTOMER_GROUP_CHOICES = [
    ("all", "All (B2C and B2B)"),
    ("b2c", "B2C"),
    ("b2b", "B2B"),
]

PAYMENT_TRANSACTION_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("authorized", "Authorized"),
    ("paid", "Paid"),
    ("failed", "Failed"),
    ("cancelled", "Cancelled"),
    ("refunded", "Refunded"),
]

PAYMENT_TRANSACTION_CUSTOMER_GROUP_CHOICES = [
    ("b2c", "B2C"),
    ("b2b", "B2B"),
]


class PaymentMethod(models.Model):
    """
    Zahlungsart-Konfiguration.
    
    Definiert verfügbare Zahlungsmethoden im Shop.
    Provider ist Klassifikation, keine echte Anbieterintegration.
    customer_group "all" bedeutet für B2C und B2B nutzbar.
    """
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=64, unique=True)
    provider = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_PROVIDER_CHOICES,
        default="manual"
    )
    customer_group = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CUSTOMER_GROUP_CHOICES,
        default="all"
    )
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active", "customer_group"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class PaymentTransaction(models.Model):
    """
    Zahlungstransaktion.
    
    Technischer Zahlungsdatensatz für spätere Orders/Checkout.
    Speichert keine Kreditkartendaten.
    raw_response und metadata dienen nur zur Dokumentation,
    keine sensiblen Daten.
    """
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_transactions"
    )
    method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
    )
    payment_reference = models.CharField(max_length=120, blank=True, default="")
    provider_reference = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_TRANSACTION_STATUS_CHOICES,
        default="pending"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="EUR")
    customer_group = models.CharField(
        max_length=10,
        choices=PAYMENT_TRANSACTION_CUSTOMER_GROUP_CHOICES,
        default="b2c"
    )
    provider = models.CharField(max_length=64, default="manual")
    raw_response = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["customer_group"]),
            models.Index(fields=["provider"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gte=Decimal("0")),
                name="payment_transaction_amount_non_negative"
            ),
        ]

    def __str__(self):
        method_name = self.method.name if self.method else "No method"
        return f"PaymentTransaction #{self.id} - {method_name} ({self.status})"


class PaymentMethodSnapshot(models.Model):
    """
    Snapshot einer Zahlungsart für Orders/Checkout.
    
    Eigenständig stabil. Denormalisiert Daten für later Orders/Checkout.
    Wird nicht mit Order-Änderung synchron gehalten.
    """
    method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="snapshots"
    )
    method_code = models.CharField(max_length=64)
    method_name = models.CharField(max_length=120)
    provider = models.CharField(max_length=64)
    customer_group = models.CharField(
        max_length=10,
        choices=PAYMENT_TRANSACTION_CUSTOMER_GROUP_CHOICES,
        default="b2c"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["provider"]),
        ]

    def __str__(self):
        return f"PaymentMethodSnapshot #{self.id} - {self.method_name} ({self.provider})"
