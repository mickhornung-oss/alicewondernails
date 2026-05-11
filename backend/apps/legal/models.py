from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class LegalDocument(models.Model):
    """
    Fachlicher Rechtstexttyp.
    Beispiele: Impressum, Datenschutz, AGB B2C, AGB B2B, Widerruf.
    """
    
    DOCUMENT_TYPE_CHOICES = [
        ('imprint', 'Impressum'),
        ('privacy_policy', 'Datenschutzrichtlinie'),
        ('terms_b2c', 'AGB B2C'),
        ('terms_b2b', 'AGB B2B'),
        ('withdrawal_b2c', 'Widerrufsrecht B2C'),
        ('shipping_info', 'Versandinformation'),
        ('payment_info', 'Zahlungsinformation'),
        ('cookie_policy', 'Cookie-Richtlinie'),
        ('other', 'Sonstiges'),
    ]
    
    TARGET_GROUP_CHOICES = [
        ('all', 'Alle'),
        ('b2c', 'B2C'),
        ('b2b', 'B2B'),
    ]
    
    document_type = models.CharField(
        max_length=32,
        choices=DOCUMENT_TYPE_CHOICES
    )
    title = models.CharField(max_length=255)
    target_group = models.CharField(
        max_length=16,
        choices=TARGET_GROUP_CHOICES,
        default='all'
    )
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    is_required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['document_type', 'target_group', 'title']
        verbose_name = 'Rechtsdokument'
        verbose_name_plural = 'Rechtsdokumente'
    
    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()}) - {self.get_target_group_display()}"


class LegalDocumentVersion(models.Model):
    """
    Versionierter Inhalt eines Rechtstextes.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Entwurf'),
        ('active', 'Aktiv'),
        ('archived', 'Archiviert'),
    ]
    
    document = models.ForeignKey(
        LegalDocument,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    version = models.CharField(max_length=32)
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default='draft'
    )
    content = models.TextField()
    summary = models.TextField(blank=True, null=True)
    effective_from = models.DateTimeField(blank=True, null=True)
    activated_at = models.DateTimeField(blank=True, null=True)
    archived_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='legal_versions_created'
    )
    activated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='legal_versions_activated'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['document', '-created_at']
        verbose_name = 'Rechtsdokument-Version'
        verbose_name_plural = 'Rechtsdokument-Versionen'
        constraints = [
            models.UniqueConstraint(
                fields=['document', 'version'],
                name='unique_document_version'
            ),
        ]
    
    def clean(self):
        """Validierung der aktiven Version."""
        if self.status == 'active' and not self.content:
            raise ValidationError('Aktive Version muss Content enthalten.')
    
    def __str__(self):
        return f"{self.document.title} v{self.version} ({self.get_status_display()})"
