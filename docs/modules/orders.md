# Orders

## Zweck

`orders` verwaltet Bestellungen und Bestellpositionen als Grundlage fuer echte Shop-Transaktionen.

Das Modul bildet ab:

- Bestellungen
- Bestellpositionen
- Bestellnummern
- User-Bezug
- Kundengruppe B2C/B2B
- Statuslogik (draft, placed, cancelled, completed)
- echte Preis-Snapshots pro Position
- Produkt-/Varianten-Snapshots pro Position
- einfache Adress-Snapshots fuer Rechnungs-/Lieferadresse
- einfache Order-Services
- Konvertierung eines Warenkorbs in eine Bestellung
- Admin-Verwaltung

## Grenzen des Moduls

`orders` haelt Bestellungen, Positionen und Snapshots bereit. Es baut keinen Checkout.

Nicht enthalten:

- Produktstammdaten
- Preisstammdaten
- Warenkorblogik
- Checkout
- Payment
- Versand
- Rechnungen
- E-Mail-Versand
- Legal-/Consent-Integration
- Frontend

## Order

Bestellungsdatensatz mit echten Preis- und Adress-Snapshots.

Wichtige Felder:

- `order_number`, CharField unique max_length=32, Format: AWN-YYYYMMDD-XXXXXX
- `user`, ForeignKey auf `settings.AUTH_USER_MODEL`
- `cart`, optionaler ForeignKey auf `cart.Cart`, nullable, blank=True, on_delete=SET_NULL
- `customer_group`: `b2c` oder `b2b`, Standard `b2c`
- `status`: `draft`, `placed`, `cancelled`, `completed`, Standard `draft`
- `currency`, Standard `EUR`
- `subtotal_amount`, DecimalField, default 0.00
- `total_amount`, DecimalField, default 0.00
- `item_count`, PositiveIntegerField, default 0
- Adress-Snapshot-Felder:
  - `billing_full_name`, `billing_company`, `billing_street`, `billing_postal_code`, `billing_city`, `billing_country` (default DE)
  - `shipping_full_name`, `shipping_company`, `shipping_street`, `shipping_postal_code`, `shipping_city`, `shipping_country` (default DE)
- `placed_at`, optional, wird beim Status `placed` gesetzt
- `cancelled_at`, optional, wird beim Cancel gesetzt
- `created_at`
- `updated_at`

Regeln:

- `order_number` ist eindeutig
- `user` ist Pflicht
- `customer_group` default `b2c`
- `status` default `draft`
- `subtotal_amount`, `total_amount`, `item_count` duerfen nicht negativ sein
- Adress-Snapshots speichern die Bestell-Adressen dauerhaft; spaetere Aenderungen an Customer-Adressen aendern bestehende Orders nicht
- `__str__` zeigt Order-Nummer und Status

## OrderItem

Bestellposition mit vollstaendigen Preis- und Produkt-Snapshots.

Wichtige Felder:

- `order`, ForeignKey auf Order
- `product`, optional ForeignKey auf `catalog.Product`, null=True, blank=True, on_delete=SET_NULL
- `variant`, optional ForeignKey auf `catalog.ProductVariant`, null=True, blank=True, on_delete=SET_NULL
- `price`, optional ForeignKey auf `pricing.ProductPrice`, null=True, blank=True, on_delete=SET_NULL
- Snapshot-Felder (Pflicht, veraendernde sich nicht):
  - `product_id_snapshot`, PositiveIntegerField
  - `variant_id_snapshot`, optional PositiveIntegerField
  - `price_id_snapshot`, optional PositiveIntegerField
  - `product_name`, CharField
  - `variant_name`, optional CharField
  - `sku`, optional CharField
- `customer_group`: `b2c` oder `b2b`
- `quantity`, PositiveIntegerField, muss > 0 sein
- `unit_amount`, DecimalField
- `line_total`, DecimalField (= quantity * unit_amount)
- `currency`, default EUR
- `tax_rate`, DecimalField, default 0.00
- `price_includes_tax`, BooleanField, default True
- `created_at`
- `updated_at`

Regeln:

- `quantity` muss groesser 0 sein
- `unit_amount`, `line_total` duerfen nicht negativ sein
- `line_total` = quantity * unit_amount
- Snapshot-Felder sind Pflicht und veraendernde sich nicht, wenn spaeter das Produkt, die Variante oder der Preis aktualisiert werden
- Spaetere Produkt-/Preisaenderungen veraendernde alte OrderItems nicht
- `__str__` zeigt Order-Nummer, Produktname, Variante

## Bestellnummer

`generate_order_number()` erzeugt eindeutige Bestellnummern:

- Format: `AWN-YYYYMMDD-XXXXXX` (Alice Wonder Nails - Datum - Zufallssuffix)
- Lokal stabil, keine externe Nummerierung noetig
- 20 Retries zur Vermeidung von Kollisionen
- Wirft `OrderError` bei 20 Fehlversuchen

