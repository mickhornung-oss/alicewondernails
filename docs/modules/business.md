# Business

## Zweck

`business` verwaltet Firmenprofile und die Datenbasis fuer spaetere B2B-Antraege und Admin-Freigaben.

In diesem Block gibt es nur stabile Datenbasis und Django-Admin-Verwaltung.

## BusinessProfile

Felder:

- `user`, One-to-one auf `settings.AUTH_USER_MODEL`
- `company_name`
- `contact_person`, optional
- `vat_id`, optional
- `status`
- `admin_note`, optional
- `requested_at`
- `reviewed_at`, optional
- `reviewed_by`, optionaler ForeignKey auf `settings.AUTH_USER_MODEL`
- `created_at`
- `updated_at`

## B2B-Antrags-/Freigabestatus

Statuswerte:

- `pending`
- `approved`
- `rejected`

Der User-Account selbst nutzt parallel `customer_status` aus `accounts`:

- `consumer`
- `business_pending`
- `business_approved`

Eine automatische Synchronisation zwischen `BusinessProfile.status` und `User.customer_status` wird in diesem Block noch nicht gebaut.

## Admin-Funktionen

`BusinessProfile` ist im Django Admin registriert.

Admin-Konfiguration:

- `company_name`, `user`, `status`, `requested_at`, `reviewed_at` in `list_display`
- Filter fuer `status`
- Suche ueber `company_name`, `user__email`, `user__username`, `vat_id`

## Tests

Getestet:

- BusinessProfile kann erstellt werden
- Statuswerte `pending`, `approved`, `rejected` sind vorhanden
- `reviewed_by` kann gesetzt werden
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
- Keine Datei-Uploads fuer Gewerbenachweise.
- Keine automatische B2B-Freigabe-API.

## Offene Punkte

- Keine Datei-Uploads fuer Gewerbenachweise.
- Keine B2B-Preise.
- Keine B2B-Produkte.
- Keine Freigabe-API.
- Keine Auditlog-Implementierung.

## Freeze-Status

- Status: frozen
- Freeze-Status: frozen
- Nicht locked.
- Notiz: stabiler Erststand.

## Aenderungsregel

Aenderungen nur mit dokumentiertem Grund, Impact-Pruefung und Regressionstest.
