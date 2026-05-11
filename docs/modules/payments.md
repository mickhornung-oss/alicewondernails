# Payments

## Zweck

Das Modul `payments` bietet die technische Grundstruktur für Zahlungslogik.

Es definiert Zahlungsarten, Transaktionen und Snapshots und stellt Services für Zahlungsverwaltung bereit.

**Wichtig:** Dieses Modul baut keine echte Zahlungsanbieter-Anbindung. Das ist für spätere Arbeitsblöcke geplant.

## Grenzen des Moduls

Payments baut **nicht**:
- Checkout-Integration
- echte Zahlungsanbieter-Anbindung (Stripe, PayPal, Klarna, Sofort, Bank-API)
- Webhooks oder externe Callbacks
- Kreditkartendatenspeicherung
- Rechnungen oder Bestelllogik
- E-Mail-Benachrichtigungen
- Frontend-Oberflächenlogik
- Order-Integration

Das Modul ist **eigenständig**, keine versteckten Dependencies.

## Modelle

### PaymentMethod

Zahlungsart-Konfiguration.

Felder:
- `name` (CharField, max_length=120): Anzeigename
- `code` (CharField, max_length=64, unique): Eindeutiger Code
- `provider` (CharField, choices): Klassifikation der Anbieter:
  - `manual` – Manuelle Zahlung
  - `bank_transfer` – Banküberweisung
  - `invoice` – Rechnung
  - `paypal` – PayPal (nur Klassifikation, keine Anbindung)
  - `stripe` – Stripe (nur Klassifikation, keine Anbindung)
  - `other` – Sonstige
- `customer_group` (CharField, choices):
  - `all` – B2C und B2B (beide Gruppen nutzbar)
  - `b2c` – Nur B2C
  - `b2b` – Nur B2B
- `description` (TextField, optional): Beschreibung
- `is_active` (BooleanField, default=True): Aktiv/Inaktiv
- `sort_order` (PositiveIntegerField, default=0): Sortierposition
- `created_at`, `updated_at`: Zeitstempel

Regeln:
- `code` ist eindeutig
- `customer_group` "all" bedeutet für B2C und B2B verfügbar
- `provider` ist nur Klassifikation, keine echte Anbindung
- Sortierung nach `sort_order`, dann `name`

### PaymentTransaction

Zahlungstransaktion.

Felder:
- `order` (ForeignKey, optional): Order-Referenz (später für Checkout-Integration)
- `method` (ForeignKey, optional): PaymentMethod-Referenz
- `payment_reference` (CharField, max_length=120, optional): Externe Referenznummer
- `provider_reference` (CharField, max_length=255, optional): Provider-Referenznummer
- `status` (CharField, choices):
  - `pending` – Ausstehend
  - `authorized` – Autorisiert
  - `paid` – Bezahlt
  - `failed` – Fehlgeschlagen
  - `cancelled` – Storniert
  - `refunded` – Erstattet
- `amount` (DecimalField, max_digits=10, decimal_places=2): Zahlungsbetrag
- `currency` (CharField, max_length=3, default="EUR"): Währung
- `customer_group` (CharField, choices):
  - `b2c` – B2C-Kunde
  - `b2b` – B2B-Kunde
- `provider` (CharField, max_length=64, default="manual"): Provider-Klassifikation
- `raw_response` (JSONField, default={}): Speichert nur unkritische Antwort-Daten
- `metadata` (JSONField, default={}): Speichert nur unkritische Metadaten
- `created_at`, `updated_at`: Zeitstempel
- `paid_at` (DateTimeField, optional): Zeitpunkt Bezahlung
- `cancelled_at` (DateTimeField, optional): Zeitpunkt Stornierung
- `refunded_at` (DateTimeField, optional): Zeitpunkt Erstattung

Regeln:
- `amount` darf nicht negativ sein (CheckConstraint)
- `amount` ist erforderlich bei Erstellung
- `raw_response` und `metadata` dürfen **keine Kreditkartendaten oder Secrets** enthalten
- `order` kann null sein – Transaktionen entstehen auch vor Order-Erstellung
- Sortierung nach `-created_at` (neueste zuerst)

### PaymentMethodSnapshot

Snapshot einer Zahlungsart.

Felder:
- `method` (ForeignKey, optional): PaymentMethod-Referenz (denormalisiert)
- `method_code` (CharField, max_length=64): Code der Methode
- `method_name` (CharField, max_length=120): Name der Methode
- `provider` (CharField, max_length=64): Provider-Klassifikation
- `customer_group` (CharField, choices):
  - `b2c` – B2C
  - `b2b` – B2B
- `created_at` (DateTimeField): Erstellungszeitpunkt

Zweck:
- Snapshot-Vorbereitung für später Orders/Checkout
- Eigenständig stabil, wird nicht mit PaymentMethod-Änderungen synchron gehalten
- Denormalisierte Daten für historische Konsistenz

## Services

### PaymentError

Eigene Exception-Klasse für Payment-Fehler.

### get_available_payment_methods(customer_group="b2c")

Gibt verfügbare Zahlungsmethoden für eine Kundengruppe zurück.

Logik:
- Filtert aktive Methoden (`is_active=True`)
- Filtert Kundengruppen:
  - `customer_group="all"` passt immer
  - `customer_group="b2c"` oder `customer_group="b2b"` must exakt passen
- Sortiert nach `sort_order`, `name`
- Wirft `PaymentError` bei ungültiger Kundengruppe

### get_payment_method(code, customer_group="b2c")

Sucht eine aktive Zahlungsmethode nach Code.

