from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from apps.legal.models import LegalDocument, LegalDocumentVersion
from apps.legal.services import (
    get_active_document_version,
    activate_document_version,
    archive_document_version,
    LegalDocumentError,
)

User = get_user_model()


class LegalDocumentTestCase(TestCase):
    """Tests für LegalDocument-Modell."""
    
    def test_create_legal_document(self):
        """Dokument kann erstellt werden."""
        doc = LegalDocument.objects.create(
            document_type='privacy_policy',
            title='Datenschutz B2C',
            target_group='b2c',
            slug='datenschutz-b2c',
            is_required=True,
        )
        self.assertEqual(doc.title, 'Datenschutz B2C')
        self.assertEqual(doc.target_group, 'b2c')
    
    def test_slug_unique(self):
        """Slug ist eindeutig."""
        LegalDocument.objects.create(
            document_type='privacy_policy',
            title='Datenschutz',
            target_group='all',
            slug='datenschutz-unique',
        )
        
        with self.assertRaises(Exception):  # IntegrityError
            LegalDocument.objects.create(
                document_type='terms_b2c',
                title='AGB',
                target_group='b2c',
                slug='datenschutz-unique',
            )
    
    def test_document_type_choices(self):
        """Document-type choices funktionieren."""
        doc = LegalDocument.objects.create(
            document_type='imprint',
            title='Impressum',
            slug='impressum',
        )
        self.assertEqual(doc.get_document_type_display(), 'Impressum')
    
    def test_target_group_choices(self):
        """Target-group choices funktionieren."""
        doc = LegalDocument.objects.create(
            document_type='terms_b2b',
            title='AGB B2B',
            target_group='b2b',
            slug='agb-b2b',
        )
        self.assertEqual(doc.get_target_group_display(), 'B2B')
    
    def test_str_method(self):
        """__str__ sinnvoll."""
        doc = LegalDocument.objects.create(
            document_type='privacy_policy',
            title='Datenschutz',
            target_group='all',
            slug='datenschutz',
        )
        self.assertIn('Datenschutz', str(doc))
        self.assertIn('Datenschutzrichtlinie', str(doc))


class LegalDocumentVersionTestCase(TestCase):
    """Tests für LegalDocumentVersion-Modell."""
    
    def setUp(self):
        """Setup für Tests."""
        self.doc = LegalDocument.objects.create(
            document_type='privacy_policy',
            title='Datenschutz',
            target_group='all',
            slug='datenschutz',
        )
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
        )
    
    def test_create_version(self):
        """Version kann erstellt werden."""
        version = LegalDocumentVersion.objects.create(
            document=self.doc,
            version='1.0',
            status='draft',
            content='Testzustand Datenschutz.',
            created_by=self.user,
        )
        self.assertEqual(version.version, '1.0')
        self.assertEqual(version.status, 'draft')
    
    def test_document_version_unique(self):
        """Document + version ist eindeutig."""
        LegalDocumentVersion.objects.create(
            document=self.doc,
            version='1.0',
            status='draft',
            content='Content 1',
        )
        
        with self.assertRaises(Exception):  # IntegrityError
            LegalDocumentVersion.objects.create(
                document=self.doc,
                version='1.0',
                status='draft',
                content='Content 2',
            )
    
    def test_active_version_requires_content(self):
        """Aktive Version muss content haben."""
        version = LegalDocumentVersion(
            document=self.doc,
            version='1.0',
            status='active',
            content='',  # Leerer Content
        )
        
        with self.assertRaises(ValidationError):
            version.clean()
    
    def test_str_method(self):
        """__str__ sinnvoll."""
        version = LegalDocumentVersion.objects.create(
            document=self.doc,
            version='1.0',
            status='draft',
            content='Test',
        )
        self.assertIn('Datenschutz', str(version))
        self.assertIn('1.0', str(version))


class LegalServiceTestCase(TestCase):
    """Tests für Legal-Services."""
    
    def setUp(self):
        """Setup für Tests."""
        self.user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass',
        )
        
        self.doc_b2c = LegalDocument.objects.create(
            document_type='terms_b2c',
            title='AGB B2C',
            target_group='b2c',
            slug='agb-b2c',
        )
        
        self.doc_all = LegalDocument.objects.create(
            document_type='privacy_policy',
            title='Datenschutz',
            target_group='all',
            slug='datenschutz',
        )
    
    def test_get_active_document_version(self):
        """Sucht aktive Version nach document_type."""
        version = LegalDocumentVersion.objects.create(
            document=self.doc_all,
            version='1.0',
            status='active',
            content='Datenschutzbestimmungen.',
            created_by=self.user,
        )
        
        found = get_active_document_version('privacy_policy', target_group='all')
        self.assertEqual(found.id, version.id)
    
    def test_get_active_document_version_fallback(self):
        """Fallback auf target_group='all' funktioniert."""
        version = LegalDocumentVersion.objects.create(
            document=self.doc_all,
            version='1.0',
            status='active',
            content='Datenschutzbestimmungen.',
        )
        
        # Suche mit target_group='b2c', sollte auf 'all' zurückfallen
        found = get_active_document_version('privacy_policy', target_group='b2c')
        self.assertEqual(found.id, version.id)
    
    def test_get_active_document_version_error(self):
        """Wirft Fehler, wenn nichts aktiv ist."""
        with self.assertRaises(LegalDocumentError):
            get_active_document_version('terms_b2c', target_group='b2c')
    
    def test_activate_document_version(self):
        """Setzt Version aktiv."""
        v1 = LegalDocumentVersion.objects.create(
            document=self.doc_b2c,
            version='1.0',
            status='draft',
            content='Content 1',
            created_by=self.user,
        )
        
        activated = activate_document_version(v1, user=self.user)
        self.assertEqual(activated.status, 'active')
        self.assertIsNotNone(activated.activated_at)
        self.assertEqual(activated.activated_by, self.user)
    
    def test_activate_document_version_archives_old(self):
        """Archiviert vorherige aktive Version."""
        v1 = LegalDocumentVersion.objects.create(
            document=self.doc_b2c,
            version='1.0',
            status='active',
            content='Content 1',
            created_by=self.user,
        )
        
        v2 = LegalDocumentVersion.objects.create(
            document=self.doc_b2c,
            version='2.0',
            status='draft',
            content='Content 2',
            created_by=self.user,
        )
        
        activate_document_version(v2, user=self.user)
        
        v1.refresh_from_db()
        self.assertEqual(v1.status, 'archived')
        self.assertIsNotNone(v1.archived_at)
    
    def test_archive_document_version(self):
        """Archiviert Version."""
        version = LegalDocumentVersion.objects.create(
            document=self.doc_b2c,
            version='1.0',
            status='active',
            content='Content',
            created_by=self.user,
        )
        
        archived = archive_document_version(version)
        self.assertEqual(archived.status, 'archived')
        self.assertIsNotNone(archived.archived_at)
