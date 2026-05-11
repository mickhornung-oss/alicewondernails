# Checkout

## Zweck

Das Modul `checkout` verwaltet die technische Backend-Struktur für Checkout-Sitzungen.

Es definiert:
- Checkout-Sitzungen (CheckoutSession) mit Verbindung zu Cart, Versand, Zahlung
- Checkout-Ereignisse (CheckoutEvent) für interne Nachverfolgung
- Services für Checkout-Ablauf (Start, Methoden-Auswahl, Validierung, Order-Erzeugung)
- Admin-Zugang für Checkout-Verwaltung

Das Modul ist die technische Grundstruktur für den späteren Kaufabschluss.

**Wichtig:** Dieses Modul baut keine echte Payment-Ausführung, keine echte Versandbuchung und keine Rechnungen.

## Grenzen des Moduls

Checkout baut **nicht**:
- Frontend-Oberflächenlogik
- echte Payment-Ausführung
- echte Versandbuchung (DHL/Hermes/Warenpost)
- Rechnungslogik
- E-Mail-Versand
- Webhooks oder externe Callbacks
- finale Steuerberechnung
- Checkout-APIs für Clients

Das Modul ist **eigenständig mit Services-Dependencies** auf cart, shipping, payments, legal, consent, orders, auditlog.

## Modelle

### CheckoutSession

Technische Sitzung für einen Checkout-Vorgang.

Felder:
- `user`: optional ForeignKey auf `settings.AUTH_USER_MODEL` (null=True, blank=True, on_delete=SET_NULL)
- `cart`: ForeignKey auf `cart.Cart` (on_delete=PROTECT, Pflicht)
- `status`: choices (started, validated, order_created, cancelled, expired), default=started
- `customer_group`: choices (b2c, b2b), default=b2c
- `currency`: CharField default=EUR
- `shipping_method`: optional ForeignKey auf `shipping.ShippingMethod`
- `shipping_snapshot`: JSONField (Snapshot der Versandmethode, keine Secrets)
- `shipping_amount`: DecimalField (10,2), default 0.00, >= 0
- `payment_method`: optional ForeignKey auf `payments.PaymentMethod`
- `payment_snapshot`: JSONField (Snapshot der Zahlungsmethode, keine Secrets)
- `cart_subtotal`: DecimalField (10,2), default 0.00, >= 0
- `order_total`: DecimalField (10,2), default 0.00, >= 0
- `item_count`: PositiveIntegerField, default 0, >= 0
- `legal_snapshot`: JSONField (Snapshot der Rechtsvereinbarungen)
- `consent_snapshot`: JSONField (Snapshot der Zustimmungen)
- `order`: optional OneToOneField auf `orders.Order` (null=True, blank=True, on_delete=SET_NULL)
- `started_at`: DateTimeField (auto_now_add=True)
- `validated_at`: optional DateTimeField
- `order_created_at`: optional DateTimeField
- `cancelled_at`: optional DateTimeField
- `expires_at`: optional DateTimeField
- `created_at`, `updated_at`: DateTimeField (auto_now_add/auto_now)

Regeln:
- `cart` ist Pflicht (PROTECT, keine Löschung)
- `user` ist optional (aus cart.user abgeleitet)
- Summen dürfen nicht negativ sein (CheckConstraint)
- JSON-Snapshots dürfen keine Secrets enthalten
- Ordering: [-updated_at] (Neueste zuerst)
- Indizes: [status, -updated_at], [user, -created_at], [cart]

### CheckoutEvent

Einfache technische Ereignisse im Checkout-Ablauf (nicht als Ersatz für auditlog).

Felder:
- `checkout`: ForeignKey auf CheckoutSession (on_delete=CASCADE)
- `event_type`: choices (started, validated, shipping_selected, payment_selected, legal_checked, consent_checked, order_created, cancelled, error)
- `message`: optional TextField
- `metadata`: JSONField (zusätzliche Daten, keine Secrets)
- `created_at`: DateTimeField (auto_now_add=True)

Regeln:
- `checkout` ist Pflicht
- Ordering: [-created_at] (Neueste zuerst)
- Indizes: [checkout, -created_at], [event_type]

## Versandmethoden-Auswahl

Datei: `backend/apps/checkout/services.py`

Service: `select_shipping_method(checkout, shipping_method_code, country_code="DE")`

Regeln:
- Nutzt `shipping.services.get_shipping_method`
- Nutzt `shipping.services.build_shipping_snapshot`
- Setzt `checkout.shipping_method`, `shipping_snapshot`, `shipping_amount`
- Erzeugt CheckoutEvent `shipping_selected`
- Keine echte Versandbuchung

## Zahlungsmethoden-Auswahl

Service: `select_payment_method(checkout, payment_method_code)`

Regeln:
- Nutzt `payments.services.get_payment_method`
- Nutzt `payments.services.build_payment_method_snapshot`
- Setzt `checkout.payment_method`, `payment_snapshot`
- Erzeugt CheckoutEvent `payment_selected`
- Keine echte Zahlung

## Legal-Snapshot

Service: `build_legal_snapshot(customer_group="b2c")`

Regeln:
- Nutzt `legal.services.get_active_document_version`
- Für B2C erfordert: terms_b2c, privacy_policy, withdrawal_b2c, shipping_info, payment_info
- Für B2B erfordert: terms_b2b, privacy_policy, shipping_info, payment_info
- Wirft CheckoutError bei fehlenden Pflichtdokumenten
- Snapshot enthält: document_type, target_group, title, version, version_id, effective_from
- Keine finalen Rechtstexte
- Keine Rechtsberatung

## Consent-Snapshot

Service: `build_consent_snapshot(user=None, session_key=None)`

