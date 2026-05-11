# Demo-Daten und Seed-Datenbestand (AB 17)

Dokumentation der Demo-Daten für lokale Entwicklung, Testzwecke und API-Smoke-Tests.

## Überblick

Das Backend wird mit realistischen Demo-Daten geseeded, um:
- Lokale Entwicklung zu unterstützen (API-Endpunkte testen)
- Admin-UI zu testen (Django Admin mit Daten navigierbar)
- Smoke-Tests der API zu ermöglichen
- Frontend-Entwickler mit Beispieldaten zu versorgen

**Alle Demo-Daten sind gekennzeichnet als DEMO PLACEHOLDER - NOT FOR PRODUCTION.**

## ⚠️ HINWEIS: Nur lokale Entwicklung

Der `seed_demo_data` Management Command ist **ausschließlich in der lokalen Entwicklungsumgebung verfügbar**:
- ✅ Lokal: `python backend/manage.py seed_demo_data` (via `config.settings.local`)
- ❌ Production: `apps.devtools` ist in Production-Settings NICHT registriert
- ⚠️ Verwende nur während lokaler Entwicklung / Tests
- ⚠️ Production wird diese Daten NICHT automatisch seeden

## Seed-Daten ausführen

```bash
# Einfach ausführen:
python backend/manage.py seed_demo_data

# Ist vollständig idempotent - mehrfach sicher ausführbar:
python backend/manage.py seed_demo_data
python backend/manage.py seed_demo_data
# Beim 2. Mal: "Already exists" Messages statt duplicates
```

## Seed-Daten Struktur

### 1. Produktkatalog (ProductCategory, Product, ProductVariant)

**Kategorien (4):**
- "Nail Colors" – Gel-Farben, Nagellacke und farbige Produkte
- "Care Products" – Nagelpflege und Wartungsprodukte
- "Sets & Bundles" – Kuratierte Produktsets
- "Accessories" – Nagel-Zubehör und Werkzeuge

**Produkte (8):**
| Produkt | Kategorie | Typ | Visibility | Varianten |
|---------|-----------|-----|------------|-----------|
| Gel Color - Rose Gold | Nail Colors | gel | public | 5ml (default), 10ml XL |
| Polish Classic - Red | Nail Colors | nail_polish | public | 15ml |
| Polish Pro - Azure | Nail Colors | nail_polish | b2c_only | 15ml |
| Nail Oil - Premium | Care Products | care | public | 30ml |
| Nail Primer | Care Products | care | public | 10ml |
| Nail Strengthener | Care Products | care | public | 12ml |
| Starter Set | Sets & Bundles | set | b2c_only | Complete |
| B2B Wholesale Kit | Sets & Bundles | set | b2b_only | 50pcs |

**Varianten (11 gesamt):**
- Mehrere Varianten pro Produkt (z.B. Gel: 5ml Standard + 10ml XL)
- Jede hat eindeutige SKU
- Eine Variante pro Produkt als `is_default=True`

### 2. Preisgestaltung (ProductPrice)

**Struktur:**
- B2C und B2B Preise vorhanden
- 19% MwSt Standard
- `price_includes_tax=True` (EU Standard)
- Alle Preise `is_active=True`

**Beispiel Preise:**
| Produkt | SKU | B2C EUR | B2B EUR |
|---------|-----|---------|---------|
| Gel Color 5ml | GEL-RG-5ML | €12,99 | €8,50 |
| Gel Color 10ml | GEL-RG-10ML | €19,99 | €13,00 |
| Polish Red 15ml | POLISH-RED-15ML | €9,99 | €6,50 |
| Oil Premium 30ml | OIL-PREM-30ML | €18,99 | €12,00 |
| Starter Set (B2C only) | STARTER-SET-001 | €49,99 | — |
| B2B Kit (B2B only) | B2B-KIT-50 | — | €125,00 |

**Gesamt:** ~18 Preiseinträge (Produkt × Variante × customer_group)

### 3. Versand (ShippingZone, ShippingMethod)

**Zonen (2):**