## Statuslogik

Order-Status:

- `draft`: neue Bestellung, noch nicht platziert
- `placed`: Bestellung abgesendet (mit `placed_at`-Zeitstempel)
- `cancelled`: Bestellung storniert (mit `cancelled_at`-Zeitstempel)
- `completed`: Bestellung abgeschlossen (zukuenftig bei Shipping/Payment)

Transitions:

- draft -> placed (manuell ueber Service oder Checkout-Logik)
- placed -> cancelled (manuell ueber `cancel_order()`)
- placed -> completed (Spaetere Payment-/Shipping-Integration)

## Echte Preis-Snapshots

OrderItem speichert echte Snapshots:

- `product_id_snapshot`, `variant_id_snapshot`, `price_id_snapshot`: IDs zum Audit-Trail
- `product_name`, `variant_name`, `sku`: beschreibende Daten
- `quantity`, `unit_amount`, `line_total`: kalkulierte Werte
- `currency`, `tax_rate`, `price_includes_tax`: Preis-Metadaten

Der Sinn: spaetere Produkt-/Preis-/Variantenänderungen veraendernde bestehende Bestellungen nicht. Der Snapshot ist die authoritative Quelle.

## Produkt-/Varianten-Snapshots

Snapshots speichern Auswahl-Context:

- Welches Produkt wurde bestellt?
- Welche Variante (Farbe, Groesse) wurde gewaehlt?
- Welcher SKU war aktiv?

Die Foreign Keys (`product`, `variant`, `price`) sind optional und dienen nur zur Referenzierung. Die Snapshots sind die quelle.

## Adress-Snapshots

Bestell-Adressen werden als Snapshots gespeichert:

- `billing_*` speichert Rechnungsadresse
- `shipping_*` speichert Lieferadresse
- Nachtraegliche Aenderungen an `customers.Address` veraendernde Bestellungen nicht
- Format: flache Text-Felder fuer einfache Lesbarkeit und SQL-Queries

## Order-Services

Datei: `backend/apps/orders/services.py`

Bereitgestellt:

- `OrderError` Exception fuer Service-Fehler
- `generate_order_number()`: erzeugt eindeutige Nummern
- `build_address_snapshot(address)`: erzeugt Dict mit Adressdaten; bei None werden Defaults zurueckgegeben
- `create_order_from_cart(cart, user=None, billing_address=None, shipping_address=None, status='placed')`: erstellt Order aus Cart mit Transaktionen, Snapshots, Cart-Status-Update
- `recalculate_order_totals(order)`: berechnet Summen aus OrderItems neu
- `cancel_order(order)`: setzt Status auf `cancelled` und `cancelled_at`

## create_order_from_cart

Konvertiert einen Warenkorb in eine Bestellung:

- Validiert: Cart vorhanden, User vorhanden, CartItems vorhanden
- Nutzt `pricing.services.calculate_cart()` fuer aktuelle Preise
- Erstellt Order mit Snapshots fuer Adressen, Kundengruppe, Status
- Erstellt OrderItems mit vollstaendigen Snapshots
- Setzt `cart.status` auf `converted`
- Atomic Transaction
- Keine Payment-, Versand- oder E-Mail-Logik

## Admin-Funktionen

Registriert im Django Admin:

- `Order`
- `OrderItem`

Admin-Konfiguration:

Order:
- list_display: order_number, user, customer_group, status, total_amount, currency, item_count, created_at
- list_filter: customer_group, status, currency, created_at
- search_fields: order_number, user__email, user__username, billing_full_name, shipping_full_name
- readonly_fields: order_number, subtotal_amount, total_amount, item_count, placed_at, cancelled_at, created_at, updated_at
- raw_id_fields: user, cart
- inlines: OrderItemInline

OrderItem:
- list_display: order, product_name, variant_name, quantity, unit_amount, line_total, currency
- search_fields: order__order_number, product_name, variant_name, sku
- raw_id_fields: order, product, variant, price

OrderItemInline (Tabular):
- readonly_fields: alle Snapshot- und Berechnungsfelder
- raw_id_fields: product, variant, price

## Tests

Getestet:

- Order kann erstellt werden
- `order_number` ist eindeutig
- default status ist `draft`
- default customer_group ist `b2c`
- subtotal_amount/total_amount duerfen nicht negativ sein
- `__str__` ist sinnvoll
- OrderItem kann erstellt werden
- `quantity` > 0
- `unit_amount` darf nicht negativ sein
- `line_total` darf nicht negativ sein
- Snapshot-Felder werden gespeichert
- Produkt-/Variantenname bleibt als Snapshot erhalten
- `generate_order_number` erzeugt eindeutige Nummern
- `build_address_snapshot` funktioniert mit Address und None
- `create_order_from_cart` erzeugt Order aus Cart
- `create_order_from_cart` erzeugt OrderItems mit Snapshots
- `create_order_from_cart` setzt cart.status auf `converted`
- `create_order_from_cart` setzt subtotal/total/item_count korrekt
- `create_order_from_cart` nutzt B2C-Preise
- `create_order_from_cart` nutzt B2B-Preise
- `create_order_from_cart` nutzt Variantenpreise
- `create_order_from_cart` schlaegt fehl bei leerem Cart
- `create_order_from_cart` schlaegt fehl ohne User
- Spaetere Preisaenderung veraendert bestehendes OrderItem nicht
- `recalculate_order_totals` berechnet korrekt
- `cancel_order` setzt status/cancelled_at und veraendert Snapshots nicht

