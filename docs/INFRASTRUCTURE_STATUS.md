# Infrastructure Status

## PostgreSQL

- Status: repariert und verwendbar fuer das Django-Backend
- Host: `localhost`
- Port: `5432`
- Datenbankname: `alice_wonder_nails`
- User-Name: `alice_local`
- Passwort: lokal in `.env` gespeichert, nicht dokumentiert
- Die lokale `.env`-Datei ist vorhanden und enthaelt die geforderten `POSTGRES_*`-Schluessel. Werte und Passwort werden nicht dokumentiert.
- Arbeitsblock 02 hat eine lokale `.env`-Strukturkorrektur ohne Ausgabe von Werten durchgefuehrt.
- `scripts/setup_postgres_local.ps1` liest zuerst `.env`, nutzt fehlende Werte aus `backend/.env.example` als Fallback, fragt Adminuser und Adminpasswort interaktiv ab und richtet Rolle, Datenbank, Owner und Rechte per Python/psycopg ein.
- `scripts/check_postgres.ps1` prueft Port, direkten DB-Login, Django-DB-Zugriff und `manage.py check`.
- PostgreSQL-Zugang wurde lokal manuell repariert.
- `.venv\Scripts\python.exe backend\manage.py migrate` wurde erfolgreich ausgefuehrt.
- `.venv\Scripts\python.exe -m pytest backend` wurde erfolgreich ausgefuehrt: 10 Tests bestanden.
- PostgreSQL ist fuer das Django-Backend verwendbar.
- Arbeitsblock 02 darf nach Arbeitsblock 01.5 starten.
- Arbeitsblock 02 hat die lokale Entwicklungsdatenbank `alice_wonder_nails` fuer das Custom User Model kontrolliert neu initialisiert.
- Reset-Grenze: nur lokales `public`-Schema der Projekt-Datenbank, keine anderen Datenbanken.
- Preflight vor Reset: vorhandene Django-Tabellen, aber keine User in `auth_user`.
- `alice_local` hat lokal `CREATEDB`, damit pytest-django die Testdatenbank erstellen kann.
- `scripts\check_postgres.ps1` ist nach Arbeitsblock 02 gruen.
- **Lokaler Status (AB 13.1)**: ✅ PostgreSQL lokal grün, 271 Tests PASS

## Django Deployment Readiness (AB 13.1)

### Local Development
- Status: ✅ GREEN
- `django check`: 0 issues
- `makemigrations --check`: 0 pending migrations
- `pytest backend`: 271/271 tests PASS (262 baseline + 1 rollback + 8 admin immutability)
- Atomicity fixes: ✅ IMPLEMENTED (transaction.atomic + select_for_update)
- Admin readonly protection: ✅ IMPLEMENTED (comprehensive readonly_fields)

### Production Deployment (via check --deploy)
- Status: ⚠️ YELLOW (NOT READY - 5 warnings, 0 errors)
- Test Command: `.venv\Scripts\python.exe backend\manage.py check --deploy --settings=config.settings.production`
- Warnings (expected for development project):
  1. **security.W004**: SECURE_HSTS_SECONDS not set → HTTP Strict Transport Security not configured
  2. **security.W008**: SECURE_SSL_REDIRECT not set → SSL redirect not enabled
  3. **security.W009**: SECRET_KEY insufficient complexity → Auto-generated demo key (django-insecure-)
  4. **security.W012**: SESSION_COOKIE_SECURE not set → Session cookies not secure-only
  5. **security.W016**: CSRF_COOKIE_SECURE not set → CSRF cookies not secure-only
- Assessment: **NOT PRODUCTION-READY**
  - Local/Development: ✅ Usable
  - Staging: ⚠️ Not yet
  - Production: ❌ Not yet
- Next Steps:
  - Configure security settings before production deployment
  - Generate production-grade SECRET_KEY
  - Enable HTTPS/SSL enforcement
  - Configure secure cookie flags
  - (Defer to future production hardening phase)

## E-Mail