| Code | Name | Länder |
|------|------|--------|
| de_std | Germany Standard | DE |
| eu_ext | EU Extended | AT, CH, NL, BE, FR, IT |

**Methoden (5):**

| Zone | Name | Code | B2C EUR | B2B EUR | Min Days | Max Days |
|------|------|------|---------|---------|----------|----------|
| de_std | Standard (2-3 days) | standard_de | €4,99 | €3,50 | 2 | 3 |
| de_std | Express (next day) | express_de | €9,99 | €6,50 | 1 | 1 |
| de_std | Overnight | overnight_de | €14,99 | €10,00 | 0 | 1 |
| eu_ext | Standard EU (3-5 days) | standard_eu | €8,99 | €5,50 | 3 | 5 |
| eu_ext | Express EU (2 days) | express_eu | €14,99 | €9,99 | 2 | 2 |

**Konventionen:**
- Keine DHL/Hermes/Warenpost echte Integration
- Nur Metadaten (code, name, price, estimated days)
- Kunde wählt eine Methode während Checkout

### 4. Zahlungsmethoden (PaymentMethod)

**Methoden (4):**

| Name | Code | Provider | customer_group | Status |
|------|------|----------|-----------------|--------|
| Bank Transfer | bank_transfer | bank_transfer | all | active |
| Invoice | invoice | invoice | all | active |
| PayPal | paypal | paypal | all | active (Platzhalter) |
| Credit Card | credit_card | stripe | all | active (Platzhalter) |

**Hinweise:**
- Kein echte Stripe/PayPal/Klarna API
- Nur Metadaten für Checkout
- Provider field nur Text-Klassifikation

### 5. Rechtliches (LegalDocument, LegalDocumentVersion)

**Dokumente (4):**

| Typ | Titel | Target Group | Version | Status |
|-----|-------|--------------|---------|--------|
| terms_of_service | Terms of Service | all | 1.0 | active |
| privacy_policy | Privacy Policy | all | 1.0 | active |
| withdrawal_policy | Right of Withdrawal | all | 1.0 | active |
| impressum | Impressum | all | 1.0 | active |

**Content-Vorlagen:**
```
**DEMO PLACEHOLDER - NOT FOR PRODUCTION**

[Document Title]

This is a demo placeholder for [Document Type].
Replace with actual legal terms before going to production.

Last updated: [Date]
Effective: [Date]
```

**Wichtig:**
- Alle Demo-Inhalte sind explizit gekennzeichnet
- Für echte Deployment: Replace mit echten Rechtsdokumenten
- Keine echten Geschäftsangaben

### 6. Zustimmungen (ConsentCategory)

**Kategorien (4):**

| Key | Display Name | Required | Zweck |
|-----|--------------|----------|--------|
| newsletter | Newsletter | No | Newsletter-Subscription opt-in |
| analytics | Analytics | No | Website-Analytics/Tracking |
| marketing | Marketing | No | Personalisierte Werbung |
| terms_accept | Terms & Conditions | Yes | Rechtsverbindlich erforderlich |

**Besonderheiten:**
- `terms_accept` ist required (must be accepted before purchase)
- Andere sind optional (user can opt-out)
- Wird später in Checkout integriert (Checkboxen für Consent)

## Test-Abdeckung

Nach Seed-Run sollten diese Tests PASS:

```bash
# Alle Seed-Tests:
pytest backend apps/devtools/tests/test_seed_demo_data.py -v

# API Smoke-Tests mit geseeded Daten:
curl http://127.0.0.1:8000/api/v1/catalog/categories/
# Response: 200 OK mit 4+ Kategorien

curl "http://127.0.0.1:8000/api/v1/catalog/products/?customer_group=b2c"
# Response: 200 OK mit 5-7 öffentliche Produkte (b2b_only gefiltert)

curl "http://127.0.0.1:8000/api/v1/shipping/methods/?customer_group=b2c&country=DE"
# Response: 200 OK mit 3 Versandmethoden (Standard, Express, Overnight für DE)

curl "http://127.0.0.1:8000/api/v1/payments/methods/?customer_group=b2c"
# Response: 200 OK mit 4 Zahlungsmethoden
```