Regeln:
- Nutzt `consent.services.get_latest_consent`
- Snapshot enthält pro Kategorie: category_key, granted, consent_version, record_id, created_at
- Leeres dict oder Default wenn keine Records
- Keine Cookie-Banner-Logik

## Order-Erzeugung

Service: `create_order_from_checkout(checkout)`

Regeln:
- checkout muss validated sein
- Nutzt `orders.services.create_order_from_cart` zum Erzeugen der Order-Grundlage
- Nutzt **`orders.services.apply_checkout_snapshot_to_order(order, checkout)`** (AB 12) zur Snapshot-Übertragung
  - Überträgt shipping_amount von checkout zu order
  - Überträgt shipping_snapshot, payment_snapshot von checkout zu order
  - Erzeugt checkout_snapshot mit Order-Kontext (checkout_id, customer_group, currency, item_count, amounts)
  - Berechnet Order.total_amount = subtotal_amount + shipping_amount (Finalisierung)
- Setzt `checkout.order`, status `order_created`, `order_created_at`
- Erzeugt CheckoutEvent `order_created`
- Optional: Erzeugt auditlog-Entry (wenn sauber ohne frozen-Modelländerung)
- **Keine echte Zahlung, keine echte Versandbuchung** – nur Snapshot-Transfer für Audit/Historisierung

## Services

Datei: `backend/apps/checkout/services.py`

Bereitgestellt:
- `CheckoutError` Exception (Validierungsfehler)
- `start_checkout(cart, user, expires_at)` – Erstellt CheckoutSession, erfordert aktiven Cart mit Items und User
- `select_shipping_method(checkout, shipping_method_code, country_code)` – Wählt Versandmethode
- `select_payment_method(checkout, payment_method_code)` – Wählt Zahlungsmethode
- `build_legal_snapshot(customer_group)` – Erzeugt Legal-Snapshot
- `build_consent_snapshot(user, session_key)` – Erzeugt Consent-Snapshot
- `validate_checkout(checkout)` – Validiert Checkout, berechnet Summen, setzt status validated
- `create_order_from_checkout(checkout)` – Erzeugt Order aus Cart
- `cancel_checkout(checkout, message)` – Storniert Checkout
- `log_checkout_event(checkout, event_type, message, metadata)` – Erstellt Event

## Admin-Funktionen

Datei: `backend/apps/checkout/admin.py`

CheckoutSessionAdmin:
- list_display: [id, user, cart, status, customer_group, cart_subtotal, shipping_amount, order_total, item_count, updated_at]
- list_filter: [status, customer_group, currency, created_at]
- search_fields: [user__email, user__username, cart__session_key, order__order_number]
- raw_id_fields: [user, cart, shipping_method, payment_method, order]
- readonly_fields: [shipping_snapshot, payment_snapshot, legal_snapshot, consent_snapshot, Zeitstempel]
- inline: CheckoutEventInline (read-only, simpel)

CheckoutEventAdmin:
- list_display: [id, checkout, event_type, message, created_at]
- list_filter: [event_type, created_at]
- search_fields: [message, checkout__user__email, checkout__order__order_number]
- readonly_fields: [All]
- has_add=False, has_change=False, has_delete=False (read-only)

## Migrationen

Datei: `backend/apps/checkout/migrations/0001_initial.py`

Erstellt:
- CheckoutSession Table mit allen Feldern, Constraints, Indizes
- CheckoutEvent Table mit allen Feldern, Indizes
- Beziehungen zwischen Models und zu anderen Apps

## Tests

Datei: `backend/apps/checkout/tests/test_checkout.py`

Test-Kategorien:
- CheckoutSessionModel (6 Tests): Creation, defaults, constraints, snapshots, __str__
- CheckoutEventModel (4 Tests): Creation, metadata, __str__, ordering
- CheckoutServices (6 Tests): start_checkout, validation, cancel, log_event

Alle Tests: 16/16 bestanden

## Abhängigkeiten

Interne Dependencies:
- `cart.models.Cart`, `cart.models.CartItem` – Warenkorbverwaltung
- `cart.services.calculate_cart` – Warensummen berechnen
- `shipping.models.ShippingMethod`, `shipping.models.ShippingZone` – Versand-Konfiguration
- `shipping.services.get_shipping_method`, `build_shipping_snapshot` – Versand-Service
- `payments.models.PaymentMethod` – Zahlungsmethoden
- `payments.services.get_payment_method`, `build_payment_method_snapshot` – Zahlungs-Service
- `legal.models.LegalDocument`, `legal.models.LegalDocumentVersion` – Rechtsdokumente
- `legal.services.get_active_document_version` – Legal-Service
- `consent.models.ConsentCategory`, `consent.models.ConsentRecord` – Zustimmungen
- `consent.services.get_latest_consent` – Consent-Service
- `orders.models.Order`, `orders.models.OrderItem` – Bestellungen
- `orders.services.create_order_from_cart` – Order-Service
- `auditlog.services.create_audit_log` – Audit-Logging (optional)

Keine Dependencies auf frozen Modules außer den oben erwähnten services (sauber gekapselt).

## Verbotene Zuständigkeiten

Checkout baut NICHT:
- Frontend-UI oder Views
- echte Payment-Ausführung oder Stripe/PayPal/Klarna Integration
- echte Versand-Ausführung oder DHL/Hermes/Warenpost Integration
- Rechnungen oder Rechnungsnummern
- E-Mail-Versand
- Cookie-Banner-Logik
- finale Steuerberechnung
- Webhooks
- Echte Rechtsberatung
- Checkout-APIs für externe Clients

Checkout ist nach Arbeitsblock 11 `tested` (noch nicht frozen). Review/Freeze folgt in Arbeitsblock 11.1. Änderungen nur mit dokumentiertem Grund, Impact-Prüfung und Regressionstest.
