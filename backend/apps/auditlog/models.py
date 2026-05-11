from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models


# Action Choices für AuditLogEntry
ACTION_CHOICES = [
    ('created', 'Created'),
    ('updated', 'Updated'),
    ('deleted', 'Deleted'),
    ('status_changed', 'Status Changed'),
    ('activated', 'Activated'),
    ('archived', 'Archived'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('cancelled', 'Cancelled'),
    ('converted', 'Converted'),
    ('login', 'Login'),
    ('logout', 'Logout'),
    ('system', 'System'),
]


class AuditLogEntry(models.Model):
    """
    Technischer Audit-Eintrag für wichtige System- und Admin-Aktionen.
    
    Zweck:
    - Admin-Aktionen nachvollziehen
    - B2B-Freigaben protokollieren
    - Preisänderungen protokollieren
    - Rechtstext-Aktivierungen protokollieren
    - Bestellstatusänderungen protokollieren
    - Spätere Checkout-/Payment-/Shipping-relevante Aktionen protokollieren
    """
    
    # Wer hat die Aktion durchgeführt
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_log_entries',
        help_text='Benutzer, der die Aktion durchgeführt hat'
    )
    
    # Was wurde getan
    action = models.CharField(
        max_length=80,
        choices=ACTION_CHOICES,
        help_text='Durchgeführte Aktion'
    )
    
    # Was wurde geändert
    entity_type = models.CharField(
        max_length=120,
        help_text='Typ der betroffenen Entität (z.B. app_label.ModelName)'
    )
    
    # Welche Instanz
    entity_id = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        help_text='ID der betroffenen Entität'
    )
    
    # Lesbare Darstellung
    entity_repr = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Lesbare Darstellung der betroffenen Entität'
    )
    
    # Nachrichten/Kontext
    message = models.TextField(
        blank=True,
        help_text='Zusätzliche Nachricht oder Kontext'
    )
    
    # Geänderte Felder
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text='Änderungen: {"field": {"old": value, "new": value}}'
    )
    
    # Zusätzliche Metadaten
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Zusätzliche Metadaten'
    )
    
    # Anfrage-Kontext
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP-Adresse der Anfrage'
    )
    
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text='User-Agent der Anfrage'
    )
    
    # Zeitstempel
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Zeitstempel des Audit-Eintrags'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Audit Log Entry'
        verbose_name_plural = 'Audit Log Entries'
        indexes = [
            models.Index(fields=['action']),
            models.Index(fields=['entity_type']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} on {self.entity_type} ({self.entity_id}) at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
