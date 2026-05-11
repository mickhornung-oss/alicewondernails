# Backend Blueprint

## Ziel

Das Backend wird als Django-basierter modularer Monolith aufgebaut. Es liefert die technische Infrastruktur fuer Shop, Nutzer, Rollen, Admin, Bestellungen und Content-Management.

## Architektur

- Django 5.x
- Django REST Framework
- PostgreSQL lokal
- Modulares App-Design
- Zentrale Datenbank
- Saubere Settings-Trennung
- `.env`-Konfiguration mit `backend/.env.example`

## Erste Mindestfunktion

- Healthcheck: `GET /api/health/`
- Erste App: `apps.core`
- Fokus: technisches Basisfundament ohne Produktkatalog, Warenkorb oder Checkout.

## Fachlicher Erststand nach Arbeitsblock 02

- `apps.accounts`
- `apps.customers`
- `apps.business`
- Custom User Model: `accounts.User`
- `AUTH_USER_MODEL = 'accounts.User'`
- Django Admin registriert User, CustomerProfile, Address und BusinessProfile.
- Keine oeffentliche Registrierung, kein Login-Frontend und keine vollstaendige API in diesem Block.

## Fachlicher Erststand nach Arbeitsblock 03

- `apps.catalog`
- Modelle: ProductCategory, Product, ProductVariant, ProductImage.
- Catalog bildet Kategorien, Produkte, Varianten, Produktbilder, Farben/Farbwerte, Kollektionen und B2C-/B2B-Sichtbarkeit ab.
- Keine Preise, kein Warenkorb, kein Checkout, kein Payment und keine Versandlogik.
- Catalog ist nach Arbeitsblock 03.1 `frozen`, aber nicht locked.

## Fachlicher Erststand nach Arbeitsblock 04

- `apps.pricing`
- Modell: ProductPrice.
- Pricing bildet B2C-/B2B-Preise fuer Produkte und Varianten ab.
- Preisservice: `get_active_price` und `build_price_snapshot`.
- Snapshot-Vorbereitung fuer spaetere Bestellungen ist vorhanden.
- Keine Warenkorb-, Checkout-, Bestell-, Payment-, Versand- oder Frontend-Logik.
- Pricing ist nach Arbeitsblock 04.1 `frozen`, aber nicht locked.

## Fachlicher Erststand nach Arbeitsblock 05

- `apps.cart`
- Modelle: `Cart`, `CartItem`.
- Eingeloggte und vorbereitete anonyme Warenkoerbe (`session_key`).
- Kundengruppe `b2c`/`b2b`, Status `active`/`converted`/`abandoned`.
- Services: `get_or_create_cart`, `add_item`, `update_item_quantity`, `remove_item`, `clear_cart`, `calculate_cart`.
- `calculate_cart` nutzt den `pricing`-Service (`get_active_price`, `build_price_snapshot`).
- Keine Bestell-, Checkout-, Payment-, Versand-, Rabatt-, Gutschein-, Frontend- oder E-Mail-Logik.
- Cart ist `tested`, aber noch nicht `frozen`.

## Fachlicher Erststand nach Arbeitsblock 06

- `apps.orders`
- Modelle: `Order`, `OrderItem`.
- Order speichert: Bestellnummer, User, Kundengruppe, Status (draft/placed/cancelled/completed), Gesamtsummen, Adress-Snapshots, Zeitstempel.
- OrderItem speichert: Referenzen und echte Snapshots von Produkt/Variante/Preis/Kundengrupppe/Menge/Betrag.
- Services: `generate_order_number`, `build_address_snapshot`, `create_order_from_cart`, `recalculate_order_totals`, `cancel_order`.
- `create_order_from_cart` nutzt den `pricing`-Service (`calculate_cart`) und erzeugt vollstaendige Snapshots.
- Adress-Snapshots bleiben stabil, spaetere Aenderungen an `customers.Address` veraendernde Bestellungen nicht.
- Preis-Snapshots bleiben stabil, spaetere Aenderungen an Preisen veraendernde OrderItems nicht.
- Keine Checkout-, Payment-, Versand-, Rechnungs-, E-Mail- oder Legal-/Consent-Logik.
- Orders ist `tested`, aber noch nicht `frozen`.

