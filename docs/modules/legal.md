# Legal

## Zweck

Das Modul `legal` verwaltet die technische Struktur für Rechtstexte und Rechtsdokumente.

Es speichert:
- Rechtsdokumenttypen (z.B. Impressum, Datenschutz, AGB B2C, AGB B2B, Widerruf)
- Versionen von Rechtsdokumenten
- Status (Entwurf, Aktiv, Archiviert)
- Zielgruppen (alle, B2C, B2B)

Zweck ist es, später:
- Checkout mit aktuellen Rechtstexten zu verknüpfen
- Website-Bereiche mit korrekten Rechtstexten zu versehen
- Account-Benutzer mit ihrer Consent-Version zu verlinken

## Grenzen dieses Moduls

Das Modul `legal` baut NICHT:
- Finale Rechtstexte (Inhalte sind technische Platzhalter)
- Rechtsberatung
- Checkout-Funktion
- Payment-Integration
- Versandlogik
- Rechnungslogik
- E-Mail-Funktion
- Cookie-Banner-Frontend
- Consent-Records (das ist das Modul `consent`)
- Frontend-Views

## Modelle

### LegalDocument

Fachlicher Rechtstexttyp.

**Felder:**
- `document_type` (choices): imprint, privacy_policy, terms_b2c, terms_b2b, withdrawal_b2c, shipping_info, payment_info, cookie_policy, other
- `title` (CharField): Titel des Dokuments
- `target_group` (choices): all, b2c, b2b (default: all)
- `slug` (SlugField): eindeutig
- `description` (TextField optional): Interne Beschreibung
- `is_required` (BooleanField): Ob dieses Dokument erforderlich ist (default: True)
- `created_at`, `updated_at`

**Ordering:** Nach document_type, target_group, title

### LegalDocumentVersion

Versionierter Inhalt eines Rechtstextes.

**Felder:**
- `document` (ForeignKey): Verweis auf LegalDocument (CASCADE)
- `version` (CharField): Versionsnummer (z.B. "1.0", "2.0")
- `status` (choices): draft, active, archived (default: draft)
- `content` (TextField): Der eigentliche Rechtstext
- `summary` (TextField optional): Kurzzusammenfassung
- `effective_from` (DateTimeField optional): Ab wann gültig
- `activated_at` (DateTimeField optional): Wann aktiviert
- `archived_at` (DateTimeField optional): Wann archiviert
- `created_by` (ForeignKey optional): User, der die Version erstellt hat
- `activated_by` (ForeignKey optional): User, der die Version aktiviert hat
- `created_at`, `updated_at`

**Constraints:**
- Eindeutig: (document, version)

**Ordering:** Nach document, -created_at

## Services

### get_active_document_version(document_type, target_group='all')

Sucht die aktive Version eines Dokumenttyps mit optionalem Fallback auf 'all'.

### activate_document_version(version, user=None)

Aktiviert eine Version und archiviert vorherige aktive Versionen.

### archive_document_version(version, user=None)

Archiviert eine Version.

## Admin

- LegalDocumentAdmin: list_display, list_filter, search_fields, prepopulated_fields, inlines
- LegalDocumentVersionAdmin: list_display, list_filter, search_fields, raw_id_fields, readonly_fields

## Tests

18 Tests für legal Module (Modelle, Services).

## Freeze-Status

- **Status**: frozen ✅
- **Tests**: grün (18 legal Tests) ✅
- **Freeze-Datum**: Arbeitsblock 07.1 Review bestanden
- **Notiz**: Stabiler Erststand, alle Anforderungen erfüllt

## Änderungsregel (frozen status)

Dieses Modul ist nun **frozen**. Das bedeutet:

1. Das Modul ist in stabilem Zustand mit vollem Test-Coverage
2. Zukünftige Änderungen sind möglich, aber NUR mit:
   - Dokumentiertem Grund (z.B. "Checkout braucht zusätzliche XYZ Funktion")
   - Überprüftem Impact (z.B. "würde Bestellung beeinflussen")
   - Neuen oder erweiterten Regressionstests
   - Genehmigung der Projekt-Leitung

3. Typische Gründe für zukünftige Änderungen:
   - Checkout-Modul braucht neue Felder/Services
   - Frontend-Integration braucht API-Erweiterung
   - Admin-Modul braucht neue Funktionalität
   - Audit-Log braucht Nachverfolgung

4. NICHT erlaubt:
   - Refactorings ohne Grund
   - Optische Verbesserungen ohne Notwendigkeit
   - Experimente auf bestehendem Code
   - Breaking Changes zu Service-Interfaces
