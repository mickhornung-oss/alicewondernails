from .models import AuditLogEntry


class AuditLogError(Exception):
    """Exception für Auditlog-Fehler."""
    pass


def create_audit_log(
    actor=None,
    action='system',
    entity=None,
    entity_type=None,
    entity_id=None,
    entity_repr=None,
    message='',
    changes=None,
    metadata=None,
    ip_address=None,
    user_agent=None
):
    """
    Erstellt einen Audit-Log-Eintrag.
    
    Argumente:
    - actor: optionaler Benutzer, der die Aktion durchgeführt hat
    - action: durchgeführte Aktion (default: 'system')
    - entity: Django-Model-Objekt (optional, wird zu entity_type/entity_id/entity_repr)
    - entity_type: Typ der betroffenen Entität (z.B. 'accounts.User', manuell oder aus entity)
    - entity_id: ID der betroffenen Entität (aus entity.pk, falls nicht gesetzt)
    - entity_repr: Lesbare Darstellung (aus str(entity), falls nicht gesetzt)
    - message: Zusätzliche Nachricht (default: '')
    - changes: Dict mit Änderungen (default: {})
    - metadata: Dict mit Metadaten (default: {})
    - ip_address: IP-Adresse der Anfrage (optional)
    - user_agent: User-Agent der Anfrage (optional)
    
    Rückgabewert:
    - AuditLogEntry-Objekt
    
    Raises:
    - AuditLogError: Falls weder entity noch entity_type vorhanden ist
    """
    
    # Defaults
    if changes is None:
        changes = {}
    if metadata is None:
        metadata = {}
    
    # Entity verarbeiten
    if entity is not None:
        # Aus Django-Objekt ableiten
        if entity_type is None:
            app_label = entity._meta.app_label
            model_name = entity._meta.model_name
            entity_type = f"{app_label}.{model_name}"
        
        if entity_id is None:
            entity_id = str(entity.pk)
        
        if entity_repr is None:
            entity_repr = str(entity)[:255]
    
    # Validierung
    if not action:
        raise AuditLogError("action darf nicht leer sein")
    
    if not entity_type:
        raise AuditLogError("entity_type muss entweder über entity oder manuell gesetzt werden")
    
    # Audit-Log erstellen
    log_entry = AuditLogEntry.objects.create(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id or None,
        entity_repr=entity_repr or None,
        message=message,
        changes=changes,
        metadata=metadata,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    return log_entry


def build_change_set(before, after, ignored_fields=None):
    """
    Vergleicht vor/nach Dicts und gibt Änderungen zurück.
    
    Argumente:
    - before: Dict mit alten Werten
    - after: Dict mit neuen Werten
    - ignored_fields: Liste von Feldnamen, die ignoriert werden sollen
    
    Rückgabewert:
    - Dict mit geänderten Feldern: {"field": {"old": old_val, "new": new_val}}
    - Leeres Dict, wenn keine Unterschiede
    """
    
    if ignored_fields is None:
        ignored_fields = []
    
    changes = {}
    
    # Alle Felder in after prüfen
    for field, new_value in after.items():
        if field in ignored_fields:
            continue
        
        old_value = before.get(field)
        
        if old_value != new_value:
            changes[field] = {
                'old': old_value,
                'new': new_value,
            }
    
    return changes
