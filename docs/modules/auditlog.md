# Auditlog

## Zweck

Technische Infrastruktur für Audit-Logging und Protokollierung kritischer Systemaktionen. Bietet ein unveränderliches Audit-Trail für:
- Admin-Änderungen (Produktpreise, Benutzer-Status, Business-Genehmigungen)
- Geschäfts-Events (Bestellungen erstellt, Bestätigt, Storniert)
- Zugriff und Authentifikation (Login, Logout, priviligierte Aktion)
- Compliance/Legal (Dokumente aktiviert, Versionen gewechselt)

Das Modul ist eine reine **Infrastruktur** – es loggt, aber integriert sich nicht automatisch in andere Module. Integration erfolgt später durch explizite Service-Calls in bestehenden Modulen.

## Fachlicher Status (Arbeitsblock 08)

- Status: **tested** ✅
- Tests: **22 Tests** (8 Modell + 10 Services + 4 Admin) – ALLE PASS
- Freeze-Status: **offen** (Freeze-Decision in 08.1)

## Aufbau

### Datenmodell (AuditLogEntry)

| Feld | Typ | Erforderlich | Notizen |
|---|---|---|---|
| actor | FK User | optional | Wer hat das Ereignis ausgelöst (z.B. Admin-Benutzer) |
| action | CharField(13 choices) | ja | created / updated / deleted / status_changed / activated / archived / approved / rejected / cancelled / converted / login / logout / system |
| entity_type | CharField | ja | Entitäts-Typ (z.B. "orders.Order", "business.BusinessProfile") |
| entity_id | CharField | optional | ID der betroffenen Entität |
| entity_repr | CharField | optional | Lesbare Repräsentation (max 255 Zeichen) |
| message | TextField | ja (default '') | Zusätzlicher Kontext oder Grund |
| changes | JSONField | ja (default {}) | {"field_name": {"old": old_val, "new": new_val}} – nur geänderte Felder |
| metadata | JSONField | ja (default {}) | Strukturierte Zusatzdaten (z.B. approval_reason, price_category) |
| ip_address | GenericIPAddressField | optional | IP-Adresse der HTTP-Anfrage (IPv4 oder IPv6) |
| user_agent | TextField | optional | Browser/Client-Informationen |
| created_at | DateTimeField | ja (auto) | Zeitstempel (UTC) |

### Indizes und Optimierung

- Index auf `action` – schnelle Filterung von Ereignis-Typen
- Index auf `entity_type` – schnelle Filterung von Entitäts-Typen
- Index auf `-created_at` – schnelle Abfrage neuester Einträge
- Ordering: Neueste Einträge zuerst (`-created_at`)

### Services (apps/auditlog/services.py)

#### `create_audit_log()`

```python
def create_audit_log(
    actor=None,              # FK User (optional)
    action='system',         # CharField (required unless provided)
    entity=None,             # Django model instance (optional)
    entity_type=None,        # String (required if entity not provided)
    entity_id=None,          # String (optional)
    entity_repr=None,        # String (optional)
    message='',              # String
    changes=None,            # Dict (optional)
    metadata=None,           # Dict (optional)
    ip_address=None,         # String (optional)
    user_agent=None,         # String (optional)
) -> AuditLogEntry:
```

**Verhalten:**
- Wenn `entity` übergeben: Auto-Erkennung von `entity_type`, `entity_id`, `entity_repr`
- Wenn `entity` nicht übergeben: `entity_type` muss manuell gesetzt sein
- Falls beide missing: Wirft `AuditLogError`
- Speichert Audit-Log in Datenbank

**Beispiel:**
```python
from apps.auditlog.services import create_audit_log

# Manual creation
create_audit_log(
    actor=user,
    action='approved',
    entity_type='business.BusinessProfile',
    entity_id='42',
    entity_repr='Company ABC',
    message='B2B-Freigabe erteilt',
    metadata={'reason': 'Kreditcheck bestanden'}
)

# Auto-detection from Django object
create_audit_log(
    action='updated',
    entity=product,  # Will auto-detect entity_type, entity_id, entity_repr
    changes={'price': {'old': '49.99', 'new': '59.99'}}
)
```

#### `build_change_set()`

```python
def build_change_set(
    before: dict,
    after: dict,
    ignored_fields=None  # List of field names to skip
) -> dict:
```

**Verhalten:**
- Vergleicht before/after Dicts feld-weise
- Ignoriert Felder in `ignored_fields` (z.B. ['password', 'token', 'updated_at'])
- Gibt nur geänderte Felder aus: `{"field": {"old": val1, "new": val2}}`
- Wenn identical: `{}`

**Beispiel:**
```python
from apps.auditlog.services import build_change_set

before = {'name': 'Old', 'password': 'hash1', 'status': 'active'}
after = {'name': 'New', 'password': 'hash2', 'status': 'active'}

changes = build_change_set(before, after, ignored_fields=['password'])
# Result: {'name': {'old': 'Old', 'new': 'New'}}
```

#### `AuditLogError`

Exception geworfen bei Validierungsfehlern (z.B. fehlende entity_type).

### Admin-Interface (Read-Only)

