# Catalog

## Zweck

`catalog` verwaltet die Produktkatalog-Grundlage fuer den spaeteren Shop.

Das Modul bildet ab:

- Produktkategorien
- Produkte
- Produktvarianten
- Produktbilder
- Farben und Farbwerte
- Serien/Kollektionen
- B2C-/B2B-Sichtbarkeit
- Aktiv-/Inaktiv-Status

## Grenzen des Moduls

Catalog beschreibt Produkte und Varianten, berechnet aber nichts.

Nicht enthalten:

- Preise
- Warenkorb
- Checkout
- Bestellungen
- Payment
- Versand
- Galerie
- Reviews
- Frontend

## Modelle

### ProductCategory

Wichtige Felder:

- `name`
- `slug`, eindeutig
- `description`, optional
- `parent`, optionale Selbstreferenz
- `sort_order`
- `is_active`
- `created_at`
- `updated_at`

Kategorien koennen verschachtelt werden. Die Sortierung laeuft nach `sort_order`, dann `name`.

### Product

Wichtige Felder:

- `category`
- `name`
- `slug`, eindeutig
- `short_description`, optional
- `description`, optional
- `collection_name`, optional
- `product_type`
- `visibility`
- `is_active`
- `is_featured`
- `created_at`
- `updated_at`

Produkttypen:

- `nail_polish`
- `gel`
- `care`
- `accessory`
- `set`
- `other`

Sichtbarkeit:

- `public`
- `b2c_only`
- `b2b_only`
- `hidden`

### ProductVariant

Wichtige Felder:

- `product`
- `name`
- `sku`, optional, eindeutig falls gesetzt
- `color_name`, optional
- `color_code`, optional
- `finish`, optional
- `size_label`, optional
- `is_default`
- `is_active`
- `sort_order`
- `created_at`
- `updated_at`

Farbe und Farbcode sind fuer Nagelprodukte bewusst direkt an Varianten vorbereitet.

### ProductImage

Wichtige Felder:

- `product`
- `variant`, optional
- `image`
- `alt_text`, optional
- `sort_order`
- `is_primary`
- `created_at`
- `updated_at`

Das Feld `image` ist als `FileField` umgesetzt, damit keine Pillow-Abhaengigkeit fuer diesen Erststand noetig ist. Komplexe Thumbnail- oder Uploadvalidierung folgt spaeter.

## Sichtbarkeitslogik

`Product` stellt einfache Properties bereit:

- `is_visible_for_b2c`
- `is_visible_for_b2b`

Logik:

- `public`: sichtbar fuer B2C und B2B
- `b2c_only`: sichtbar fuer B2C
- `b2b_only`: sichtbar fuer B2B
- `hidden`: nicht sichtbar im oeffentlichen Shop

Noch keine komplexe Rollenabfrage ueber User.

## Admin-Funktionen

Registriert im Django Admin:

- `ProductCategory`
- `Product`
- `ProductVariant`
- `ProductImage`

Admin-Funktionen:

- Suche ueber Namen, Slugs, SKU, Farbname und Bild-Alt-Text
- Filter fuer Aktivstatus, Typ, Sichtbarkeit, Featured, Default und Primaerbild
- Slug-Vorbefuellung fuer Kategorien und Produkte
- einfache Inlines fuer Varianten und Bilder am Produkt

## Tests

Getestet:

- Kategorie kann erstellt werden
- Kategorie-Slug ist eindeutig
- Parent-Kategorie funktioniert
- Produkt kann erstellt werden
- Produkttyp-Choices funktionieren
- Sichtbarkeits-Choices funktionieren
- B2C-/B2B-Sichtbarkeitslogik funktioniert
- Product enthaelt keine Preisfelder
- Variante kann erstellt werden
- SKU, Farbe, Farbcode und Default-Status funktionieren
- Produktbild kann erstellt werden
- Produktbild kann optional Variante referenzieren
- `__str__` Methoden sind sinnvoll

Backend-Pytest: gruen.

## Abhaengigkeiten

- Django ORM
- PostgreSQL
- Django Admin
- Noch keine Abhaengigkeit auf pricing, cart, orders, payment oder shipping

## Verbotene Zustaendigkeiten

Catalog baut NICHT:

- Preise
- Warenkorb
- Checkout
- Bestellungen
- Payment
- Versand
- Galerie
- Reviews
- Frontend

## Offene Punkte

- Medienstrategie, Uploadvalidierung und Thumbnails folgen spaeter.
- Produkt-API folgt spaeter.
- Preislogik folgt im Modul `pricing`.
- Warenkorb folgt spaeter im Modul `cart`.
- Bestellungen folgen spaeter im Modul `orders`.

## Freeze-Status

- Status: frozen
- Freeze-Status: frozen
- Locked: nein
- Notiz: stabiler Erststand, Aenderungen nur noch dokumentiert.

## Aenderungsregel

Aenderungen nur mit dokumentiertem Grund, Impact-Pruefung und Regressionstest.
