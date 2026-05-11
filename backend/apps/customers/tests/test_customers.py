from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.customers.models import Address, CustomerProfile


class CustomerModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='customer',
            email='customer@example.test',
            password='test-pass-123',
        )

    def test_customer_profile_can_be_created(self):
        profile = CustomerProfile.objects.create(
            user=self.user,
            display_name='Alice Customer',
            phone='12345',
        )

        self.assertEqual(str(profile), 'Alice Customer')

    def test_address_can_be_created(self):
        address = Address.objects.create(
            user=self.user,
            address_type=Address.AddressType.BILLING,
            full_name='Alice Customer',
            street='Main Street 1',
            postal_code='12345',
            city='Berlin',
            is_default=True,
        )

        self.assertEqual(address.country, 'DE')
        self.assertIn('Berlin', str(address))

    def test_address_type_choices_include_billing_and_shipping(self):
        choices = {choice for choice, label in Address.AddressType.choices}

        self.assertEqual(choices, {'billing', 'shipping'})