## Nicht geseeded (intentional)

Die folgenden Module sind **absichtlich nicht** geseeded:

- **User/Accounts:** Keine Test-Nutzer
- **Customers/Addresses:** Keine fiktiven Kundendaten
- **Business Profiles:** Keine fiktiven B2B-Kundenprofile
- **Cart:** Keine Warenkorb-Items (wird während Checkout erstellt)
- **Orders:** Keine Demo-Bestellungen (wird später implementiert)
- **Payments:** Keine Transaktionen (wird durch Checkout erstellt)
- **Checkout:** Keine Sessions (wird durch Benutzer erstellt)

**Begründung:**
- Katalog + Preise + Zonen + Methoden sind stabil und unveränderlich (genug für Tests)
- User/Orders sind transienten (werden dynamisch erstellt)
- AB 17 fokussiert auf "Read-Only" Demo-Daten, nicht auf Transaktionen
- Spätere Blöcke können Orders/Checkout-Seeds hinzufügen

## Idempotenz-Garantie

Der Seed-Command ist **vollständig idempotent:**

```bash
# Run 1: Erstelle alles
$ python manage.py seed_demo_data
✓ Demo data seed completed successfully!

# Run 2: Erkenne Duplikate und skip
$ python manage.py seed_demo_data
✓ Demo data seed completed successfully!
  - ProductCategory: 0 created, 4 skipped
  - Product: 0 created, 8 skipped
  - ProductPrice: 0 created, 18 skipped
  - ...etc
```

**Mechanismus:**
- Prüft `slug` (Kategorien, Produkte) vor Create → `.get_or_create(slug=...)`
- Prüft `code` (Zonen, Methoden, Payment) → `.get_or_create(code=...)`
- Prüft `sku` (Varianten) → `.get_or_create(sku=...)`
- Prüft `category_key` (Consent) → `.get_or_create(category_key=...)`
- Prüft `document_type` (Legal) → `.get_or_create(document_type=...)`

## Lokal verwenden (Entwicklung)

### Setup

```bash
# 1. Backend vorbereiten
cd backend
source ../.venv/Scripts/Activate.ps1  # Windows
python manage.py migrate

# 2. Seed-Daten laden
python manage.py seed_demo_data

# 3. Django Admin testen
python manage.py runserver
# http://127.0.0.1:8000/admin → Login mit Superuser, Daten navigierbar

# 4. API testen
curl http://127.0.0.1:8000/api/v1/catalog/categories/
```

### Zurücksetzen (wenn nötig)

```bash
# Drop alle Daten + re-seed (Vorsicht!):
python manage.py flush --noinput
python manage.py migrate
python manage.py seed_demo_data
```

**Hinweis:** In AB 17 gibt es kein `--force` Flag. Zum Löschen verwend `flush`.

## Production-Deployment

**KRITISCH:**
- ⚠️ Seed-Daten sind NUR für lokale Entwicklung gedacht
- ⚠️ "DEMO PLACEHOLDER" Marker sind absichtlich kennzeichnend
- ✅ Vor Production:
  1. Echte Produkte eingeben (via Django Admin oder CSV-Import, später)
  2. Echte Versandzonen/Methoden konfigurieren
  3. Echte Zahlungsmethoden (mit echten Provider-Keys, später)
  4. Echte Rechtsdokumente (Impressum, Datenschutz, AGB)

## Weitere Seed-Experimente

Die Seed-Strategie kann später erweitert werden:

- **Phase 2**: Orders + OrderItems Seeds (für Order-API-Tests)
- **Phase 3**: Checkout-Sessions (für Checkout-Workflow-Tests)
- **Phase 4**: Audit-Log Seeds (für Audit-Trail-Tests)
- **Phase 5**: CSV-Import für Produktkatalog (für echte Produktverwaltung)

Jede Phase wird separat als Management Command oder JSON-Fixture implementiert.

## API-Integration (AB 18)

