# Core Module

## Modulzweck

Das **Core-Modul** ist die technische Basis des Django-Backends. Seine Aufgabe:

1. Bereitstellung eines stabilen **Health-Check-Endpunktes** für Diagnostik und Monitoring
2. Routing für Backend-Basis-Endpoints
3. Keine fachliche Business-Logik, keine Datenbankmodelle, keine Admin-Funktionen

Das Core-Modul bleibt bewusst **minimal und technisch**, um Abhängigkeitszirkeln zu vermeiden und eine klare Architektur zu halten.

---

## Modulgrenzen

### Core enthält:

- **Health-Check-View:** `views.py` – Simple Funktion, die `{'status': 'ok', 'service': '...'}` zurückgibt
- **URL-Routing:** `urls.py` – Mapping von `/api/health/` zur Health-View
- **App-Konfiguration:** `apps.py` – Standard Django AppConfig
- **Tests:** `tests/test_health.py` – 3 Tests für Health-Endpunkt

### Core enthält NICHT:

- **Keine Datenbankmodelle** – Core hat keine `models.py`
- **Keine Migrationen** – Keine Abhängigkeit auf Datenbank-Schema-Änderungen
- **Keine Admin-Oberfläche** – Keine Django Admin Registration
- **Keine Geschäftslogik** – Keine Shop-, Benutzer-, Katalog- oder Bestelllogik
- **Keine Authentifizierung** – Health-Check ist öffentlich und stateless
- **Keine komplexen Dependencies** – Abhängigkeiten nur auf Django Core Framework

---

## Abhängigkeiten

### Externe Abhängigkeiten:

- Django Core Framework (implizit in `INSTALLED_APPS`)
- `django.http.JsonResponse` (Standard)

### Abhängigkeiten zu anderen Modulen:

- **Keine Rückwärts-Abhängigkeiten** – Kein anderes Modul importiert aus Core
- **Keine Vorwärts-Abhängigkeiten** – Core importiert keine Fach-Module (accounts, catalog, etc.)

### Abhängigkeiten VON anderen Modulen auf Core:

- Implizit: Core wird durch `config.urls` registered und mounted
- Das ist eine Routing-Abhängigkeit, keine Code-Abhängigkeit

---

## Endpunkte

### GET `/api/health/`

**Beschreibung:**  
Liefert den aktuellen Health-Status des Backends.

**Response (200 OK):**
```json
{
  "status": "ok",
  "service": "alice-wonder-nails-backend"
}
```

**Besonderheiten:**
- Keine Datenbank-Query
- Stateless Response
- Immer 200 OK (keine Error-Logik)
- Keine Authentifizierung erforderlich

**Hinweis:**  
Es existiert auch ein `/api/v1/health/` Endpunkt in der API App (DRF-basiert, ausführlichere Response). Die beiden Health-Endpunkte haben unterschiedliche Response-Formate:
- Core (`/api/health/`): Einfach (status + service)
- API v1 (`/api/v1/health/`): Ausführlich (status + service + version + environment)

Diese Unterscheidung ist gewünscht und dokumentiert in `docs/API_CONTRACTS.md`.

---

## Testabdeckung

### Vorhandene Tests

Datei: `backend/apps/core/tests/test_health.py`

Klasse: `HealthCheckTest` (SimpleTestCase – keine Datenbank erforderlich)

Tests:

1. **`test_health_endpoint_returns_ok`**
   - Prüft: HTTP 200 OK
   - Prüft: Response ist `{'status': 'ok', 'service': 'alice-wonder-nails-backend'}`

2. **`test_health_response_format_is_valid_json`**
   - Prüft: Response ist gültiges JSON
   - Prüft: Required Fields existieren (status, service)
   - Prüft: Field-Werte sind korrekt

3. **`test_health_endpoint_no_database_required`**
   - Prüft: Health-Endpunkt funktioniert ohne Datenbank
   - Rationale: SimpleTestCase erzeugt keine Test-DB; Test bestätigt, dass Health-View unabhängig vom DB-State ist

### Test-Philosophie

- **Minimal:** Nur 3 Tests für ein minimales Modul
- **DB-unabhängig:** Alle Tests erben von SimpleTestCase (keine DB-Setup)
- **Stabil:** Tests prüfen nur essenzielle Anforderungen, nicht Implementierungsdetails

---

## Freeze-Kriterien

Das Core-Modul kann **Frozen** werden, wenn:

1. ✅ **Zweck klar definiert** – Technische Basis, Health-Check, kein Fachlogik
2. ✅ **Grenzen dokumentiert** – In dieser Datei (modules/core.md)
3. ✅ **Tests bestanden** – 3 Tests grün, keine DB-Abhängigkeit
4. ✅ **Keine Fach-Dependencies** – Keine Imports aus accounts, catalog, orders, etc.
5. ✅ **Django system check bestanden** – `manage.py check` = 0 issues
6. ✅ **pytest bestanden** – Alle 304 Tests grün, kein Regression
7. ✅ **Dokumentation aktualisiert** – Diese Datei + MODULE_STATUS.md + PROGRESS.md

---

## Abhängigkeiten zu anderen Modulen prüfen

### Importiert Core andere Module?

```python
# backend/apps/core/views.py
from django.http import JsonResponse

# backend/apps/core/urls.py
from django.urls import path
from .views import health

# backend/apps/core/apps.py
from django.apps import AppConfig
```

✅ **Keine Imports aus Fach-Modulen.** Core hat keine Abhängigkeiten auf andere App-Module.

### Werden andere Module durch Core beeinflusst?

✅ **Nein.** Core ist ein reiner Basis-Service, der von anderen Modulen nicht aufgerufen wird.

---

## Migration / Version-Handling

- **Migrationen:** Nicht erforderlich (keine Models)
- **Versionierung:** Core-Version folgt Backend-Versionierung
- **Breaking Changes:** Keine bekannten zukünftigen Breaking Changes

---

## Status nach AB 16

| Kriterium | Status | Notizen |
|-----------|--------|---------|
| Zweck definiert | ✅ OK | Technische Basis + Health-Check |
| Grenzen dokumentiert | ✅ OK | Diese Datei |
| Tests | ✅ 3 PASS | SimpleTestCase, keine DB |
| Dependencies | ✅ OK | Keine zu Fach-Modulen |
| Django check | ✅ OK | 0 issues |
| pytest | ✅ 304 PASS | Kein Regression |
| Dokumentation | ✅ OK | Aktuell (modules/core.md) |
| Freeze-Ready | ✅ JA | Kann sofort frozen werden |

---

## Nächste Schritte

Nach AB 16:

1. Core-Modul als **FROZEN** markieren in `docs/MODULE_STATUS.md`
2. Keine Änderungen an Core mehr ohne explizite Freigabe und neuen Arbeitsblock
3. Abhängigkeiten auf Core (z.B. neue Monitoring-Logik) müssen dokumentiert werden

---

## Referenzen

- **Projekt-Master:** `docs/PROJECT_MASTER.md`
- **Backend-Architektur:** `docs/BACKEND_BLUEPRINT.md`
- **Modul-Status:** `docs/MODULE_STATUS.md`
- **API-Verträge:** `docs/API_CONTRACTS.md`
- **Deployment-Plan:** `docs/DEPLOYMENT_PLAN.md`