## Nicht im ersten Block

- Checkout-Oberflaechenlogik
- Zahlungsabwicklung
- Versandlogik
- Rechnungs-Generierung
- E-Mail-Versand
- Legal-/Consent-Integration
- Nutzerregistrierung
- Rollenverwaltung
- Admin-Oberflaeche jenseits von Django Admin
- Galerie-Upload

## Lokal vorbereitet

- `backend/manage.py`
- `backend/requirements.txt`
- `backend/.env.example`
- `backend/config/`
- `backend/apps/core/`
- `backend/apps/accounts/`
- `backend/apps/customers/`
- `backend/apps/business/`
- `backend/apps/catalog/`
- `backend/apps/pricing/`
- `backend/apps/cart/`
- `backend/apps/orders/`
- `backend/tests/`
- lokale virtuelle Umgebung: `.venv/`

## Infrastruktur-Vorbereitung

- Logging-Grundstruktur in Django ist vorbereitet.
- E-Mail ist als Console-Backend vorbelegt, jedoch nicht produktiv eingerichtet.
- PostgreSQL-Zielzustand ist definiert: DB `alice_wonder_nails`, User `alice_local`, Host `localhost`, Port `5432`.
- Die lokale `.env` enthaelt die benoetigten `POSTGRES_*`-Schluessel; Werte und Passwoerter werden nicht dokumentiert.
- Der PostgreSQL-Zugang wurde lokal repariert und ist fuer das Django-Backend verwendbar.
- Migrationen wurden erfolgreich ausgefuehrt.
- Backend-Pytest wurde erfolgreich ausgefuehrt: 98 Tests bestanden (nach Arbeitsblock 06 mit Orders-Tests).

## Lokale Setup-Hinweise

- Erstelle die lokale venv im Projektstamm: `.venv`
- Installiere Abhaengigkeiten mit `.venv\Scripts\python.exe -m pip install -r backend\requirements.txt`
- PostgreSQL-Setup: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\setup_postgres_local.ps1`
- PostgreSQL-Check: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_postgres.ps1`
- Verifizierter Stand nach Arbeitsblock 02.1: Migrationen und Backend-Pytest sind erfolgreich.

## PostgreSQL-Stand nach Arbeitsblock 01.5

Der PostgreSQL-Zugang wurde lokal manuell repariert. Es werden keine Passwoerter oder Secret-Werte dokumentiert.

Erfolgreich ausgefuehrt:

```powershell
.venv\Scripts\python.exe backend\manage.py migrate
.venv\Scripts\python.exe -m pytest backend
```

## PostgreSQL-Stand nach Arbeitsblock 02

- Fuer das Custom User Model wurde die lokale Entwicklungsdatenbank `alice_wonder_nails` kontrolliert neu initialisiert.
- Preflight vor Reset: bestehende Django-Tabellen vorhanden, aber keine User in `auth_user`.
- Reset betraf nur das `public`-Schema der lokalen Projekt-Datenbank `alice_wonder_nails`.
- Keine anderen Datenbanken wurden angefasst.
- Keine Secrets wurden ausgegeben oder dokumentiert.
- Der lokale Projektuser `alice_local` hat `CREATEDB`, damit pytest-django die Testdatenbank erstellen kann.
- `scripts\check_postgres.ps1` ist gruen.
- `manage.py migrate` ist gruen.
- `manage.py check` ist gruen.
- `pytest backend` ist gruen: 24 Tests bestanden.

## Fachlicher Erststand nach Arbeitsblock 08

