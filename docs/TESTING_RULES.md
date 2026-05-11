# TESTING_RULES

## Fuer Dokumentationsauftrag

Pruefen:

- Alle Pflichtdateien existieren.
- Alle Dateien sind lesbar.
- Keine Dateien ausserhalb des Projektordners erstellt.
- `README.md` verweist auf `docs/PROJECT_RULES.md` und `docs/PROGRESS.md`.
- `docs/PROGRESS.md` enthaelt initialen Eintrag.
- Status ist korrekt gesetzt.

## Spaetere Modul-Tests

- Seite laedt
- Navigation funktioniert
- Bilder laden
- Videos/Platzhalter sichtbar
- Links funktionieren
- Formulare validieren
- Datenschutz-Hinweise sichtbar
- Mobile Lesbarkeit grob geprueft
- Keine Browserfehler
- Keine kaputten Pfade

## Spaetere harte Tests

- Login/Rechte
- Adminfunktionen
- Shoppreise
- Einzelhandel/Grosshandel-Trennung
- Formularmissbrauch
- Kaputte Eingaben
- Sicherheitspruefung

## Lokale Testhinweise

- Verwende die Projekt-venv `.venv/` fuer Backend-Tests.
- Keine globalen pip-Installationen fuer das Projekt erzwingen.
- Keine Fake-Tests: Alle Testergebnisse muessen echt und nachvollziehbar sein.
- Pruefe Infrastrukturtests mit `scripts/check_postgres.ps1`.
- Arbeitsblock 02 darf erst starten, wenn `scripts\check_postgres.ps1`, `.venv\Scripts\python.exe backend\manage.py check`, `.venv\Scripts\python.exe backend\manage.py migrate` und `.venv\Scripts\python.exe -m pytest backend` erfolgreich waren.
- Stand Arbeitsblock 01.5: PostgreSQL-Zugang wurde repariert; `.venv\Scripts\python.exe backend\manage.py migrate` und `.venv\Scripts\python.exe -m pytest backend` wurden erfolgreich ausgefuehrt.
- Arbeitsblock 02 ist freigegeben, solange keine neue Infrastrukturregression auftritt.
- PostgreSQL-Testlaeufe mit pytest-django brauchen lokal die Berechtigung, eine Testdatenbank zu erstellen.
- Stand Arbeitsblock 02: `alice_local` hat lokal `CREATEDB`, damit `.venv\Scripts\python.exe -m pytest backend` gegen PostgreSQL laufen kann.
- Stand Arbeitsblock 02: `manage.py check`, `makemigrations --check --dry-run`, `migrate`, `scripts\check_postgres.ps1` und `pytest backend` waren erfolgreich.
- Stand Arbeitsblock 02.1: Review/Freeze-Regression war gruen; `pytest backend` meldete 10 Tests bestanden.
- Stand Arbeitsblock 03: Catalog-Regression war gruen; `pytest backend` meldete 24 Tests bestanden.

## API-Testing Regeln – Arbeitsblock 14+

### DRF Endpoint-Tests

**Allgemeine Regeln:**
- Alle Endpoints sind GET-only; keine POST/PUT/PATCH/DELETE testen außer um zu beweisen, dass sie 405/400 zurückweisen
- Verwende Django test client: `from django.test import Client`
- Verwende `@tag('api')` um API-Tests zu markieren
- Erwartete Status-Codes: 200 (OK), 400 (Bad Request), 404 (Not Found), 405 (Method Not Allowed)
- Response-Format immer: `{success: bool, data: [...] or {...}, error: {code, message} (if not success)}`

**Read-Only Enforcement:**
- `POST /api/v1/...` must return 400/405
- `PUT /api/v1/...` must return 400/405
- `PATCH /api/v1/...` must return 400/405
- `DELETE /api/v1/...` must return 400/405
- Test dass DRF automatisch POST/PUT/PATCH/DELETE auf @api_view(['GET']) endpoints blockiert

**Parameter Validation:**
- `customer_group` Parameter: test `b2c` (default), `b2b`, and invalid values (`admin`, ``, `null`)
- Invalid customer_group must return 400 with error code "invalid_customer_group"
- `country` Parameter: test valid (`DE`, `AT`, `CH`), missing (default `DE`), and invalid (`ZZ`, ``, `null`)

**404 Handling:**
- Test that missing products return 404 with appropriate error message
- Test that missing documents return 404
- Error response must have: `{success: false, error: {code: 'not_found', message: '...'}}`

**No Secrets in Responses:**
- Verify that no API keys, passwords, secrets, or sensitive data appear in responses
- Verify that no stack traces or internal error details exposed
- Health endpoint must not reveal database connection strings

**Customer Group Filtering:**
- `GET /api/v1/catalog/products/?customer_group=b2c` must return only b2c_visible products
- `GET /api/v1/catalog/products/?customer_group=b2b` must return only b2b_visible products
- `GET /api/v1/shipping/methods/?customer_group=b2c` must return b2c + all-group methods
- `GET /api/v1/payments/methods/?customer_group=b2b` must return b2b + all-group methods
- Test "all" customer_group option where applicable

**Response Envelope:**
- All responses must be wrapped in `{success: true/false, data: ... or error: ...}`
- Verify that response always has `success` key (boolean)
- Verify that `data` key exists when `success: true`
- Verify that `error` key exists when `success: false`
- Error must have `code` (string) and `message` (string)

### Expected Test Count Growth

- AB 14: 33 new API tests (304 total: 271 baseline + 33 API)
- Future blocks may add integration tests or endpoint-specific tests
- All tests must remain in `backend/apps/api/tests/test_api.py`
- Regression test suite always: `pytest backend -q` must pass with 304+ tests

### CI/CD Integration

- In future pipeline: `pytest backend/apps/api/tests/test_api.py -v --tb=short` for API-specific runs
- In future pipeline: `pytest backend -q --tb=no` for full regression test
- No API tests should be skipped in CI/CD (no @skip unless documented with issue link)
- Stand Arbeitsblock 03.1: Catalog-Review/Freeze-Regression war gruen; `pytest backend` meldete 24 Tests bestanden.
- Stand Arbeitsblock 04: Pricing-Regression war gruen; `pytest backend` meldete 43 Tests bestanden.
- Tests fuer FileField/Image-nahe Felder muessen temporaere Medienpfade nutzen und duerfen keine Mediendateien im Projekt hinterlassen.
- Pricing-Tests muessen negative Betraege, negative Steuersaetze, Gueltigkeitszeitraeume, Varianten-/Produktbeziehung, B2C/B2B-Preisfindung, Variantenpreis-Fallback und Snapshots abdecken.
