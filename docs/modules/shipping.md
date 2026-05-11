# Shipping – Versand- und Logistik-Grundstruktur

## Zweck

Dieses Modul bietet die Grundstruktur für Versand- und Logistik-Verwaltung:

- **Versandzonen** (ShippingZone): Geografische Kategorisierung (z.B. Deutschland, EU, International)
- **Versandmethoden** (ShippingMethod): Konkrete Versandarten pro Zone und Kundengruppe
- **Rate-Snapshots** (ShippingRateSnapshot): Stabile Momentaufnahmen der Versandkosten zur Berechnung

## Datenbankmodelle

### ShippingZone

**Ziel**: Definiert geografische Versandzonen mit Länderlisten.

| Feld | Typ | Beschreibung |
|---|---|---|
| `name` | CharField(120) | Name der Zone (z.B. "Deutschland", "EU") |
| `code` | CharField(32, unique) | Eindeutiger Code (z.B. "DE", "EU") |
| `countries` | ArrayField | ISO-Ländercodes (z.B. ["DE", "AT", "CH"]) |
| `is_active` | BooleanField | Zone aktiv für Versandberechnung |
| `sort_order` | PositiveIntegerField | Sortierreihenfolge |
| `created_at` | DateTimeField | Erstellungszeitstempel |
| `updated_at` | DateTimeField | Änderungszeitstempel |

**Meta**: Ordering: `[sort_order, name]` | Indizes: `[code]`, `[is_active]` | Constraint: `code` eindeutig

### ShippingMethod

**Ziel**: Definiert konkrete Versandmethoden pro Zone und Kundengruppe.

| Feld | Typ | Beschreibung |
|---|---|---|
| `zone` | ForeignKey(ShippingZone) | Zugehörige Versandzone (PROTECT) |
| `name` | CharField(120) | Name (z.B. "Standardversand") |
| `code` | CharField(64, unique) | Eindeutiger Code (z.B. "standard_de") |
| `customer_group` | CharField(10) | Kundengruppe: "all", "b2c", "b2b" |
| `base_price` | DecimalField(10,2) | Basis-Versandkosten |
| `currency` | CharField(3) | Währung (Standard: "EUR") |
| `estimated_min_days` | PositiveIntegerField | Min. Liefertage (optional) |
| `estimated_max_days` | PositiveIntegerField | Max. Liefertage (optional) |
| `is_active` | BooleanField | Methode aktiv |
| `sort_order` | PositiveIntegerField | Sortierreihenfolge |
| `created_at` | DateTimeField | Erstellungszeitstempel |
| `updated_at` | DateTimeField | Änderungszeitstempel |

**Meta**: Ordering: `[sort_order, name]` | Indizes: `[zone, is_active]`, `[code]`, `[customer_group]` | Constraints: base_price>=0, max_days>=min_days | FK: Zone with PROTECT

### ShippingRateSnapshot

**Ziel**: Stabile Momentaufnahme eines Versand-Rates (nicht vom Original abhängig).

| Feld | Typ | Beschreibung |
|---|---|---|
| `method` | ForeignKey(ShippingMethod) | Referenz (optional, SET_NULL) |
| `method_code` | CharField(64) | Code (Snapshot, unveränderlich) |
| `method_name` | CharField(120) | Name (Snapshot, unveränderlich) |
| `zone_code` | CharField(32) | Zone-Code (Snapshot, unveränderlich) |
| `zone_name` | CharField(120) | Zone-Name (Snapshot, unveränderlich) |
| `customer_group` | CharField(10) | "b2c" oder "b2b" |
| `amount` | DecimalField(10,2) | Versandkosten-Betrag |
| `currency` | CharField(3) | Währung (Standard: "EUR") |
| `estimated_min_days` | PositiveIntegerField | Min. Liefertage (optional) |
| `estimated_max_days` | PositiveIntegerField | Max. Liefertage (optional) |
| `created_at` | DateTimeField | Erstellungszeitstempel |

**Meta**: Ordering: `[-created_at]` | Indizes: `[method_code]`, `[customer_group]`, `[-created_at]` | Constraints: amount>=0 | Admin: read-only (add/change/delete=False)

## Services

### `get_available_shipping_methods(country_code="DE", customer_group="b2c")`
Findet verfügbare Methoden für Land und Kundengruppe. Filtert aktive Zonen/Methoden, sortiert nach sort_order.

### `get_shipping_method(code, customer_group="b2c", country_code="DE")`
Findet spezifische Methode, validiert Kundengruppe und Zone/Land. Wirft `ShippingError` bei Validierungsfehler.

### `calculate_shipping_amount(method)`
Gibt method.base_price zurück (einfache Logik, keine Gewichts-/Warenwertlogik).

### `build_shipping_snapshot(method, customer_group="b2c")`
Erstellt stabilen Snapshot mit denormalisierten method/zone-Daten.

## Freeze-Status

- Status: **frozen** (nicht locked)
- Block: Arbeitsblock 09
- Review/Freeze-Decision: Arbeitsblock 09.1 ✅
- Änderungsregel: Änderungen nur mit dokumentiertem Grund, Impact-Prüfung und Regressionstest
- Letzte Review: 2026-05-04, alle 42 Tests grün, Infrastruktur stabil

## Grenzen

❌ Nicht im Scope: DHL/Hermes/Warenpost-Anbindung, Label-Erstellung, Tracking-API, Checkout/Order-Integration, Payment-Logik

## Status

- Status: **frozen**
- Tests: gruen (42 Tests)
- Migrationen: 1 (0001_initial.py)
- Freeze-Status: frozen
