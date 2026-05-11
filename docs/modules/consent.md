# Consent

## Zweck

Das Modul `consent` verwaltet die technische Struktur für Benutzer-Zustimmungen zu verschiedenen Kategorien.

Es speichert:
- Consent-Kategorien (notwendig, analytik, marketing, einstellungen)
- Consent-Records (Zustimmung oder Ablehnung pro User/Session und Kategorie)
- Source der Zustimmung (Banner, Account-Einstellungen, Admin, System)

Zweck ist es, später:
- Cookie-Banner-Logik umzusetzen
- Tracking/Analytics-Consent zu verwalten
- Marketing-Consent zu verwalten
- Benutzereinstellungen zu speichern

## Grenzen dieses Moduls

Das Modul `consent` baut NICHT:
- Cookie-Banner-Frontend (nur Backend-Struktur)
- Tracking-Integration
- Marketing-Tools
- Finale Datenschutztexte (das ist Modul `legal`)
- Checkout-Funktion
- Payment-Integration
- Versandlogik
- Rechnungslogik
- E-Mail-Funktion
- Frontend-Views

## Modelle

### ConsentCategory

Kategorie für Benutzer-Zustimmungen.

**Felder:**
- `key` (CharField unique): necessary, analytics, marketing, preferences
- `name` (CharField): Display-Name
- `description` (TextField optional): Interne Beschreibung
- `is_required` (BooleanField): Ob zwingend erforderlich (default: False)
- `is_active` (BooleanField): Ob aktiv (default: True)
- `sort_order` (IntegerField): Sortierungsreihenfolge (default: 0)
- `created_at`, `updated_at`

### ConsentRecord

Konkrete Zustimmung oder Ablehnung für eine Kategorie.

**Felder:**
- `user` (ForeignKey optional): User instance (wenn eingeloggt)
- `session_key` (CharField optional): Session-Key (für anonyme Besucher)
- `category` (ForeignKey): Verweis auf ConsentCategory (CASCADE)
- `granted` (BooleanField): True = zugestimmt, False = abgelehnt
- `consent_version` (CharField): Version (default: "v1")
- `source` (choices): banner, account, admin, system (default: banner)
- `ip_address` (GenericIPAddressField optional): IP-Adresse des Besuchers
- `user_agent` (TextField optional): User-Agent-String
- `created_at` (DateTimeField): Zeitstempel

**Constraints:**
- user ODER session_key muss vorhanden sein

## Services

### record_consent(category, granted, user=None, session_key=None, source='banner', consent_version='v1', ip_address=None, user_agent=None)

Erstellt einen Consent-Record.

### get_latest_consent(user=None, session_key=None)

Liefert pro Kategorie den neuesten ConsentRecord.

### has_consent(category_key, user=None, session_key=None)

Prüft, ob Consent für eine Kategorie vorhanden ist.

## Admin

- ConsentCategoryAdmin: list_display, list_filter, search_fields
- ConsentRecordAdmin: list_display, list_filter, search_fields, readonly_fields

## Tests

18 Tests für consent Module (Modelle, Services).

## Freeze-Status

- **Status**: frozen ✅
- **Tests**: grün (18 consent Tests) ✅
- **Freeze-Datum**: Arbeitsblock 07.1 Review bestanden
- **Notiz**: Stabiler Erststand, alle Anforderungen erfüllt

## Änderungsregel (frozen status)

Dieses Modul ist nun **frozen**. Das bedeutet:

1. Das Modul ist in stabilem Zustand mit vollem Test-Coverage
2. Zukünftige Änderungen sind möglich, aber NUR mit:
   - Dokumentiertem Grund (z.B. "Cookie-Banner braucht zusätzliche Kategorien")
   - Überprüftem Impact (z.B. "würde User-Consent-Abfrage beeinflussen")
   - Neuen oder erweiterten Regressionstests
   - Genehmigung der Projekt-Leitung

3. Typische Gründe für zukünftige Änderungen:
   - Cookie-Banner-Frontend braucht neue Kategorien
   - Legal-Modul braucht Consent-Verknüpfung
   - Checkout braucht Consent-Validierung
   - Admin-Modul braucht Consent-Reporting

4. NICHT erlaubt:
   - Refactorings ohne Grund
   - Optische Verbesserungen ohne Notwendigkeit
   - Experimente auf bestehendem Code
   - Breaking Changes zu Service-Interfaces
