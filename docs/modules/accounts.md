# Accounts

## Zweck

`accounts` ist das zentrale User- und Rollenstatusmodul.

Es bildet die Grundlage fuer:

- Benutzerkonto
- B2C-/B2B-Status
- spaetere Registrierung
- spaeteres Login
- spaetere Rechte- und Rollenlogik

## Modelle

### User

Pfad: `apps.accounts.User`

Basis: `django.contrib.auth.models.AbstractUser`

Zusaetzliche Felder:

- `email`, eindeutig
- `customer_status`
- `created_at`
- `updated_at`

## Rollen-/Statuslogik

`customer_status` hat diese Werte:

- `consumer`
- `business_pending`
- `business_approved`

Properties:

- `is_consumer`
- `is_business_pending`
- `is_business_approved`

Django-Felder `is_staff` und `is_superuser` bleiben fuer Staff/Admin/Superadmin relevant.

## Admin-Funktionen

`User` ist im Django Admin registriert.

Admin-Konfiguration:

- basiert auf `UserAdmin`
- `customer_status` und `email` in `list_display`
- Filter fuer `customer_status`, `is_staff`, `is_active`
- Suche ueber `username`, `email`, `first_name`, `last_name`

## Tests

Getestet:

- User wird mit Defaultstatus `consumer` erstellt
- E-Mail wird gesetzt
- E-Mail ist eindeutig
- `business_pending` Property funktioniert
- `business_approved` Property funktioniert

Backend-Pytest: gruen.

## Abhaengigkeiten

- Django Auth
- `settings.AUTH_USER_MODEL`
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
- Kein Login-Frontend.
- Keine Registrierung oder Passwort-Reset-Logik in diesem Modulstand.

## Offene Punkte

- Keine oeffentliche Registrierung in diesem Block.
- Kein Login-Frontend in diesem Block.
- Keine Passwort-Reset-Logik in diesem Block.
- Keine API-Endpunkte in diesem Block.
- Rollen-/Gruppenfeinheiten folgen spaeter.

## Freeze-Status

- Status: frozen
- Freeze-Status: frozen
- Nicht locked.
- Notiz: stabiler Erststand.

## Aenderungsregel

Aenderungen nur mit dokumentiertem Grund, Impact-Pruefung und Regressionstest.
