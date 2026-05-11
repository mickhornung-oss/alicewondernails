from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class CheckoutSession(models.Model):
    """
    Technische Checkout-Sitzung für einen Warenkorb.
    Speichert User, Versandmethode, Zahlungsmethode und rechtliche Grundlagen.
    """

    STATUS_CHOICES = (
        ('started', 'Started'),
        ('validated', 'Validated'),
        ('order_created', 'Order Created'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    )

    CUSTOMER_GROUP_CHOICES = (
        ('b2c', 'B2C'),
        ('b2b', 'B2B'),
    )

    # Beziehungen
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='checkout_sessions'
    )
    cart = models.ForeignKey(
        'cart.Cart',
        on_delete=models.PROTECT,
        related_name='checkout_sessions'
    )

    # Status
    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default='started'
    )
    customer_group = models.CharField(
        max_length=10,
        choices=CUSTOMER_GROUP_CHOICES,
        default='b2c'
    )
    currency = models.CharField(
        max_length=3,
        default='EUR'
    )

    # Versand
    shipping_method = models.ForeignKey(
        'shipping.ShippingMethod',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='checkout_sessions'
    )
    shipping_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot der Versandmethode (keine Secrets)"
    )
    shipping_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    # Zahlung
    payment_method = models.ForeignKey(
        'payments.PaymentMethod',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='checkout_sessions'
    )
    payment_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot der Zahlungsmethode (keine Secrets)"
    )

    # Summen
    cart_subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    order_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    item_count = models.PositiveIntegerField(
        default=0
    )

    # Legal & Consent
    legal_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot der Rechtsvereinbarungen"
    )
    consent_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot der Zustimmungen (Consent)"
    )

    # Order-Bezug
    order = models.OneToOneField(
        'orders.Order',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='checkout_session'
    )

    # Zeitstempel
    started_at = models.DateTimeField(
        auto_now_add=True
    )
    validated_at = models.DateTimeField(
        null=True,
        blank=True
    )
    order_created_at = models.DateTimeField(
        null=True,
        blank=True
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['status', '-updated_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['cart']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(shipping_amount__gte=0),
                name='checkout_shipping_amount_non_negative'
            ),
            models.CheckConstraint(
                condition=models.Q(cart_subtotal__gte=0),
                name='checkout_cart_subtotal_non_negative'
            ),
            models.CheckConstraint(
                condition=models.Q(order_total__gte=0),
                name='checkout_order_total_non_negative'
            ),
            models.CheckConstraint(
                condition=models.Q(item_count__gte=0),
                name='checkout_item_count_non_negative'
            ),
        ]

    def __str__(self):
        return f"Checkout #{self.pk} ({self.status}) - Cart: {self.cart_id}"


class CheckoutEvent(models.Model):
    """
    Einfaches technisches Ereignis im Checkout-Ablauf.
    Nicht als Ersatz für auditlog, sondern für checkout-interne Nachverfolgung.
    """

    EVENT_TYPE_CHOICES = (
        ('started', 'Started'),
        ('validated', 'Validated'),
        ('shipping_selected', 'Shipping Selected'),
        ('payment_selected', 'Payment Selected'),
        ('legal_checked', 'Legal Checked'),
        ('consent_checked', 'Consent Checked'),
        ('order_created', 'Order Created'),
        ('cancelled', 'Cancelled'),
        ('error', 'Error'),
    )

    checkout = models.ForeignKey(
        CheckoutSession,
        on_delete=models.CASCADE,
        related_name='events'
    )
    event_type = models.CharField(
        max_length=32,
        choices=EVENT_TYPE_CHOICES
    )
    message = models.TextField(
        blank=True,
        default=''
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Zusätzliche Daten (keine Secrets)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['checkout', '-created_at']),
            models.Index(fields=['event_type']),
        ]

    def __str__(self):
        return f"CheckoutEvent: {self.event_type} (Checkout #{self.checkout_id})"
