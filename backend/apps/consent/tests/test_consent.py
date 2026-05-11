from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from apps.consent.models import ConsentCategory, ConsentRecord
from apps.consent.services import (
    record_consent,
    get_latest_consent,
    has_consent,
    ConsentError,
)

User = get_user_model()


class ConsentCategoryTestCase(TestCase):
    """Tests für ConsentCategory-Modell."""
    
    def test_create_consent_category(self):
        """Kategorie kann erstellt werden."""
        cat = ConsentCategory.objects.create(
            key='necessary',
            name='Notwendig',
            is_required=True,
        )
        self.assertEqual(cat.key, 'necessary')
        self.assertTrue(cat.is_required)
    
    def test_key_unique(self):
        """Key ist eindeutig."""
        ConsentCategory.objects.create(
            key='analytics',
            name='Analytik',
        )
        
        with self.assertRaises(Exception):  # IntegrityError
            ConsentCategory.objects.create(
                key='analytics',
                name='Analytics 2',
            )
    
    def test_required_category(self):
        """Required-Kategorie funktioniert."""
        cat = ConsentCategory.objects.create(
            key='necessary',
            name='Notwendig',
            is_required=True,
        )
        self.assertTrue(cat.is_required)
    
    def test_str_method(self):
        """__str__ sinnvoll."""
        cat = ConsentCategory.objects.create(
            key='marketing',
            name='Marketing',
        )
        self.assertIn('Marketing', str(cat))
        self.assertIn('marketing', str(cat))


class ConsentRecordTestCase(TestCase):
    """Tests für ConsentRecord-Modell."""
    
    def setUp(self):
        """Setup für Tests."""
        self.user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='pass123',
        )
        self.category = ConsentCategory.objects.create(
            key='analytics',
            name='Analytik',
        )
    
    def test_create_record_with_user(self):
        """Record für User kann erstellt werden."""
        record = ConsentRecord.objects.create(
            user=self.user,
            category=self.category,
            granted=True,
        )
        self.assertEqual(record.user, self.user)
        self.assertTrue(record.granted)
    
    def test_create_record_with_session(self):
        """Record für session_key kann erstellt werden."""
        record = ConsentRecord.objects.create(
            session_key='test-session-key',
            category=self.category,
            granted=False,
        )
        self.assertEqual(record.session_key, 'test-session-key')
        self.assertFalse(record.granted)
    
    def test_record_without_user_and_session_invalid(self):
        """Record ohne user und ohne session_key ist ungültig."""
        record = ConsentRecord(
            category=self.category,
            granted=True,
        )
        
        with self.assertRaises(ValidationError):
            record.clean()
    
    def test_granted_true_false(self):
        """granted True/False funktioniert."""
        r1 = ConsentRecord.objects.create(
            user=self.user,
            category=self.category,
            granted=True,
        )
        r2 = ConsentRecord.objects.create(
            session_key='session2',
            category=self.category,
            granted=False,
        )
        
        self.assertTrue(r1.granted)
        self.assertFalse(r2.granted)
    
    def test_str_method(self):
        """__str__ sinnvoll."""
        record = ConsentRecord.objects.create(
            user=self.user,
            category=self.category,
            granted=True,
        )
        self.assertIn(self.user.email, str(record))
        self.assertIn('analytics', str(record))


class ConsentServiceTestCase(TestCase):
    """Tests für Consent-Services."""
    
    def setUp(self):
        """Setup für Tests."""
        self.user = User.objects.create_user(
            email='service@example.com',
            username='service_user',
            password='pass123',
        )
        
        self.cat_necessary = ConsentCategory.objects.create(
            key='necessary',
            name='Notwendig',
            is_required=True,
        )
        
        self.cat_analytics = ConsentCategory.objects.create(
            key='analytics',
            name='Analytik',
            is_required=False,
        )
    
    def test_record_consent_with_user(self):
        """record_consent erstellt Record mit User."""
        record = record_consent(
            category=self.cat_analytics,
            granted=True,
            user=self.user,
            source='banner',
        )
        self.assertEqual(record.user, self.user)
        self.assertTrue(record.granted)
        self.assertEqual(record.source, 'banner')
    
    def test_record_consent_with_session(self):
        """record_consent erstellt Record mit session_key."""
        record = record_consent(
            category=self.cat_analytics,
            granted=False,
            session_key='test-session',
            source='banner',
        )
        self.assertEqual(record.session_key, 'test-session')
        self.assertFalse(record.granted)
    
    def test_record_consent_with_category_key(self):
        """record_consent kann category_key string akzeptieren."""
        record = record_consent(
            category='analytics',  # String statt Objekt
            granted=True,
            user=self.user,
        )
        self.assertEqual(record.category.key, 'analytics')
    
    def test_record_consent_requires_user_or_session(self):
        """record_consent verlangt user oder session_key."""
        with self.assertRaises(ConsentError):
            record_consent(
                category=self.cat_analytics,
                granted=True,
            )
    
    def test_record_consent_with_ip_and_user_agent(self):
        """record_consent speichert optional IP und User-Agent."""
        record = record_consent(
            category=self.cat_analytics,
            granted=True,
            user=self.user,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0...',
        )
        self.assertEqual(record.ip_address, '192.168.1.1')
        self.assertIn('Mozilla', record.user_agent)
    
    def test_get_latest_consent(self):
        """get_latest_consent liefert neuesten Record pro Kategorie."""
        # Erstelle zwei Records für verschiedene Kategorien
        record_consent(
            category=self.cat_necessary,
            granted=True,
            user=self.user,
        )
        record_consent(
            category=self.cat_analytics,
            granted=False,
            user=self.user,
        )
        
        latest = get_latest_consent(user=self.user)
        self.assertIn('necessary', latest)
        self.assertIn('analytics', latest)
        self.assertTrue(latest['necessary'].granted)
        self.assertFalse(latest['analytics'].granted)
    
    def test_get_latest_consent_empty(self):
        """get_latest_consent returns empty dict ohne Records."""
        latest = get_latest_consent(user=self.user)
        self.assertEqual(latest, {})
    
    def test_has_consent_true(self):
        """has_consent true bei granted=True."""
        record_consent(
            category=self.cat_analytics,
            granted=True,
            user=self.user,
        )
        
        result = has_consent('analytics', user=self.user)
        self.assertTrue(result)
    
    def test_has_consent_false(self):
        """has_consent false bei granted=False."""
        record_consent(
            category=self.cat_analytics,
            granted=False,
            user=self.user,
        )
        
        result = has_consent('analytics', user=self.user)
        self.assertFalse(result)
    
    def test_has_consent_false_without_record(self):
        """has_consent false ohne Record für optionale Kategorie."""
        result = has_consent('analytics', user=self.user)
        self.assertFalse(result)
    
    def test_has_consent_true_for_required(self):
        """has_consent true für required/necessary Kategorien."""
        # Kein Record erstellt, aber necessary ist required
        result = has_consent('necessary', user=self.user)
        self.assertTrue(result)
    
    def test_has_consent_with_session_key(self):
        """has_consent funktioniert mit session_key."""
        record_consent(
            category=self.cat_analytics,
            granted=True,
            session_key='session123',
        )
        
        result = has_consent('analytics', session_key='session123')
        self.assertTrue(result)