Logik:
- Sucht `PaymentMethod` mit `code` und `is_active=True`
- Prüft Kundengruppen-Kompatibilität
- Wirft `PaymentError` bei nicht gefundener Methode oder ungültiger Kundengruppe

### build_payment_method_snapshot(method, customer_group="b2c")

Erstellt einen Snapshot einer Zahlungsmethode.

Rückgabe:
```python
{
    "method_id": int,
    "method_code": str,
    "method_name": str,
    "provider": str,
    "customer_group": str,
}
```

Keine externe API, nur lokale Denormalisierung.

### create_payment_transaction(order=None, method=None, amount=None, currency="EUR", customer_group="b2c", payment_reference="", provider_reference="", metadata=None)

Erstellt eine neue Zahlungstransaktion.

Logik:
- `amount` ist erforderlich und darf nicht negativ sein
- `order` optional (für spätere Checkout-Integration)
- `method` optional (wenn nicht gesetzt, `provider="manual"`)
- Wirft `PaymentError` bei ungültigen Daten
- Keine externe Zahlung auslösen
- Keine API-Aufrufe

### mark_payment_paid(transaction)

Markiert Transaktion als bezahlt.

Setzt:
- `status = "paid"`
- `paid_at = now()`

### mark_payment_failed(transaction)

Markiert Transaktion als fehlgeschlagen.

Setzt:
- `status = "failed"`

### cancel_payment(transaction)

Storniert Transaktion.

Setzt:
- `status = "cancelled"`
- `cancelled_at = now()`

### refund_payment(transaction)

Erstattet Transaktion.

Setzt:
- `status = "refunded"`
- `refunded_at = now()`

## Admin-Funktionen

### PaymentMethodAdmin

- `list_display`: name, code, provider, customer_group, is_active, sort_order
- `list_filter`: provider, customer_group, is_active, created_at
- `search_fields`: name, code, provider
- `fieldsets`: Grundinfo, Status, Zeitstempel
- `ordering`: sort_order, name

### PaymentTransactionAdmin

- `list_display`: id, order, method, status, amount, currency, customer_group, provider, created_at
- `list_filter`: status, provider, customer_group, currency, created_at
- `search_fields`: payment_reference, provider_reference, order__order_number, method__name, method__code
- `raw_id_fields`: order, method
- `readonly_fields`: raw_response, metadata, timestamps
- `fieldsets`: Grundinfo, Betrag, Provider, Daten, Zeitstempel
- `ordering`: -created_at

### PaymentMethodSnapshotAdmin

- `list_display`: method_name, method_code, provider, customer_group, created_at
- `list_filter`: provider, customer_group, created_at
- `search_fields`: method_name, method_code, provider
- `readonly_fields`: Alle (Snapshots sind immutable)
- `ordering`: -created_at

## Tests

37 Tests decken ab:

**PaymentMethod (7 Tests):**
- Erstellung
- `code` Eindeutigkeit
- `customer_group` Choices (all/b2c/b2b)
- Provider speichern
- `__str__`
- Sortierung

**PaymentTransaction (7 Tests):**
- Erstellung
- `amount` nicht negativ (CheckConstraint)
- `status` default pending
- `raw_response`/`metadata` default dict
- `__str__`
- Sortierung

**PaymentMethodSnapshot (3 Tests):**
- Erstellung
- `__str__`
- Sortierung

**Payment Services (13 Tests):**
- `get_available_payment_methods` für B2C/B2B
- Filter aktive Methoden
- Filter nach Kundengruppe
- `get_payment_method` findet Methode
- `get_payment_method` prüft Kundengruppe
- `get_payment_method` wirft Error
- `build_payment_method_snapshot` enthält Felder
- `create_payment_transaction` ohne externe API
- `create_payment_transaction` lehnt negative Beträge ab
- Status-Änderungen (paid, failed, cancelled, refunded)

**Admin (5 Tests):**
- Admin-Registrierung

Alle Tests **100% grün** (235/235), keine Warnungen.

## Abhängigkeiten

Intern:
- Django ORM (PostgreSQL)
- `django.utils.timezone` für Zeitstempel

Extern:
- Keine ForeignKeys zu anderen Modulen außer optional zu `orders.Order` (für spätere Checkout-Integration)

## Freeze-Status und Änderungsregel

**Freeze-Status:** payments ist nach Arbeitsblock 10.1 **frozen** (nicht locked).

**Änderungsregel nach Freeze:**
- Änderungen nur mit dokumentiertem Grund
- Impact-Prüfung vor Implementierung erforderlich
- Regressionstest (alle 235+ Tests) erforderlich
- Änderungen in PROGRESS.md und ggf. DECISIONS.md dokumentieren

## Verbotene Zuständigkeiten

Payments macht **nicht**:
- ❌ Checkout-Integration (kommt später)
- ❌ echte Zahlungsanbieter-Anbindung
- ❌ Stripe/PayPal/Klarna/Sofort API-Anbindung
- ❌ Webhooks oder Callbacks
- ❌ Kreditkartendatenspeicherung
- ❌ PCI-DSS-Compliance-Logik
- ❌ Rechnungen oder Bestelländerungen
- ❌ E-Mail-Versand
- ❌ Frontend-Logik
- ❌ Signals oder Seiteneffekte

## Status

- **Modul:** `payments`
- **Arbeitsblock:** 10 – Payments-Grundstruktur, 10.1 – Review und Freeze
- **Tests:** 37 Tests, 235 gesamt, 100% grün
- **Dokumentation:** Deutsch, sachlich
- **Freeze-Status:** frozen (nicht locked)

Nächster Block: 10.2 oder später (nutzer entscheidet)

