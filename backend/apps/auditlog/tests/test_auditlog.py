from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from ..models import AuditLogEntry
from ..services import create_audit_log, build_change_set, AuditLogError


User = get_user_model()


class AuditLogEntryModelTests(TestCase):
    """Tests für AuditLogEntry Modell."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='pass123'
        )
    
    def test_create_audit_log_entry_minimal(self):
        """AuditLogEntry kann mit Minimal-Feldern erstellt werden."""
        entry = AuditLogEntry.objects.create(
            action='created',
            entity_type='accounts.User',
        )
        self.assertEqual(entry.action, 'created')
        self.assertEqual(entry.entity_type, 'accounts.User')
        self.assertIsNone(entry.actor)
        self.assertIsNone(entry.entity_id)
        self.assertIsNone(entry.entity_repr)
        self.assertEqual(entry.changes, {})
        self.assertEqual(entry.metadata, {})
    
    def test_actor_optional(self):
        """actor ist optional."""
        entry1 = AuditLogEntry.objects.create(
            action='system',
            entity_type='orders.Order',
        )
        self.assertIsNone(entry1.actor)
        
        entry2 = AuditLogEntry.objects.create(
            actor=self.user,
            action='approved',
            entity_type='business.BusinessProfile',
        )
        self.assertEqual(entry2.actor, self.user)
    
    def test_action_stored(self):
        """action wird gespeichert."""
        entry = AuditLogEntry.objects.create(
            action='updated',
            entity_type='catalog.Product',
        )
        self.assertEqual(entry.action, 'updated')
    
    def test_entity_type_stored(self):
        """entity_type wird gespeichert."""
        entry = AuditLogEntry.objects.create(
            action='created',
            entity_type='orders.OrderItem',
        )
        self.assertEqual(entry.entity_type, 'orders.OrderItem')
    
    def test_entity_id_entity_repr_optional(self):
        """entity_id und entity_repr sind optional."""
        entry = AuditLogEntry.objects.create(
            action='status_changed',
            entity_type='business.BusinessProfile',
            entity_id=None,
            entity_repr=None,
        )
        self.assertIsNone(entry.entity_id)
        self.assertIsNone(entry.entity_repr)
    
    def test_changes_metadata_dicts(self):
        """changes und metadata speichern dicts."""
        changes_data = {'field': {'old': 'val1', 'new': 'val2'}}
        metadata_data = {'key': 'value', 'nested': {'inner': 'data'}}
        
        entry = AuditLogEntry.objects.create(
            action='updated',
            entity_type='catalog.Product',
            changes=changes_data,
            metadata=metadata_data,
        )
        
        self.assertEqual(entry.changes, changes_data)
        self.assertEqual(entry.metadata, metadata_data)
    
    def test_str_representation(self):
        """__str__ gibt sinnvolle Darstellung zurück."""
        entry = AuditLogEntry.objects.create(
            action='created',
            entity_type='accounts.User',
            entity_id='42',
            entity_repr='TestUser',
        )
        str_repr = str(entry)
        self.assertIn('Created', str_repr)
        self.assertIn('accounts.User', str_repr)
        self.assertIn('42', str_repr)
    
    def test_ordering_by_created_at_desc(self):
        """Einträge werden nach -created_at sortiert."""
        entry1 = AuditLogEntry.objects.create(
            action='created',
            entity_type='orders.Order',
        )
        entry2 = AuditLogEntry.objects.create(
            action='updated',
            entity_type='orders.Order',
        )
        
        entries = list(AuditLogEntry.objects.all())
        # Neuester zuerst
        self.assertEqual(entries[0].id, entry2.id)
        self.assertEqual(entries[1].id, entry1.id)


class AuditLogServiceTests(TestCase):
    """Tests für Auditlog Services."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='pass123'
        )
    
    def test_create_audit_log_with_manual_entity_type(self):
        """create_audit_log mit manuellem entity_type."""
        entry = create_audit_log(
            actor=self.user,
            action='approved',
            entity_type='business.BusinessProfile',
            entity_id='123',
            entity_repr='Company ABC',
            message='B2B-Freigabe genehmigt',
        )
        
        self.assertEqual(entry.actor, self.user)
        self.assertEqual(entry.action, 'approved')
        self.assertEqual(entry.entity_type, 'business.BusinessProfile')
        self.assertEqual(entry.entity_id, '123')
        self.assertEqual(entry.entity_repr, 'Company ABC')
        self.assertEqual(entry.message, 'B2B-Freigabe genehmigt')
    
    def test_create_audit_log_with_django_entity(self):
        """create_audit_log mit Django Model-Objekt."""
        # Verwende den User als Entity
        entry = create_audit_log(
            action='created',
            entity=self.user,
        )
        
        self.assertEqual(entry.entity_type, 'accounts.user')
        self.assertEqual(entry.entity_id, str(self.user.pk))
        self.assertEqual(entry.entity_repr, str(self.user)[:255])
    
    def test_create_audit_log_without_entity_raises_error(self):
        """create_audit_log ohne entity und entity_type löst AuditLogError aus."""
        with self.assertRaises(AuditLogError):
            create_audit_log(
                action='updated',
                # Kein entity, kein entity_type
            )
    
    def test_create_audit_log_with_actor(self):
        """create_audit_log mit actor funktioniert."""
        entry = create_audit_log(
            actor=self.user,
            action='login',
            entity_type='accounts.User',
        )
        
        self.assertEqual(entry.actor, self.user)
    
    def test_create_audit_log_without_actor(self):
        """create_audit_log ohne actor speichert None."""
        entry = create_audit_log(
            action='system',
            entity_type='core.System',
        )
        
        self.assertIsNone(entry.actor)
    
    def test_create_audit_log_defaults(self):
        """create_audit_log mit Defaults."""
        entry = create_audit_log(
            action='created',
            entity_type='pricing.ProductPrice',
        )
        
        self.assertEqual(entry.changes, {})
        self.assertEqual(entry.metadata, {})
        self.assertEqual(entry.message, '')
        self.assertIsNone(entry.ip_address)
        self.assertIsNone(entry.user_agent)
    
    def test_build_change_set_detects_changes(self):
        """build_change_set erkennt geänderte Felder."""
        before = {'name': 'Old Name', 'status': 'active'}
        after = {'name': 'New Name', 'status': 'active'}
        
        changes = build_change_set(before, after)
        
        self.assertIn('name', changes)
        self.assertEqual(changes['name']['old'], 'Old Name')
        self.assertEqual(changes['name']['new'], 'New Name')
        self.assertNotIn('status', changes)
    
    def test_build_change_set_ignores_fields(self):
        """build_change_set ignoriert ignored_fields."""
        before = {'name': 'Old Name', 'password': 'old_hash', 'email': 'old@test.com'}
        after = {'name': 'New Name', 'password': 'new_hash', 'email': 'new@test.com'}
        
        changes = build_change_set(before, after, ignored_fields=['password'])
        
        self.assertIn('name', changes)
        self.assertIn('email', changes)
        self.assertNotIn('password', changes)
    
    def test_build_change_set_no_changes(self):
        """build_change_set gibt {} zurück bei keine Änderungen."""
        before = {'name': 'Same Name', 'status': 'active'}
        after = {'name': 'Same Name', 'status': 'active'}
        
        changes = build_change_set(before, after)
        
        self.assertEqual(changes, {})
    
    def test_build_change_set_new_fields(self):
        """build_change_set findet neue Felder."""
        before = {'name': 'Product'}
        after = {'name': 'Product', 'new_field': 'new_value'}
        
        changes = build_change_set(before, after)
        
        self.assertIn('new_field', changes)
        self.assertIsNone(changes['new_field']['old'])
        self.assertEqual(changes['new_field']['new'], 'new_value')


