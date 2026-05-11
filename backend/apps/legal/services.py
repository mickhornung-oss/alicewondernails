from django.db import transaction
from django.utils import timezone
from .models import LegalDocument, LegalDocumentVersion


class LegalDocumentError(Exception):
    """Custom exception für Legal-Service-Fehler."""
    pass


def get_active_document_version(document_type, target_group='all'):
    """
    Sucht aktive Version nach document_type und target_group.
    Bei Nicht-Finden optional Fallback auf target_group='all'.
    
    Args:
        document_type: Der Dokumenttyp (z.B. 'privacy_policy')
        target_group: Zielgruppe ('b2c', 'b2b', 'all')
    
    Returns:
        LegalDocumentVersion: Die aktive Version
    
    Raises:
        LegalDocumentError: Wenn keine aktive Version gefunden wird
    """
    # Zuerst versuchen, nach target_group zu suchen
    try:
        document = LegalDocument.objects.get(
            document_type=document_type,
            target_group=target_group
        )
        version = document.versions.filter(status='active').first()
        if version:
            return version
    except LegalDocument.DoesNotExist:
        pass
    
    # Fallback auf target_group='all', wenn nicht b2c/b2b gefunden
    if target_group in ('b2c', 'b2b'):
        try:
            document = LegalDocument.objects.get(
                document_type=document_type,
                target_group='all'
            )
            version = document.versions.filter(status='active').first()
            if version:
                return version
        except LegalDocument.DoesNotExist:
            pass
    
    raise LegalDocumentError(
        f"Keine aktive Version für document_type='{document_type}', "
        f"target_group='{target_group}' gefunden."
    )


@transaction.atomic
def activate_document_version(version, user=None):
    """
    Setzt andere aktive Versionen desselben Dokuments auf archived.
    Setzt übergebene Version auf active.
    
    Args:
        version: LegalDocumentVersion instance
        user: Optional User instance für activated_by
    
    Returns:
        LegalDocumentVersion: Die aktivierte Version
    
    Raises:
        LegalDocumentError: Bei Validierungsfehlern
    """
    if not version.content:
        raise LegalDocumentError('Version muss Content enthalten.')
    
    # Archiviere vorherige aktive Versionen desselben Dokuments
    old_active = version.document.versions.filter(
        status='active'
    ).exclude(id=version.id)
    
    now = timezone.now()
    for v in old_active:
        v.status = 'archived'
        v.archived_at = now
        v.save()
    
    # Aktiviere neue Version
    version.status = 'active'
    version.activated_at = now
    version.activated_by = user
    version.save()
    
    return version


@transaction.atomic
def archive_document_version(version, user=None):
    """
    Setzt Version auf archived.
    
    Args:
        version: LegalDocumentVersion instance
        user: Optional (nicht zwingend erforderlich für archivieren)
    
    Returns:
        LegalDocumentVersion: Die archivierte Version
    """
    version.status = 'archived'
    version.archived_at = timezone.now()
    version.save()
    
    return version
