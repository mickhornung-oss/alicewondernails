from .models import ConsentCategory, ConsentRecord


class ConsentError(Exception):
    """Custom exception für Consent-Service-Fehler."""
    pass


def record_consent(
    category,
    granted,
    user=None,
    session_key=None,
    source='banner',
    consent_version='v1',
    ip_address=None,
    user_agent=None
):
    """
    Erstellt einen ConsentRecord.
    
    Args:
        category: ConsentCategory instance oder category_key string
        granted: bool - True für granted, False für denied
        user: Optional User instance
        session_key: Optional session_key string
        source: 'banner', 'account', 'admin', 'system'
        consent_version: Version string, default 'v1'
        ip_address: Optional IP address
        user_agent: Optional user agent string
    
    Returns:
        ConsentRecord: Der erstellte Record
    
    Raises:
        ConsentError: Bei Validierungsfehlern
    """
    # user oder session_key muss vorhanden sein
    if not user and not session_key:
        raise ConsentError('Entweder user oder session_key muss vorhanden sein.')
    
    # Wenn category ein string ist, suche die ConsentCategory
    if isinstance(category, str):
        try:
            category = ConsentCategory.objects.get(key=category)
        except ConsentCategory.DoesNotExist:
            raise ConsentError(f"ConsentCategory mit key='{category}' nicht gefunden.")
    
    # Erstelle ConsentRecord
    record = ConsentRecord(
        user=user,
        session_key=session_key,
        category=category,
        granted=granted,
        consent_version=consent_version,
        source=source,
        ip_address=ip_address,
        user_agent=user_agent
    )
    record.clean()
    record.save()
    
    return record


def get_latest_consent(user=None, session_key=None):
    """
    Liefert pro Kategorie den neuesten ConsentRecord.
    
    Args:
        user: Optional User instance
        session_key: Optional session_key string
    
    Returns:
        dict: {category_key: ConsentRecord, ...}
    """
    if not user and not session_key:
        return {}
    
    # Query für Records
    records = ConsentRecord.objects.select_related('category')
    
    if user:
        records = records.filter(user=user)
    elif session_key:
        records = records.filter(session_key=session_key)
    
    # Pro Kategorie den neuesten nehmen
    result = {}
    for record in records.order_by('category_id', '-created_at').distinct('category_id'):
        result[record.category.key] = record
    
    return result


def has_consent(category_key, user=None, session_key=None):
    """
    Prüft, ob Consent für eine Kategorie vorhanden ist.
    
    Rules:
    - necessary/required Kategorien: True, wenn kategorie required ist
    - Optionale Kategorien: True nur, wenn neuester Record granted=True
    - Keine Records: False, außer required/necessary
    
    Args:
        category_key: String ('necessary', 'analytics', etc.)
        user: Optional User instance
        session_key: Optional session_key string
    
    Returns:
        bool: True wenn Consent vorhanden/granted, False sonst
    """
    try:
        category = ConsentCategory.objects.get(key=category_key)
    except ConsentCategory.DoesNotExist:
        return False
    
    # Für required/necessary Kategorien: always True
    if category.is_required:
        return True
    
    # Suche neuesten Record
    records = ConsentRecord.objects.filter(category=category)
    
    if user:
        records = records.filter(user=user)
    elif session_key:
        records = records.filter(session_key=session_key)
    else:
        return False
    
    # Neuesten Record nehmen
    record = records.order_by('-created_at').first()
    
    if not record:
        return False
    
    return record.granted