Backend-Pytest: 26 Orders-Tests, davon alle gruen.

## Abhaengigkeiten

- `settings.AUTH_USER_MODEL` (`accounts.User`)
- `catalog.Product`
- `catalog.ProductVariant`
- `pricing.ProductPrice`
- `cart.Cart`
- `customers.Address` (optional)
- PostgreSQL
- Django Admin

## Verbotene Zustaendigkeiten

orders baut NICHT:

- Produktstammdaten
- Preisstammdaten
- Warenkorblogik
- Checkout
- Payment
- Versand
- Rechnungen
- E-Mail
- Legal-/Consent-Modul
- Frontend

Ordering bezieht sich **ausschliesslich** auf das Speichern von Bestellungen mit Snapshots. Alle anderen Funktionen sind Sache spaeteren Module.

## Arbeitsblock 12: Checkout-Finalisierung im Order-Modul

Kontrollierte Erweiterung des frozen orders-Moduls:

### Neue Felder im Order-Modell

- `shipping_amount`, DecimalField(10,2), default 0.00, >= 0 (finale Versandkosten aus Checkout)
- `shipping_snapshot`, JSONField (Versandmethoden-Metadaten: method_code, method_name, zone_code, zone_name, amount, currency)
- `payment_snapshot`, JSONField (Zahlungsmethoden-Metadaten: method_code, method_name, provider, customer_group)
- `checkout_snapshot`, JSONField (Checkout-Kontext: checkout_id, customer_group, currency, item_count, cart_subtotal, shipping_amount, order_total)

Alle neue Felder haben default dict/0.00 und beeinflussen nicht bestehendes Orders.

### Geaenderte Order-Logik

`recalculate_order_totals(order)` berechnet jetzt:

- `subtotal_amount` aus OrderItems
- `total_amount = subtotal_amount + shipping_amount` (war vorher nur subtotal_amount)
- `item_count` aus Items

### Neue Funktion: apply_checkout_snapshot_to_order

`apply_checkout_snapshot_to_order(order, checkout)` transferiert finale Checkout-Daten in Order:

- Setzt `order.shipping_amount` aus `checkout.shipping_amount`
- Setzt `order.shipping_snapshot` aus `checkout.shipping_snapshot`
- Setzt `order.payment_snapshot` aus `checkout.payment_snapshot`
- Erstellt `order.checkout_snapshot` mit Checkout-Kontext
- Berechnet `order.total_amount = order.subtotal_amount + order.shipping_amount`
- Speichert Order

Zweck: Nach Order-Erzeugung speichert Order die finalen kaufrelevanten Daten (Versand/Payment) dauerhaft ab. Spaetere Aenderungen an Shipping-/Payment-Methoden veraendernde bestehendes Orders nicht.

### Keine echte Ausführung

- Keine echte Payment-Ausführung (nur Metadaten-Snapshot)
- Keine echte Versand-Buchung (nur Metadaten-Snapshot)
- Keine Rechnungs-Generierung
- Keine E-Mail-Versand

### Tests fuer AB 12

- Order.shipping_amount default 0.00
- shipping_amount CheckConstraint (non-negative)
- Order.shipping_snapshot default empty dict
- Order.payment_snapshot default empty dict
- Order.checkout_snapshot default empty dict
- recalculate_order_totals mit shipping_amount
- apply_checkout_snapshot_to_order transferiert alle Snapshots
- Order.total_amount includes shipping_amount
- Neue Tests: 7 Orders-Tests, alle gruen
- Gesamtstatus: 262/262 Backend-Tests bestanden (251 existing + 11 new checkout tests)

## Freeze-Status

- Status: tested
- Tests: gruen (26 Orders-Tests)
- Freeze-Status: frozen
- Notiz: Stabiler Erststand, Aenderungen nur noch dokumentiert

## Aenderungsregel

Aenderungen nur mit dokumentiertem Grund, Impact-Pruefung und Regressionstest.

## Offene Punkte

- Checkout-Integration (Arbeitsblock 07)
- Payment-Integration (Arbeitsblock payment)
- Versand-Integration (Arbeitsblock shipping)
- Rechnungs-Generierung (Arbeitsblock billing)
- E-Mail-Versand (Arbeitsblock notifications)
- Legal-/Consent-Integration (Arbeitsblock legal/consent)
