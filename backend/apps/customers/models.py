from django.conf import settings
from django.db import models


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_profile',
    )
    display_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or self.user.get_username()


class Address(models.Model):
    class AddressType(models.TextChoices):
        BILLING = 'billing', 'Billing'
        SHIPPING = 'shipping', 'Shipping'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses',
    )
    address_type = models.CharField(max_length=16, choices=AddressType.choices)
    full_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True)
    street = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=32)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=2, default='DE')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('user', 'address_type', '-is_default', 'city')

    def __str__(self):
        return f'{self.full_name} - {self.city} ({self.address_type})'
