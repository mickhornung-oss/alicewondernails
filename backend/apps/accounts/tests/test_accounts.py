from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase


class UserModelTest(TestCase):
    def test_user_defaults_to_consumer(self):
        user = get_user_model().objects.create_user(
            username='consumer',
            email='consumer@example.test',
            password='test-pass-123',
        )

        self.assertTrue(user.is_consumer)
        self.assertFalse(user.is_business_pending)
        self.assertFalse(user.is_business_approved)
        self.assertEqual(user.email, 'consumer@example.test')
        self.assertEqual(user.customer_status, get_user_model().CustomerStatus.CONSUMER)

    def test_business_status_properties(self):
        user_model = get_user_model()
        pending = user_model.objects.create_user(
            username='pending',
            email='pending@example.test',
            password='test-pass-123',
            customer_status=user_model.CustomerStatus.BUSINESS_PENDING,
        )
        approved = user_model.objects.create_user(
            username='approved',
            email='approved@example.test',
            password='test-pass-123',
            customer_status=user_model.CustomerStatus.BUSINESS_APPROVED,
        )

        self.assertTrue(pending.is_business_pending)
        self.assertTrue(approved.is_business_approved)

    def test_email_is_unique(self):
        user_model = get_user_model()
        user_model.objects.create_user(
            username='first',
            email='same@example.test',
            password='test-pass-123',
        )

        with self.assertRaises(IntegrityError):
            user_model.objects.create_user(
                username='second',
                email='same@example.test',
                password='test-pass-123',
            )
