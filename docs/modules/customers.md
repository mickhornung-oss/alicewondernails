# Customers

## Zweck

`customers` verwaltet Endverbraucherprofile und Adressen.

Es bildet die Grundlage fuer spaetere Konto-, Bestell- und Checkout-Funktionen, baut aber in diesem Block noch keine Checkout- oder Versandlogik.

## CustomerProfile

Felder:

- `user`, One-to-one auf `settings.AUTH_USER_MODEL`
- `display_name`, optional
- `phone`, optional
- `created_at`
- `updated_at`

## Address

Felder:

- `user`, ForeignKey auf `settings.AUTH_USER_MODEL`
- `address_type`
- `full_name`
- `company`, optional
- `street`
- `postal_code`
- `city`
- `country`, Standard `DE`
- `is_default`
- `created_at`
- `updated_at`

Adressarten:

- `billing`
- `shipping`

## Admin-Funktionen

Registriert im Django Admin:

- `CustomerProfile`
- `Address`

Admin-Konfiguration:

- sinnvolle `list_display`
- Suche ueber User, E-Mail, Namen, Adressdaten
- Filter fuer Adresstyp, Land und Default-Status

## Tests

Getestet:

- CustomerProfile kann erstellt werden
- Address kann erstellt werden
- `billing`/`shipping` Choices sind vorhanden
- `__str__` liefert sinnvolle Darstellung

Backend-Pytest: gruen.

## Abhaengigkeiten

- `settings.AUTH_USER_MODEL`
- `accounts.User`
- PostgreSQL
- Django Admin

## Verbotene Zustaendigkeiten

- Keine Produktlogik.
- Kein Katalog.
- Kein Pricing.
- Kein Warenkorb.
- Kein Checkout.
- Kein Payment.
- Keine Versandlogik.
- Keine B2B-Freigabelogik.

## Offene Punkte

- Keine Checkout-Logik.
- Keine Versandlogik.
- Keine komplexe Default-Adressvalidierung.
- Keine API-Endpunkte in diesem Block.

## Freeze-Status

- Status: frozen
- Freeze-Status: frozen
- Nicht locked.
- Notiz: stabiler Erststand.

## Aenderungsregel

Aenderungen nur mit dokumentiertem Grund, Impact-Pruefung und Regressionstest.