- `apps.auditlog` (neu)
- Modell: AuditLogEntry.
- Auditlog bietet Infrastruktur für Audit-Trail-Protokollierung kritischer Systemaktionen.
- Services: `create_audit_log` (Entity-Auto-Erkennung) und `build_change_set` (Änderungserkennung).
- Admin: Vollständig read-only (hat_add_permission=False, has_change_permission=False, has_delete_permission=False).
- 22 Tests grün (AuditLogEntryModelTests, AuditLogServiceTests, AuditLogAdminTests).
- Status: tested, offen für Freeze-Decision in Arbeitsblock 08.1.
- Keine automatischen Signals oder Integration in frozen Module in diesem Block.
- Auditlog ist Infrastruktur – Integration folgt nach Freeze in 08.1.


- `accounts` ist frozen.
- `customers` ist frozen.
- `business` ist frozen.
- Nicht locked.
- Aenderungen an diesen Modulen nur noch mit dokumentiertem Grund, Impact-Pruefung und Regressionstest.

Der folgende SQL-Hinweis bleibt nur als lokale Wiederherstellungsnotiz erhalten; das lokale Projektpasswort kommt aus `.env` und darf nicht in Doku oder Terminalbericht kopiert werden:

## Freeze-Stand nach Arbeitsblock 03.1

- `catalog` ist frozen.
- Nicht locked.
- Aenderungen am Catalog nur noch mit dokumentiertem Grund, Impact-Pruefung und Regressionstest.
- Preislogik bleibt fuer `pricing`, Warenkorb fuer `cart`, Bestellungen fuer `orders`.

```sql
-- Platzhalter ersetzen, Passwort nicht dokumentieren.
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'alice_local') THEN
        CREATE ROLE alice_local WITH LOGIN PASSWORD '<POSTGRES_PASSWORD_AUS_LOKALER_ENV>';
    ELSE
        ALTER ROLE alice_local WITH LOGIN PASSWORD '<POSTGRES_PASSWORD_AUS_LOKALER_ENV>';
    END IF;
END
$$;
```

Wenn die Datenbank noch nicht existiert:

```sql
CREATE DATABASE alice_wonder_nails OWNER alice_local;
GRANT ALL PRIVILEGES ON DATABASE alice_wonder_nails TO alice_local;
```

Wenn die Datenbank bereits existiert:

```sql
ALTER DATABASE alice_wonder_nails OWNER TO alice_local;
\c alice_wonder_nails
ALTER SCHEMA public OWNER TO alice_local;
GRANT USAGE, CREATE ON SCHEMA public TO alice_local;
```

## Fachlicher Erststand nach Arbeitsblock 12

**Order-Finalisierung durch Checkout-Integration**

- `apps.orders` erweitert um Checkout-Snapshot-Felder:
  - Neu: `Order.shipping_amount` (DecimalField, default 0.00, >= 0)
  - Neu: `Order.shipping_snapshot` (JSONField, Audit-Trail für Versandmethode)
  - Neu: `Order.payment_snapshot` (JSONField, Audit-Trail für Zahlungsmethode)
  - Neu: `Order.checkout_snapshot` (JSONField, Checkout-Kontext bei Order-Erzeugung)
  - Neu: CheckConstraint `orders_order_shipping_amount_non_negative` (shipping_amount >= 0)

- `apps.orders` erweitert um neue Service-Funktion:
  - Neu: `apply_checkout_snapshot_to_order(order, checkout)` – Überträgt Versand-/Payment-Snapshots von Checkout zu Order, berechnet Order.total_amount = subtotal + shipping

- `apps.orders` Service aktualisiert:
  - `recalculate_order_totals(order)` – Jetzt: total_amount = subtotal_amount + shipping_amount (vorher nur subtotal)

- `apps.checkout` Service aktualisiert:
  - `create_order_from_checkout(checkout)` – Jetzt: ruft `apply_checkout_snapshot_to_order()` auf, überträgt Snapshots und finalisiert Order.total_amount

- Migration `0002_order_checkout_snapshot_...` erstellt und angewendet (4 Felder + 1 Constraint)

## REST API Layer nach Arbeitsblock 14

