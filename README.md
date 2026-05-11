# Alice Wonder Nails

Dies ist jetzt die neue grosse V2-Shop-Version von Alice Wonder Nails.

Die alte statische V1, STRATO-Uploadpakete, Archive und Legacy-Dateien sind nicht mehr Teil dieses Projektordners. Der Nutzer hat den kompletten Projektordner extern gesichert; deshalb werden V1-/Strato-/Legacy-Reste hier nicht weiter archiviert.

## Aktueller Status

- V2 wird backend-first aufgebaut.
- Architektur: Django-basierter modularer Monolith.
- Datenbankziel: lokales PostgreSQL.
- Frontend ist aktuell nicht Teil des aktiven Projektstands und wird spaeter neu angelegt, wenn der Frontend-Block wirklich startet.
- PostgreSQL-Zugang wurde lokal repariert und ist fuer das Django-Backend verwendbar.
- Migrationen wurden erfolgreich ausgefuehrt.
- **Arbeitsblock 08.1**: Auditlog-Review und Freeze abgeschlossen – 156 Tests grün, auditlog eingeforen, ready für 09.
- **Arbeitsblock 09**: Shipping-Grundstruktur gebaut – ShippingZone, ShippingMethod, ShippingRateSnapshot, 42 neue Tests – 198 Tests total grün.
- **Arbeitsblock 11.1**: Checkout-Review und Freeze abgeschlossen – 251 Tests grün, checkout eingeforen, orders vorbereitet.
- **Arbeitsblock 12**: Order-Finalisierung mit Checkout-Snapshots erweitert – 11 neue Tests (7 orders, 4 checkout) – 262 Tests total grün, orders/checkout re-frozen.
- **Arbeitsblock 13**: Senior-Audit Critical Fixes – Atomicity + Admin Protection + Doco Corrections – 9 neue Tests (1 rollback + 8 admin immutability) – **271 Tests total grün**.
- **Arbeitsblock 13.1**: Review der Backend-Konsolidierung – AB 13 Fixes verifiziert, Doku bereinigt, Production-Status dokumentiert.
- **Arbeitsblock 14**: REST API Modul (v1 read-only) gebaut – 7 Endpoints, DRF Integration – 33 neue Tests – **304 Tests total grün** (271 baseline + 33 API).
- **Arbeitsblock 14.1**: Review und Freeze der API-Grundstruktur – Alle Endpoints verifiziert, Doku nachgezogen, API-Modul eingeforen.
- Frozen Module (nach 14): `accounts`, `customers`, `business`, `catalog`, `pricing`, `cart`, `orders`, `checkout`, `legal`, `consent`, `auditlog`, `shipping`, `payments`, `api` (14 Module)
- Aktive Module (nicht gefroren): `core`
- Custom User Model ist aktiv: `accounts.User`.
- Backend-Pytest aktueller Stand: **304 Tests bestanden** (271 baseline + 33 API).
- **REST API**: v1 read-only mit 7 Endpoints (health, catalog, shipping, payments, legal), DRF-basiert, local/dev GREEN
- **Production Deployment**: NOT READY – check --deploy 5 Warnings, local development ready

## Ziel

- Django + Django REST Framework
- PostgreSQL-Integration
- Klare Modulstruktur
- Dokumentierte V2-Shop-Architektur
- Zentrale Tests mit pytest
- Nachfolgende Module fuer Payments, Content, Gallery, Reviews, Notifications
- Aktueller fachlicher Erststand: Accounts/Rollenstatus, CustomerProfile, Address, BusinessProfile, Catalog, Pricing, Cart, Orders, Legal, Consent, Auditlog, Shipping

## Verzeichnisstruktur

- `backend/` - neue Django-V2-Struktur
- `docs/` - V2-Dokumentation
- `docs/modules/` - Modul-Dokumentation fuer V2
- `scripts/` - lokale V2-Start-, Status-, PostgreSQL- und Testskripte

## Lokale Entwicklung

- Backend lokal starten: `scripts\start_backend.ps1`
- Backend-Status pruefen: `scripts\status_backend.ps1`
- Backend-Tests ausfuehren: `scripts\test_backend.ps1`
- PostgreSQL lokal einrichten: `scripts\setup_postgres_local.ps1`
- PostgreSQL pruefen: `scripts\check_postgres.ps1`

## Lokale Pruefung

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_postgres.ps1
.venv\Scripts\python.exe backend\manage.py migrate
.venv\Scripts\python.exe -m pytest backend
```

Der bestaetigte Infrastrukturstand ist gruen. Keine Secrets werden dokumentiert.

Stand nach Arbeitsblock 04:

- `scripts\check_postgres.ps1` gruen
- `manage.py check` gruen
- `makemigrations --check --dry-run` gruen
- `manage.py migrate` gruen
- `pytest backend` gruen, 43 Tests bestanden

Catalog-Stand:

- Kategorien
- Produkte
- Varianten
- Produktbilder
- B2C-/B2B-Sichtbarkeit
- keine Preise, kein Warenkorb, kein Checkout
- Freeze-Status: frozen, nicht locked

Pricing-Stand:

- B2C-/B2B-Preise
- Produkt- und Variantenpreise
- Waehrung und Steuerfelder vorbereitet
- Gueltigkeitszeitraeume und Aktivstatus
- Preisservice und Snapshot-Vorbereitung
- kein Warenkorb, kein Checkout, keine Bestellungen
- Freeze-Status: noch nicht frozen

## Sicherheit

Folgende Inhalte werden nicht versioniert:

- `.env`
- `.venv/`
- `data/`
- `*.sqlite`, `*.sqlite3`, `*.db`
- `*.csv`
- Logs, Caches, Uploads und lokale Entwicklungsartefakte

Keine echten Secrets in Git, README, Dokumentation oder Abschlussberichten.