class AuditLogAdminTests(TestCase):
    """Tests für AuditLog Admin."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='pass123'
        )
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='admin123'
        )
        self.client.force_login(self.admin_user)
    
    def test_audit_log_entry_registered(self):
        """AuditLogEntry ist im Django Admin registriert."""
        entry = AuditLogEntry.objects.create(
            action='created',
            entity_type='test.Model',
        )
        
        # Prüfe, dass AuditLogEntry in Django Admin sichtbar ist
        from django.contrib.admin.sites import site
        self.assertIn(AuditLogEntry, [model for model, _ in site._registry.items()])
    
    def test_audit_log_has_add_permission_false(self):
        """Admin-Hinzufügen von Audit-Logs ist deaktiviert."""
        from apps.auditlog.admin import AuditLogEntryAdmin
        from django.contrib.admin.sites import AdminSite
        
        admin_site = AdminSite()
        admin_instance = AuditLogEntryAdmin(AuditLogEntry, admin_site)
        
        self.assertFalse(admin_instance.has_add_permission(self.admin_user))
    
    def test_audit_log_has_change_permission_false(self):
        """Admin-Bearbeiten von Audit-Logs ist deaktiviert."""
        from apps.auditlog.admin import AuditLogEntryAdmin
        from django.contrib.admin.sites import AdminSite
        
        entry = AuditLogEntry.objects.create(
            action='created',
            entity_type='test.Model',
        )
        
        admin_site = AdminSite()
        admin_instance = AuditLogEntryAdmin(AuditLogEntry, admin_site)
        
        self.assertFalse(admin_instance.has_change_permission(self.admin_user, entry))
    
    def test_audit_log_has_delete_permission_false(self):
        """Admin-Löschen von Audit-Logs ist deaktiviert."""
        from apps.auditlog.admin import AuditLogEntryAdmin
        from django.contrib.admin.sites import AdminSite
        
        entry = AuditLogEntry.objects.create(
            action='created',
            entity_type='test.Model',
        )
        
        admin_site = AdminSite()
        admin_instance = AuditLogEntryAdmin(AuditLogEntry, admin_site)
        
        self.assertFalse(admin_instance.has_delete_permission(self.admin_user, entry))