### Modul `apps.api` – v1 Read-Only Endpoints

**Ansatz:**
- Django REST Framework (DRF) für standardisierte REST-Architektur
- Function-based views mit `@api_view(['GET'])` decorator
- ModelSerializers für read-only Datenkonvertierung
- Keine POST/PUT/PATCH/DELETE Endpoints

**Endpoints:**

| Endpoint | HTTP | Purpose | Response |
|----------|------|---------|----------|
| `/api/v1/health/` | GET | System status | `{success: true, data: {status, service, version, environment}}` |
| `/api/v1/catalog/categories/` | GET | Product categories | `{success: true, data: [{id, name, slug, sort_order}]}` |
| `/api/v1/catalog/products/` | GET | Product list (b2c/b2b filtered) | `{success: true, data: [{id, name, slug, sku, description}]}` |
| `/api/v1/catalog/products/<slug>/` | GET | Product detail | `{success: true, data: {id, name, slug, sku, description, variants}}` |
| `/api/v1/shipping/methods/` | GET | Shipping methods (customer_group filtered) | `{success: true, data: [{id, name, description}]}` |
| `/api/v1/payments/methods/` | GET | Payment methods (customer_group filtered) | `{success: true, data: [{id, name, description}]}` |
| `/api/v1/legal/active/` | GET | Active legal documents (b2c/b2b) | `{success: true, data: [{id, document_type, title, updated_at}]}` |

**Query Parameters (All Optional):**
- `customer_group`: `b2c` (default) or `b2b` – determines visibility filtering
- `country`: Country code (default `DE`) – for shipping methods
- Unrecognized values → 400 Bad Request

**Response Format:**
```json
{
  "success": true,
  "data": [...]  // or single object
}
```
or on error:
```json
{
  "success": false,
  "error": {
    "code": "invalid_customer_group",
    "message": "Invalid customer_group parameter"
  }
}
```

**Error Handling:**
- 400 Bad Request: Invalid customer_group, validation errors
- 404 Not Found: Product/document not found
- 405 Method Not Allowed: POST/PUT/PATCH/DELETE rejected automatically by DRF
- 500 Internal Server Error: Wrapped in try/except, no stack traces exposed

**Constraints (Intentional):**
- Read-only only; no transactional endpoints
- No order creation
- No payment processing
- No shipping booking
- No authentication required (public data only)
- No pricing in responses
- No secrets in responses

**Testing:**
- 33 comprehensive tests covering:
  - All 7 endpoints
  - Response structure validation
  - customer_group filtering
  - 404 handling
  - POST/PUT/PATCH/DELETE rejection
  - Invalid parameter handling
- All tests passing (304 total: 271 baseline + 33 API)

**Tech Stack:**
- Django 5.2.13
- djangorestframework>=3.15
- Python 3.14.3
- PostgreSQL (local)

**Status:**
- Frozen (non-locked)
- Local/Dev: ✅ GREEN
- Production: ❌ NOT READY (5 security warnings from check --deploy remain)
- Change rule: Document business rationale, assess impact, run regression tests

- **Keine echte Zahlungsausführung, keine echte Versandbuchung** – nur Snapshot-Transfer und Audit-Trail

- `orders` bleibt frozen (aber mit dokumentierter AB 12 Erweiterung)
- `checkout` bleibt frozen (ab AB 11.1, AB 12 Integration validiert)
- Tests: 262 bestanden (251 AB 11.1 + 11 neu AB 12, keine Regression)

**Fachliche Konsequenz**:
- Order-Finalisierung ist nun durch Checkout integriert (Versand + Payment als Snapshots persistent)
- Checkout-Session speichert Versand-/Payment-Entscheidung, Order-Modell historisiert diese
- Gesamtbetrag (total_amount) wird bei Order-Erzeugung final berechnet: subtotal (aus Artikel) + shipping (aus Checkout)
- AB 13 kann starten: Shipping/Payment-Modul-Erweiterungen sind technisch vorbereitet