- Status: nicht eingerichtet
- Kein SMTP-Anbieter festgelegt
- Keine echten Zugangsdaten vorhanden
- Spaeter benoetigt fuer Registrierung, Passwort-Reset, Bestellbestaetigung, B2B-Freigaben und Admin-Benachrichtigungen.
- Aktueller Entwicklungsmodus: Console-Mail-Backend als Platzhalterloesung in den Django-Settings vorgesehen.

## Logging

- Status: vorbereitet, noch nicht produktiv abgesichert
- Ziel: lokales Entwicklungslogging, spaetere Produktionslogs, Fehlerlogs, keine Secrets im Log, keine unnoetigen personenbezogenen Daten.
- Aktuell: Django-Logging-Grundstruktur ist vorhanden.

## Secrets

- `.env` lokal ist erlaubt.
- `.env` darf nicht ins Git.
- `.env.example` bleibt nur mit Platzhaltern.
- Keine echten Secrets in README, Docs oder Abschlussberichte.
- Lokale Tests duerfen `.env` pruefen, aber keine Passwoerter ausgeben.
- Der PostgreSQL-Fix wurde ohne Dokumentation von Secrets festgehalten.

## REST API Infrastructure – Arbeitsblock 14

### DRF Integration Status
- Status: ✅ GREEN (local/dev)
- Framework: Django REST Framework >= 3.15
- App: `apps.api` registered in INSTALLED_APPS
- URLs: `config/urls.py` routing `api/` prefix
- Endpoints: 7 read-only endpoints via @api_view(['GET'])
- Serializers: 8 ModelSerializers (all read-only)
- Tests: 33 new tests in `backend/apps/api/tests/test_api.py`
- Test Status: ✅ ALL PASSING (33/33)
- Total Test Count: 304 (271 baseline + 33 API)
- Regression: 0 (all pre-existing tests still passing)

### API Response Format
- Standardized envelope: `{success: true/false, data: [...], error: {code, message}}`
- Status 200: `{success: true, data: [...]}`
- Status 400: `{success: false, error: {code: "invalid_customer_group", message: "..."}}`
- Status 404: `{success: false, error: {code: "not_found", message: "..."}}`
- Status 405: DRF auto-rejection (POST on @api_view(['GET']))
- No secrets in responses, no stack traces exposed

### Endpoints Deployed (Arbeitsblock 14)
| Endpoint | Status | Test Coverage |
|----------|--------|----------------|
| GET /api/v1/health/ | ✅ Working | 4/4 tests |
| GET /api/v1/catalog/categories/ | ✅ Working | 3/3 tests |
| GET /api/v1/catalog/products/ | ✅ Working | 6/6 tests |
| GET /api/v1/catalog/products/<slug>/ | ✅ Working | 4/4 tests |
| GET /api/v1/shipping/methods/ | ✅ Working | 4/4 tests |
| GET /api/v1/payments/methods/ | ✅ Working | 4/4 tests |
| GET /api/v1/legal/active/ | ✅ Working | 3/3 tests |
| Boundary Tests (POST rejection) | ✅ Working | 4/4 tests |

### Local/Dev Status (After AB 14.1)
- PostgreSQL: ✅ GREEN
- Django check: ✅ PASS (0 issues)
- Migrations: ✅ UP TO DATE
- API tests: ✅ 33/33 PASS
- Regression tests: ✅ 304/304 PASS
- Production check --deploy: ⚠️ YELLOW (5 warnings, same as AB 13.1)

### Production Status (After AB 14.1)
- Status: ❌ NOT READY (same warnings as AB 13.1)
- Warnings persist: security.W004, W008, W009, W012, W016
- Security hardening: Deferred to future production deployment phase
- API Deployment: NO API DEPLOYMENT TO PRODUCTION IN AB 14

### Change Tracking
- DRF version: locked to `>=3.15` in requirements.txt
- API version: v1 (frozen, non-locked)
- Response schema: frozen
- Endpoint count: 7 (frozen until next business release)
- Test count: 33 API tests (growing to 304+ in later blocks)
