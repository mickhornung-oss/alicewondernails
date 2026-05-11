# Pricing

## Zweck

`pricing` verwaltet die Preisgrundlage fuer den spaeteren Shop.

Das Modul bildet ab:

- B2C-Preise
- B2B-Preise
- Produktpreise
- Variantenpreise
- Waehrung
- Steuer-/Brutto-/Netto-Vorbereitung
- Gueltigkeitszeitraeume
- Aktiv-/Inaktiv-Status
- einfachen Preisservice
- Snapshot-Vorbereitung fuer spaetere Bestellungen

## Grenzen des Moduls

Pricing berechnet und findet Preise, baut aber keinen Kaufprozess.

Nicht enthalten:

- Produktstammdaten
- Warenkorb
- Checkout
- Bestellungen
- Payment
- Versand
- Frontend
- echte Steuerberatung

## ProductPrice

Preisdatensatz fuer ein Produkt oder optional eine Produktvariante.

Wichtige Felder:

- `product`, ForeignKey auf `catalog.Product`
- `variant`, optionaler ForeignKey auf `catalog.ProductVariant`
- `customer_group`
- `amount`
- `currency`
- `tax_rate`
- `price_includes_tax`
- `valid_from`, optional
- `valid_until`, optional
- `is_active`
- `created_at`
- `updated_at`

Regeln:

- `amount` darf nicht negativ sein.
- `tax_rate` darf nicht negativ sein.
- `valid_until` darf nicht vor `valid_from` liegen.
- Wenn `variant` gesetzt ist, muss sie zum angegebenen `product` gehoeren.
- Preise werden nicht in `catalog.Product` oder `catalog.ProductVariant` gespeichert.

## Customer Groups

`customer_group` unterscheidet:

- `b2c`
- `b2b`

Die Rollen-/User-Pruefung wird hier noch nicht gebaut. Spaetere Views, Cart oder Orders nutzen diese Preislogik mit passendem Kontext.

## Steuer-/Brutto-/Netto-Vorbereitung

`tax_rate` und `price_includes_tax` bereiten spaetere Netto-/Brutto-Logik vor.

Dieser Modulstand liefert keine Steuerberatung und keine finale rechtliche Preisangabenlogik.

## Gueltigkeitslogik

Ein Preis ist fuer den Service gueltig, wenn:

- `is_active=True`
- `customer_group` passt
- `product` passt
- `variant` passt oder ein Produktpreis als Fallback genutzt wird
- `valid_from` leer oder kleiner/gleich dem Pruefzeitpunkt ist
- `valid_until` leer oder groesser/gleich dem Pruefzeitpunkt ist

Bei mehreren passenden Preisen wird der neuere gueltige Preis bevorzugt.

## Preisservice

Datei: `backend\apps\pricing\services.py`

Bereitgestellt:

- `PriceNotFound`
- `get_active_price(product, customer_group, variant=None, at=None)`
- `build_price_snapshot(price)`

`get_active_price` bevorzugt Variantenpreise. Wenn kein Variantenpreis vorhanden ist, faellt der Service auf einen produktweiten Preis zurueck.

## Snapshot-Vorbereitung

`build_price_snapshot` erzeugt ein Dict fuer spaetere OrderItem-Snapshots.

Snapshot-Felder:

- `product_id`
- `variant_id`
- `product_name`
- `variant_name`
- `customer_group`
- `amount`
- `currency`
- `tax_rate`
- `price_includes_tax`
- `price_id`

Noch keine OrderItem-Integration.

## Admin-Funktionen

Registriert im Django Admin:

- `ProductPrice`

Admin-Funktionen:

- Listenanzeige fuer Produkt, Variante, Kundengruppe, Betrag, Waehrung, Steuersatz, Steuerstatus, Gueltigkeit und Aktivstatus
- Suche ueber Produktname, Variantenname und SKU
- Filter fuer Kundengruppe, Waehrung, Aktivstatus und Steuerstatus
- `raw_id_fields` fuer Produkt und Variante

## Tests

Getestet:

- B2C-Preis kann erstellt werden
- B2B-Preis kann erstellt werden
- Produktpreis kann erstellt werden
- Variantenpreis kann erstellt werden
- Negative Betraege sind ungueltig
- Negative Steuersaetze sind ungueltig
- `valid_until` vor `valid_from` ist ungueltig
- Variante muss zum Produkt gehoeren
- `__str__` ist sinnvoll
- B2C-/B2B-Produktpreise werden gefunden
- Variantenpreis wird bevorzugt
- Fallback auf Produktpreis funktioniert
- Inaktive Preise werden ignoriert
- Preise ausserhalb des Gueltigkeitszeitraums werden ignoriert
- `PriceNotFound` wird ausgelost, wenn kein Preis existiert
- Preis-Snapshot enthaelt die erwarteten Felder
- Produktname und Variantenname sind im Snapshot enthalten

Backend-Pytest: gruen.

## Abhaengigkeiten

- Django ORM
- PostgreSQL
- Django Admin
- `catalog.Product`
- `catalog.ProductVariant`

## Verbotene Zustaendigkeiten

Pricing baut NICHT:

- Produktstammdaten
- Warenkorb
- Checkout
- Bestellungen
- Payment
- Versand
- Frontend
- echte Steuerberatung

## Offene Punkte

- Aktionspreise, Staffelpreise und komplexere B2B-Konditionen folgen spaeter.
- Warenkorb nutzt spaeter den Preisservice.
- Bestellungen speichern spaeter Snapshots.

## Freeze-Status

- Status: frozen
- Freeze-Status: frozen
- Notiz: stabiler Erststand, Aenderungen nur noch dokumentiert.

## Aenderungsregel

Aenderungen nur mit dokumentiertem Grund, Impact-Pruefung und Regressionstest. Schnittstellenanpassungen fuer spaetere Module wie `cart` oder `orders` sind erlaubt, wenn sie dokumentiert und getestet werden.