**Eigenschaften:**
- 100% read-only – keine Add/Change/Delete via Admin möglich
- `has_add_permission=False` – Kein Hinzufügen über Admin UI
- `has_change_permission=False` – Kein Bearbeiten über Admin UI
- `has_delete_permission=False` – Kein Löschen über Admin UI
- Logs können nur durch Datenbank-Direkt-Manipulationen gelöscht werden (intentional, für Audit-Trails)

**Display-Felder:**
- list_display: [created_at, actor, action, entity_type, entity_id, entity_repr]
- list_filter: [action, entity_type, created_at]
- search_fields: [actor__email, actor__username, entity_type, entity_id, entity_repr, message]
- fieldsets: Aktion | Entität | Details | Anfrage-Kontext

**Zugriff:**
- Nur Admin-Benutzer können Logs einsehen
- Django-Admin-Authentifikation erforderlich

## Tests (Arbeitsblock 08 – Alle ✅ PASS)

### AuditLogEntryModelTests (8 Tests)
1. ✅ test_create_audit_log_entry_minimal – Minimal-Felder
2. ✅ test_actor_optional – actor optional
3. ✅ test_action_stored – action persistiert
4. ✅ test_entity_type_stored – entity_type persistiert
5. ✅ test_entity_id_entity_repr_optional – Optional-Felder
6. ✅ test_changes_metadata_dicts – JSONFields speichern korrekt
7. ✅ test_str_representation – __str__ sinnvoll
8. ✅ test_ordering_by_created_at_desc – Neueste zuerst

### AuditLogServiceTests (10 Tests)
1. ✅ test_create_audit_log_with_manual_entity_type – Manuell
2. ✅ test_create_audit_log_with_django_entity – Auto-Erkennung
3. ✅ test_create_audit_log_without_entity_raises_error – Fehlerfall
4. ✅ test_create_audit_log_with_actor – Mit actor
5. ✅ test_create_audit_log_without_actor – Ohne actor
6. ✅ test_create_audit_log_defaults – Defaults korrekt
7. ✅ test_build_change_set_detects_changes – Änderungen erkannt
8. ✅ test_build_change_set_ignores_fields – ignored_fields funktioniert
9. ✅ test_build_change_set_no_changes – Keine Änderungen → {}
10. ✅ test_build_change_set_new_fields – Neue Felder erkannt

### AuditLogAdminTests (4 Tests)
1. ✅ test_audit_log_entry_registered – Im Admin registriert
2. ✅ test_audit_log_has_add_permission_false – Add disabled
3. ✅ test_audit_log_has_change_permission_false – Change disabled
4. ✅ test_audit_log_has_delete_permission_false – Delete disabled

## Abhängigkeiten

- **Abhängt von:** accounts.User (FK), Django ORM, PostgreSQL
- **Abhängig von:** Keine (Infrastruktur-Modul)
- **Später Konsumenten:** payments, shipping, orders (für Event-Logging nach 08.1)

## Grenzen und Nicht-Zuständigkeiten

- ❌ **Keine automatischen Signals** – Services müssen manuell aufgerufen werden
- ❌ **Keine automatische Integration** in bestehende Modules (accounts, customers, business, etc.)
- ❌ **Keine Passwort/Token-Protokollierung** – Security by Design (Services akzeptieren keine `password`/`token` in changes)
- ❌ **Nicht im Scope:** Checkout, Payment, Shipping, Frontend, Notifications (andere Arbeitsblöcke)
- ❌ **Keine Signal-basierte Automation** – Verhindert hidden dependencies und unerwartete side effects

## Migrations

- `0001_initial.py` – Tabelle auditlog_auditlogentry mit Indizes
- `0002_alter_auditlogentry_user_agent.py` – user_agent nullable setzen

## Freeze-Status

**Status nach Arbeitsblock 08.1:** ✅ **frozen** | ✅ **eingeforen nach Review**

**Rationale:**
- Fachlicher Erststand vollständig und reviewed
- 22 Tests grün, technisch solide, keine Blocker
- Admin-Interface korrekt read-only konfiguriert
- Keine Secrets, keine automatischen Signals, keine verstecken Dependencies

**Änderungsregel (ab jetzt frozen):**
- Änderungen nur mit dokumentiertem Grund
- Impact-Prüfung erforderlich
- Regressionstest (pytest backend) erforderlich
- Dokumentation aktualisieren

**Nächster Schritt (nach 08.1):**
- Integration in bestehende Module durch explizite Service-Calls beginnen (wenn nötig)
- Dann: Checkout/Payment/Shipping implementieren

## Migrationen und Setup

```bash
# App bereits in INSTALLED_APPS
# Migrations bereits angewendet

# Manuell (falls nötig):
python manage.py makemigrations auditlog
python manage.py migrate
python manage.py pytest backend/apps/auditlog/tests/
```

## Git-Status

- Neue Dateien: `backend/apps/auditlog/` (models.py, services.py, admin.py, apps.py, tests/test_auditlog.py, migrations/*)
- Modifiziert: `backend/config/settings/base.py` (INSTALLED_APPS)
- Keine `.env`, keine `.venv` committed

