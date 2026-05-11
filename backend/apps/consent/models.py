from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class ConsentCategory(models.Model):
    """
    Consent-Kategorie, z. B. necessary, analytics, marketing, preferences.
    """
    
    KEY_CHOICES = [
        ('necessary', 'Notwendig'),
        ('analytics', 'Analytik'),
        ('marketing', 'Marketing'),
        ('preferences', 'Einstellungen'),
    ]
    
    key = models.CharField(
        max_length=32,
        unique=True,
        choices=KEY_CHOICES
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_required = models.BooleanField(
        default=False,
        help_text='necessary-Kategorie sollte required sein'
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'key']
        verbose_name = 'Consent-Kategorie'
        verbose_name_plural = 'Consent-Kategorien'
    
    def __str__(self):
        return f"{self.name} ({self.key})"


class ConsentRecord(models.Model):
    """
    Konkrete Zustimmung oder Ablehnung eines Users oder einer anonymen Session.
    """
    
    SOURCE_CHOICES = [
        ('banner', 'Banner'),
        ('account', 'Account'),
        ('admin', 'Admin'),
        ('system', 'System'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='consent_records'
    )
    session_key = models.CharField(
        max_length=80,
        blank=True,
        null=True,
        db_index=True
    )
    category = models.ForeignKey(
        ConsentCategory,
        on_delete=models.CASCADE,
        related_name='consent_records'
    )
    granted = models.BooleanField()
    consent_version = models.CharField(
        max_length=32,
        default='v1'
    )
    source = models.CharField(
        max_length=16,
        choices=SOURCE_CHOICES,
        default='banner'
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True
    )
    user_agent = models.TextField(
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Consent-Record'
        verbose_name_plural = 'Consent-Records'
    
    def clean(self):
        """user oder session_key muss vorhanden sein."""
        if not self.user and not self.session_key:
            raise ValidationError('Entweder user oder session_key muss vorhanden sein.')
    
    def __str__(self):
        user_or_session = (
            f"{self.user.email}" if self.user 
            else f"Session:{self.session_key}"
        )
        status = 'Granted' if self.granted else 'Denied'
        return f"{user_or_session} - {self.category.key} - {status}"
