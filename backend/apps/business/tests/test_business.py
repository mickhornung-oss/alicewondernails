from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.business.models import BusinessProfile


class BusinessProfileModelTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='business',
            email='business@example.test',
            password='test-pass-123',
        )
        self.reviewer = user_model.objects.create_user(
            username='reviewer',
            email='reviewer@example.test',
            password='test-pass-123',
            is_staff=True,
        )

    def test_business_profile_can_be_created(self):
        profile = BusinessProfile.objects.create(
            user=self.user,
            company_name='Wonder Nails GmbH',
        )

        self.assertEqual(profile.status, BusinessProfile.Status.PENDING)
        self.assertIn('Wonder Nails GmbH', str(profile))

    def test_status_choices_include_pending_approved_rejected(self):
        choices = {choice for choice, label in BusinessProfile.Status.choices}

        self.assertEqual(choices, {'pending', 'approved', 'rejected'})

    def test_reviewed_by_can_be_set(self):
        profile = BusinessProfile.objects.create(
            user=self.user,
            company_name='Wonder Nails GmbH',
            status=BusinessProfile.Status.APPROVED,
            reviewed_by=self.reviewer,
            reviewed_at=timezone.now(),
        )

        self.assertEqual(profile.reviewed_by, self.reviewer)
        self.assertEqual(profile.status, BusinessProfile.Status.APPROVED)
