# API Contracts

## Ziel

Dokumentation der API-Schnittstellen für das Backend.

## Erste API (v1, read-only, frozen in AB 14.1)

### Health Endpoint
- `GET /api/v1/health/`
  - Response: `{ "success": true, "data": { "status": "ok", "service": "alice-wonder-nails-api", "version": "v1", "environment": "local-dev" } }`

### Catalog Endpoints
- `GET /api/v1/catalog/categories/`
- `GET /api/v1/catalog/products/?customer_group=b2c|b2b`
- `GET /api/v1/catalog/products/<slug>/?customer_group=b2c|b2b`

### Shipping Endpoint
- `GET /api/v1/shipping/methods/?customer_group=b2c|b2b&country=DE`

### Payments Endpoint
- `GET /api/v1/payments/methods/?customer_group=b2c|b2b`

### Legal Endpoint
- `GET /api/v1/legal/active/?customer_group=b2c|b2b`

## API v1.1 Extension – Pricing (AB 19, additive read-only)

### Pricing Endpoints (NEW)
- `GET /api/v1/pricing/products/<slug>/prices/?customer_group=b2c|b2b`
  - **Purpose:** Fetch active prices for a product by slug
  - **Query Parameters:**
    - `customer_group` (optional, default: 'b2c'): Filter prices by customer group ('b2c' or 'b2b')
  - **Success Response (200):**
    ```json
    {
      "success": true,
      "data": {
        "product": {
          "slug": "gel-color-rose-gold",
          "name": "Gel Color Rose Gold"
        },
        "customer_group": "b2c",
        "currency": "EUR",
        "prices": [
          {
            "type": "product",
            "variant_sku": null,
            "variant_name": null,
            "amount": "12.99",
            "currency": "EUR",
            "tax_rate": "19.00",
            "price_includes_tax": true
          },
          {
            "type": "variant",
            "variant_sku": "GEL-RG-5ML",
            "variant_name": "5ml",
            "amount": "14.99",
            "currency": "EUR",
            "tax_rate": "19.00",
            "price_includes_tax": true
          }
        ]
      }
    }
    ```
  - **Error Responses:**
    - 400 Bad Request (invalid customer_group):
      ```json
      {
        "success": false,
        "error": {
          "code": "invalid_customer_group",
          "message": "customer_group must be \"b2c\" or \"b2b\", got \"...\""
        }
      }
      ```
    - 404 Not Found (product not found or not visible):
      ```json
      {
        "success": false,
        "error": {
          "code": "product_not_found",
          "message": "Product with slug \"...\" not found"
        }
      }
      ```
      or
      ```json
      {
        "success": false,
        "error": {
          "code": "product_not_visible",
          "message": "Product not visible for customer group: b2c"
        }
      }
      ```

### Pricing v1.1 Features
- **Read-Only:** No POST/PUT/DELETE allowed, GET only
- **Filtering:** Only active prices (is_active=True)
- **Time Windows:** Respects valid_from/valid_until constraints
- **Customer Groups:** Separates B2C and B2B prices
- **Visibility Control:** Respects product visibility settings (public, b2c_only, b2b_only)
- **Price Types:** Both product-level and variant-level prices included
- **Tax Information:** Returns tax_rate and price_includes_tax flags

### Backward Compatibility
- ✅ No changes to existing v1 endpoints
- ✅ No changes to existing response formats
- ✅ No changes to existing query parameters
- ✅ Additive extension only (new URL pattern)
- ✅ All existing v1 tests remain unchanged

## Test-Abdeckung (AB 18 + AB 19)

Die API wird durch folgende Testsuiten validiert:

### API-Vertrags-Tests
- Datei: `backend/apps/api/tests/test_api.py` (33 tests)
- Zweck: Validieren der API-Verträge mit minimalen/mocked Daten
- Scope: API-Endpunkte, Response-Format, Fehlerbehandlung
- Status: Frozen (AB 14.1)

### API-Integrations-Smoke-Tests (AB 18)
- Datei: `backend/apps/devtools/tests/test_seeded_api_smoke.py` (~18 tests)
- Zweck: Validieren, dass seeded Demo-Daten über die API korrekt abrufbar sind
- Scope: Kategorien, Produkte, Versand, Zahlungen, Rechtliches
- Test-Struktur:
  - Seed-Daten einmal pro Testklasse laden
  - Endpunkte-Hits durchführen
  - Response-Format + Dateninhalt validieren
  - B2C/B2B-Filterung validieren
  - Fehler-Handling validieren
- Status: Neu in AB 18

**Summe:** 33 + 18 = 51 API-Tests, alle read-only Operationen

### Pricing-Endpunkt-Tests (AB 19 + AB 19.1)
- Datei: `backend/apps/api/tests/test_pricing_endpoints.py` (18 tests)
- Zweck: Validieren des neuen Pricing v1.1 Endpunkts
- Scope: ProductPrice-Abruf, customer_group Filterung, Visibility-Checks, Fehlerbehandlung, Edge Cases
- Test-Struktur:
  - Endpoint-Existenz und Status-Codes
  - Default customer_group Handling
  - B2C/B2B Preis-Separation
  - Variant- vs Product-Level Preise
  - Inaktive Preise filtern
  - Produkt-Visibility respektieren
  - Tax-Rate und price_includes_tax Ausgabe
  - Response-Format Stabilität
  - Error-Handling
  - **Neu in AB 19.1:**
    - Produkt ohne aktive Preise (sollte 200 OK mit leerer prices[]-Array sein)
    - GET-only Validierung (POST sollte 405 Method Not Allowed sein)
- Status: Implementiert in AB 19, Edge-Cases in AB 19.1 validiert

**Summe:** 51 + 18 = 69 API-Tests, alle read-only Operationen

## CSV/API Smoke Tests (AB 20)

- Datei: `backend/apps/devtools/tests/test_csv_api_smoke.py` (32 tests)
- Zweck: Validierung der CSV-Import → Database → API-Kette
- Scope: Alle 9 v1/v1.1 Endpunkte mit CSV-importierten Demo-Daten
- Teststruktur:
  - Health, Categories, Products, Product-Detail, Pricing, Shipping, Payments, Legal
  - B2C/B2B Filterung validiert
  - Visibility-Checks (public, b2c_only, b2b_only)
  - Error-Handling (404, 400)
- Status: Neu in AB 20 (CSV-Integration-Tests)

**Summe:** 69 + 32 = 101 API-Tests (33 Contract + 18 Pricing + 32 Smoke)

## Spätere APIs

- Authentifizierung und User
- Produktkatalog (erweitert mit Preis-Endpunkt, siehe DATA_COLLECTION.md)
- Warenkorb
- Bestellungen
- Zahlungen
- Versand
- Consent/Datenschutz
