from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class CustomerStatus(models.TextChoices):
        CONSUMER = 'consumer', 'Consumer'
        BUSINESS_PENDING = 'business_pending', 'Business pending'
        BUSINESS_APPROVED = 'business_approved', 'Business approved'

    email = models.EmailField(unique=True)
    customer_status = models.CharField(
        max_length=32,
        choices=CustomerStatus.choices,
        default=CustomerStatus.CONSUMER,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_consumer(self):
        return self.customer_status == self.CustomerStatus.CONSUMER

    @property
    def is_business_pending(self):
        return self.customer_status == self.CustomerStatus.BUSINESS_PENDING

    @property
    def is_business_approved(self):
        return self.customer_status == self.CustomerStatus.BUSINESS_APPROVED
