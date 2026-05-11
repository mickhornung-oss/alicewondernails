# Cart

## Zweck

`cart` verwaltet Warenkoerbe und Warenkorbpositionen als Grundlage fuer spaetere Checkout- und Order-Logik.

Das Modul bildet ab:

- Warenkorb pro eingeloggtem User
- Warenkorb pro anonymer Session ueber `session_key`
- Kundengruppe `b2c` und `b2b`
- Warenkorbpositionen mit Mengenlogik
- Produkt-/Variantenpruefung
- aktuelle Preisberechnung ueber den `pricing`-Service
- Status `active`, `converted`, `abandoned`

## Grenzen des Moduls

`cart` haelt Warenkoerbe und Positionen bereit und berechnet Summen. Es baut keinen Kaufprozess.

Nicht enthalten:

- Produktstammdaten
- Preisstammdaten
- Bestellungen
- Checkout
- Payment
- Versand
- Rabatte
- Gutscheine
- Frontend
- E-Mail-Versand

## Cart

Datei: `backend\apps\cart\models.py`

Wichtige Felder:

- `user`, optionaler ForeignKey auf `settings.AUTH_USER_MODEL`
- `session_key`, optionales `CharField(max_length=80)`
- `customer_group`: `b2c` oder `b2b`, Standard `b2c`
- `status`: `active`, `converted`, `abandoned`, Standard `active`
- `currency`, Standard `EUR`
- `created_at`
- `updated_at`

Regeln:

- `user` ODER `session_key` muss vorhanden sein (DB-Constraint und `clean()`).
- Pro `user` darf hoechstens ein Warenkorb mit `status=active` existieren.
- Pro `session_key` (sofern gesetzt) darf hoechstens ein Warenkorb mit `status=active` existieren.
- `ordering = ('-updated_at',)`.

## CartItem

Wichtige Felder:

- `cart`, ForeignKey auf `Cart`
- `product`, ForeignKey auf `catalog.Product`
- `variant`, optionaler ForeignKey auf `catalog.ProductVariant`
- `quantity`, `PositiveIntegerField`, Standard `1`
- `created_at`
- `updated_at`

Regeln:

- `quantity` muss groesser 0 sein (DB-Constraint und `clean()`).
- Wenn `variant` gesetzt ist, muss sie zum angegebenen `product` gehoeren.
- Kombination `cart`/`product`/`variant` ist eindeutig (UniqueConstraint).
- Keine Preisfelder dauerhaft im `CartItem` gespeichert.
- Keine Order-Snapshots im `CartItem`.

## Warenkorb-Services

Datei: `backend\apps\cart\services.py`

Bereitgestellt:

- `CartError`
- `get_or_create_cart(user=None, session_key=None, customer_group='b2c')`
- `add_item(cart, product, variant=None, quantity=1)`
- `update_item_quantity(item, quantity)`
- `remove_item(item)`
- `clear_cart(cart)`
- `calculate_cart(cart)`

Verhalten:

- `get_or_create_cart` benoetigt `user` oder `session_key`, sucht aktiven Warenkorb und erstellt einen neuen, falls keiner vorhanden ist.
- `add_item` validiert Variante und Menge; bestehende Positionen werden um die Menge erhoeht, sonst wird eine neue Position erstellt.
- `update_item_quantity` erlaubt nur Mengen groesser 0; `0` und negative Werte loesen `CartError` aus. In diesem Block wird bei `0` nicht automatisch geloescht.
- `remove_item` loescht eine Position.
- `clear_cart` loescht alle Positionen des Warenkorbs.

## Preisberechnung ueber pricing

`calculate_cart` nutzt:

- `pricing.services.get_active_price`
- `pricing.services.build_price_snapshot`

Berechnet wird:

- `lines` mit `item_id`, `product_id`, `variant_id`, `quantity`, `unit_amount`, `line_total`, `price_snapshot`
- `subtotal` (Summe der Positionen)
- `currency` (folgt dem Snapshot)
- `customer_group` aus dem Warenkorb
- `item_count` (Summe der Mengen)