Alle seeded Daten sind über die **read-only API v1** verfügbar:

### Verfügbar über API

| Seed-Entität | API-Endpunkt | Query-Parameter | Sichtbarkeit | AB 18 Test |
|--|--|--|--|--|
| Categories | GET /api/v1/catalog/categories/ | — | Public | test_seeded_categories_visible |
| Products | GET /api/v1/catalog/products/ | `customer_group` | B2C/B2B filter | test_seeded_products_b2c_visible |
| Product Detail | GET /api/v1/catalog/products/<slug>/ | `customer_group` | B2C/B2B filter | test_product_detail_by_slug_returns_200 |
| Shipping Methods | GET /api/v1/shipping/methods/ | `customer_group`, `country` | B2C/B2B filter | test_seeded_shipping_methods_visible |
| Payment Methods | GET /api/v1/payments/methods/ | `customer_group` | B2C/B2B filter | test_seeded_payment_methods_visible |
| Legal Documents | GET /api/v1/legal/active/ | `customer_group` | Active versions only | test_seeded_legal_documents_visible |
| **ProductPrice** | **GET /api/v1/pricing/products/<slug>/prices/** | **`customer_group`** | **B2C/B2B filter** | **test_csv_pricing_*** (AB 20 Smoke) |

## CSV-zu-API Smoke Test Matrix (AB 20)

Vollständige Validierung der CSV-Import → API-Kette:

| CSV-Datei | Entities | API-Endpunkt | Smoke-Test | Status |
|-----------|----------|---|---|---|
| `categories_demo.csv` | 4 Categories | GET /api/v1/catalog/categories/ | test_csv_categories_* | ✅ |
| `products_demo.csv` | 8 Products | GET /api/v1/catalog/products/ | test_csv_products_* | ✅ |
| `variants_demo.csv` | 9 Variants | GET /api/v1/catalog/products/<slug>/ | test_csv_product_detail_* | ✅ |
| `prices_demo.csv` | 15 Prices | GET /api/v1/pricing/products/<slug>/prices/ | test_csv_pricing_* | ✅ |
| `shipping_zones_demo.csv` | 2 Zones | (indirekt in methods) | — | ✅ |
| `shipping_methods_demo.csv` | 5 Methods | GET /api/v1/shipping/methods/ | test_csv_shipping_methods_* | ✅ |
| `payment_methods_demo.csv` | 4 Methods | GET /api/v1/payments/methods/ | test_csv_payment_methods_* | ✅ |
| `legal_documents_demo.csv` | 4 Docs | GET /api/v1/legal/active/ | test_csv_legal_active_* | ✅ |
| `legal_versions_demo.csv` | 4 Versions | (indirekt in legal_active) | — | ✅ |
| `consent_categories_demo.csv` | 4 Categories | (nicht über API) | — | ❌ nicht verfügbar |

**Gesamt CSV→API Coverage:** 9 Endpunkte, 32 Smoke-Tests, alle B2C/B2B-Varianten geprüft

### NICHT über API verfügbar (dokumentierte Lücke)

| Entität | Grund | Folgepunkt |
|--|--|--|
| ShippingZone (Metadaten) | Nur ShippingMethod über API | Nicht geplant (Backend-only Infrastruktur) |
| Consent-Kategorien | Kein GDPR-Endpunkt | AB 19+: `GET /api/v1/consent/categories/` (später wenn GDPR-Module erweitert) |

**Update AB 19:** ProductPrice ist jetzt über dedizierter Pricing-API vollständig abrufbar. Die CSV-importierten Preise (prices_demo.csv: 15 Zeilen) sind direkt über `GET /api/v1/pricing/products/<slug>/prices/?customer_group=b2c|b2b` zugänglich.

---

## CSV-Import für Demo-Daten (AB 18 + AB 18.1)

### Überblick

Nach dem Initial-Seeding mit `seed_demo_data` können Demo-Daten auch via CSV-Import aktualisiert/neu erstellt werden. Dies ermöglicht:
- Austauschbare Demo-Datensätze ohne Code-Änderung
- Idempotente Imports (mehrfache Ausführung sicher)
- Change Detection (nur echte Änderungen speichern)
- FK-Validierung und Transaction-Safety

### CSV-Dateien

10 CSV-Dateien unter `backend/data/imports/demo/`:

| Datei | Zeilen | Entity | Features |
|-------|--------|--------|----------|
| categories_demo.csv | 4 | ProductCategory | Slug-based unique key |
| products_demo.csv | 8 | Product | FK: category_slug, Enums: product_type, visibility |
| variants_demo.csv | 9 | ProductVariant | FK: product_slug, Unique by sku or product+name |
| prices_demo.csv | 15 | ProductPrice | Compound key: (product, variant, customer_group), Decimal parsing |
| shipping_zones_demo.csv | 2 | ShippingZone | Code-based key, Comma-separated countries |
| shipping_methods_demo.csv | 10 | ShippingMethod | FK: zone_code, Estimated delivery days |
| payment_methods_demo.csv | 4 | PaymentMethod | Provider integration placeholder |
| legal_documents_demo.csv | 4 | LegalDocument | Document type key, Target group filter |
| legal_versions_demo.csv | 4 | LegalDocumentVersion | Compound key: (document, version), DEMO PLACEHOLDER marker |
| consent_categories_demo.csv | 4 | ConsentCategory | Key-based unique key, Boolean parsing |

**Total:** 64 Demo-Entities

### Import-Befehl

```bash
python manage.py import_demo_csv --settings=config.settings.local
python manage.py import_demo_csv --settings=config.settings.local --source backend/data/imports/demo
```

### Features

- ✅ **Idempotent Upsert:** Mehrfache Ausführung überwrite ohne Duplikate
- ✅ **Change Detection:** Feldvergleich → nur echte Änderungen speichern (Skip wenn identisch)
- ✅ **FK Validation:** Dependencies in korrekter Reihenfolge importieren
- ✅ **Type Coercion:** Decimal, Boolean, Enum parsing
- ✅ **Transaction-Safe:** @transaction.atomic() für All-or-Nothing
- ✅ **Clear Reporting:** created/updated/skipped/errors Statistik
- ❌ **No Delete:** Import-only, keine Lösch-Funktionalität

### Statistik

**Typischer Lauf (mit Change Detection):**
```
[OK] Total: 0 created | 0 updated | 64 skipped
```
- Alle Datensätze bereits vorhanden (von seed_demo_data oder vorherigen Imports)
- Keine Feldunterschiede erkannt
- Alle als "skipped" gezählt (DB-Performance-gewinn durch 0 Saves)

**Idempotency Test:**
```
python manage.py import_demo_csv    # Run 1: 64 skipped
python manage.py import_demo_csv    # Run 2: 64 skipped (identisch)
```

### Implementation Details

- **Command:** `backend/apps/devtools/management/commands/import_demo_csv.py` (750 Zeilen)
- **Helper:** `_upsert_with_change_detection()` für echten Change Detection
- **Tests:** 23 Test Cases in `backend/apps/devtools/tests/test_import_demo_csv.py`
- **Status:** ✅ PRODUCTION READY (AB 18.1)

### Zukünftige Erweiterungen

Dieses Framework kann für weitere Data Sources erweitert werden:

- **Supplier CSV Import:** Lieferanten, Lieferprodukte, Lieferpreise (nach AB 18)
- **PDF/Certificate Upload:** Zertifikate für Lieferanten (nach Supplier Module)
- **Image Import:** Produktbilder, Galerien (nach Image Module)
- **Price Update API:** POST-basierte Preis-Updates für API (nach Pricing API)

Aktuell: Nur Demo-CSV für lokale Entwicklung (keine echten Lieferanten-Daten).

---

**Seed-Daten hinzugefügt:** Arbeitsblock 17
**CSV-Import implementiert:** Arbeitsblock 18 + AB 18.1
**Letzte Aktualisierung:** 2026-05-08
**Status:** PRODUCTION READY (für lokale Entwicklung)