Wenn fuer eine Position kein aktiver Preis gefunden wird, wird `CartError` ausgeloest. Es werden keine Fake-Preise erzeugt.

Snapshots werden hier nur als Berechnungsausgabe geliefert, nicht als Order-Speicherung.

## Admin-Funktionen

Registriert im Django Admin:

- `Cart`
- `CartItem`

Funktionen:

- Cart `list_display`: `id`, `user`, `session_key`, `customer_group`, `status`, `currency`, `updated_at`
- Cart `list_filter`: `customer_group`, `status`, `currency`
- Cart `search_fields`: `user__email`, `user__username`, `session_key`
- Cart `raw_id_fields`: `user`
- `CartItemInline` im Cart-Admin
- CartItem `list_display`: `cart`, `product`, `variant`, `quantity`, `updated_at`
- CartItem `search_fields`: `product__name`, `variant__name`, `variant__sku`, `cart__user__email`
- CartItem `raw_id_fields`: `cart`, `product`, `variant`

## Tests

Getestet:

- Cart fuer User kann erstellt werden
- Cart mit `session_key` kann erstellt werden
- Cart ohne `user` und ohne `session_key` ist ungueltig
- `customer_group` Standard `b2c`
- `status` Standard `active`
- `__str__` ist sinnvoll
- CartItem kann erstellt werden
- `quantity` Standard `1`
- `quantity = 0` ist ungueltig
- `variant` muss zum `product` gehoeren
- Doppelte `cart`/`product`/`variant`-Kombination wird per IntegrityError verhindert
- `__str__` ist sinnvoll
- `get_or_create_cart` erstellt neuen aktiven Cart
- `get_or_create_cart` findet bestehenden aktiven Cart
- `get_or_create_cart` mit `session_key`
- `get_or_create_cart` ohne user und session_key loest `CartError` aus
- `add_item` erstellt neue Position
- `add_item` erhoeht Menge bei bestehender Position
- `add_item` lehnt Menge `0` ab
- `add_item` lehnt Variante ab, die nicht zum Produkt gehoert
- `update_item_quantity` setzt Menge
- `update_item_quantity` mit `0` loest `CartError` aus
- `remove_item` loescht Position
- `clear_cart` leert Warenkorb
- `calculate_cart` mit B2C-Preis
- `calculate_cart` mit B2B-Preis
- `calculate_cart` bevorzugt Variantenpreis
- `calculate_cart` faellt auf Produktpreis zurueck
- `calculate_cart` loest `CartError` aus, wenn kein Preis existiert

Backend-Pytest: gruen.

## Abhaengigkeiten

- Django ORM
- PostgreSQL
- Django Admin
- `accounts.User` (`settings.AUTH_USER_MODEL`)
- `catalog.Product`
- `catalog.ProductVariant`
- `pricing.services` (`get_active_price`, `build_price_snapshot`, `PriceNotFound`)

## Verbotene Zustaendigkeiten

`cart` baut NICHT:

- Produktstammdaten
- Preisstammdaten
- Bestellungen
- Checkout
- Payment
- Versand
- Rabatte
- Gutscheine
- Frontend
- E-Mail-Versand

## Offene Punkte

- Spaetere Module:
  - `orders` uebernimmt Preis-Snapshots in OrderItems.
  - `payments` uebernimmt Zahlungsanbieter.
  - `shipping` uebernimmt Versandkosten und -arten.
  - Frontend folgt spaeter.

## Freeze-Status

- Status: frozen
- Freeze-Status: frozen
- Notiz: stabiler Erststand, Aenderungen nur noch dokumentiert.

## Aenderungsregel

Aenderungen nur mit dokumentiertem Grund, Impact-Pruefung und Regressionstest. Schnittstellenanpassungen fuer spaetere Module wie `orders`, `payments` oder `shipping` sind erlaubt, wenn sie dokumentiert und getestet werden.
