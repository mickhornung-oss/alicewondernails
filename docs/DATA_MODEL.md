# Datenmodell

Dieses Dokument wird später die Datenstruktur der Shop-/Plattform-Version abbilden.

## Geplanter Inhalt

- Kern-Entitäten: Produkte, Kunden, Bestellungen, Preise, Warenkorb, Zahlungen, Versand
- Nutzer und Rollen
- Rechtstexte und Zustimmung
- Business-Accounts vs. Privatkunden
- Audit-/Logging-Struktur

## Aktueller Status

- Arbeitsblock 02 hat den ersten fachlichen Backend-Datenmodellstand gebaut.
- `accounts`, `customers` und `business` sind als Django-Apps vorhanden.
- Custom User Model ist aktiv: `accounts.User`.
- Migrationen wurden nach lokalem Entwicklungsdatenbank-Reset erfolgreich ausgefuehrt.
- Arbeitsblock 02.1 hat `accounts`, `customers` und `business` reviewed und auf `frozen` gesetzt.
- Arbeitsblock 03 hat `catalog` als fachlichen Erststand gebaut.
- Arbeitsblock 03.1 hat `catalog` reviewed und auf `frozen` gesetzt.
- Arbeitsblock 04 hat `pricing` als fachlichen Erststand gebaut.
- Arbeitsblock 04.1 hat `pricing` reviewed und auf `frozen` gesetzt.
- Arbeitsblock 05 hat `cart` als fachlichen Erststand gebaut.
- Arbeitsblock 05.1 hat `cart` reviewed und auf `frozen` gesetzt.
- Backend-Pytest ist gruen: 72 Tests bestanden.

## Accounts

### User

Modell: `apps.accounts.User`

Basis: `django.contrib.auth.models.AbstractUser`

Zusaetzliche Felder:

- `email`, eindeutig
- `customer_status`
- `created_at`
- `updated_at`

Customer-Status:

- `consumer`
- `business_pending`
- `business_approved`

Properties:

- `is_consumer`
- `is_business_pending`
- `is_business_approved`

Django-Felder `is_staff` und `is_superuser` bleiben fuer Staff/Admin/Superadmin relevant.

## Customers

### CustomerProfile

- `user`, One-to-one auf `settings.AUTH_USER_MODEL`
- `display_name`, optional
- `phone`, optional
- `created_at`
- `updated_at`

### Address

- `user`, ForeignKey auf `settings.AUTH_USER_MODEL`
- `address_type`: `billing` oder `shipping`
- `full_name`
- `company`, optional
- `street`
- `postal_code`
- `city`
- `country`, Standard `DE`
- `is_default`
- `created_at`
- `updated_at`

Noch keine Checkout-, Versand- oder uebertriebene Adresslogik.

## Business

### BusinessProfile

- `user`, One-to-one auf `settings.AUTH_USER_MODEL`
- `company_name`
- `contact_person`, optional
- `vat_id`, optional
- `status`: `pending`, `approved`, `rejected`
- `admin_note`, optional
- `requested_at`
- `reviewed_at`, optional
- `reviewed_by`, optionaler ForeignKey auf `settings.AUTH_USER_MODEL`
- `created_at`
- `updated_at`

Noch keine Datei-Uploads, keine B2B-Preise, keine B2B-Produkte und keine Freigabe-API.

## Catalog

### ProductCategory

- `name`, CharField
- `slug`, SlugField unique
- `description`, optional
- `image`, optional FileField
- `created_at`, `updated_at`

### Product

- `category`, ForeignKey auf ProductCategory
- `name`, CharField
- `slug`, SlugField unique
- `description`, optional
- `product_type`: GEL, CARE, ACCESSORY, etc.
- `is_active`, default True
- `created_at`, `updated_at`

Keine Preise, keine Verfügbarkeit, keine Bestände.

### ProductVariant

- `product`, ForeignKey auf Product
- `name`, CharField
- `sku`, CharField unique
- `color_name`, optional
- `color_code`, optional
- `created_at`, `updated_at`

Referenzen zwischen Product/Variant, keine Bestände.

### ProductImage

- `product`, ForeignKey auf Product
- `variant`, optional ForeignKey auf ProductVariant
- `image`, ImageField
- `alt_text`, optional
- `sort_order`, default 0
- `created_at`, `updated_at`

## Pricing

### ProductPrice

- `product`, ForeignKey auf Product
- `variant`, optional ForeignKey auf ProductVariant
- `customer_group`: `b2c` oder `b2b`
- `amount`, DecimalField (Listenpreis)
- `currency`, default EUR
- `tax_rate`, DecimalField, default 0.00
- `price_includes_tax`, BooleanField, default True
- `valid_from`, optional DateTimeField
- `valid_until`, optional DateTimeField
- `is_active`, BooleanField, default True
- `created_at`, `updated_at`

Preise sind nach Kundengruppe filterbar. Variantenpreise überschreiben Produktpreise. Spaetere Preisänderungen beeinflussen bestehende OrderItems nicht (Snapshots).

## Cart

### Cart

- `user`, optional ForeignKey auf `settings.AUTH_USER_MODEL`
- `session_key`, optional CharField (fuer anonyme Nutzer)
- `customer_group`: `b2c` oder `b2b`, default `b2c`
- `currency`, default EUR
- `status`: `active`, `converted`, `abandoned`, default `active`
- `created_at`, `updated_at`

### CartItem

- `cart`, ForeignKey auf Cart
- `product`, ForeignKey auf Product
- `variant`, optional ForeignKey auf ProductVariant
- `quantity`, PositiveIntegerField, default 1, > 0
- `created_at`, `updated_at`

UniqueConstraint auf (cart, product, variant) zur Deduplication. Keine Preise, keine Snapshots, keine Bestände.

## Orders

### Order

- `order_number`, CharField unique (Format: AWN-YYYYMMDD-XXXXXX)
- `user`, ForeignKey auf `settings.AUTH_USER_MODEL`
- `cart`, optional ForeignKey auf Cart (SET_NULL)
- `customer_group`: `b2c` oder `b2b`
- `status`: `draft`, `placed`, `cancelled`, `completed`
- `currency`, default EUR
- `subtotal_amount`, DecimalField (Summe aus OrderItems)
- `total_amount`, DecimalField (subtotal_amount + shipping_amount, final order sum)
- `item_count`, PositiveIntegerField (Summe der Mengen)
- Adress-Snapshots (Billing/Shipping): full_name, company, street, postal_code, city, country
- **AB 12 Erweiterungen**:
  - `shipping_amount`, DecimalField, default 0.00, >= 0 (finale Versandkosten)
  - `shipping_snapshot`, JSONField (Versandmethoden-Metadaten: method_code, method_name, zone_code, zone_name, amount, currency)
  - `payment_snapshot`, JSONField (Zahlungsmethoden-Metadaten: method_code, method_name, provider, customer_group)
  - `checkout_snapshot`, JSONField (Checkout-Kontext: checkout_id, customer_group, currency, item_count, cart_subtotal, shipping_amount, order_total)
- `placed_at`, optional DateTimeField
- `cancelled_at`, optional DateTimeField
- `created_at`, `updated_at`

**Wichtig**: `total_amount = subtotal_amount + shipping_amount`. Die Snapshots speichern die finalen kaufrelevanten Daten dauerhaft ab. Spaetere Aenderungen an Produkten, Preisen, Versandmethoden oder Zahlungsmethoden beeinflussen bestehende Orders nicht.

### OrderItem

- `order`, ForeignKey auf Order
- `product`, optional ForeignKey auf Product (SET_NULL)
- `variant`, optional ForeignKey auf ProductVariant (SET_NULL)
- `price`, optional ForeignKey auf ProductPrice (SET_NULL)
- Snapshot-Felder (unveraenderlich):
  - `product_id_snapshot`, PositiveIntegerField
  - `variant_id_snapshot`, optional PositiveIntegerField
  - `price_id_snapshot`, optional PositiveIntegerField
  - `product_name`, CharField
  - `variant_name`, optional CharField
  - `sku`, optional CharField
- `customer_group`: `b2c` oder `b2b`
- `quantity`, PositiveIntegerField, > 0
- `unit_amount`, DecimalField (Preis pro Einheit zum Bestellzeitpunkt)
- `line_total`, DecimalField (= quantity * unit_amount)
- `currency`, default EUR
- `tax_rate`, DecimalField, default 0.00
- `price_includes_tax`, BooleanField, default True
- `created_at`, `updated_at`

Snapshot-Felder speichern alle Informationen zum Bestellzeitpunkt. Spaetere Aenderungen an Produkten oder Preisen aendern bestehende OrderItems nicht.

## Checkout

### CheckoutSession

- `user`, optional ForeignKey auf `settings.AUTH_USER_MODEL`
- `cart`, ForeignKey auf Cart (Pflicht, on_delete=PROTECT)
- `status`: `started`, `validated`, `order_created`, `cancelled`, `expired`
- `customer_group`: `b2c` oder `b2b`
- `currency`, default EUR
- `shipping_method`, optional ForeignKey auf `shipping.ShippingMethod`
- `shipping_snapshot`, JSONField
- `shipping_amount`, DecimalField >= 0
- `payment_method`, optional ForeignKey auf `payments.PaymentMethod`
- `payment_snapshot`, JSONField
- `cart_subtotal`, DecimalField (aus Cart calculation)
- `order_total`, DecimalField (= cart_subtotal + shipping_amount)
- `item_count`, PositiveIntegerField
- `legal_snapshot`, JSONField (Rechtsvereinbarungen)
- `consent_snapshot`, JSONField (Zustimmungen)
- `order`, optional OneToOneField auf Order
- Timestamps: started_at, validated_at, order_created_at, cancelled_at, expires_at, created_at, updated_at

CheckoutSession ist rein technische Ablaufverwaltung. Nach Order-Erzeugung werden finale Snapshots in die Order überführt (AB 12).

### CheckoutEvent

- `checkout`, ForeignKey auf CheckoutSession (on_delete=CASCADE)
- `event_type`: started, validated, shipping_selected, payment_selected, legal_checked, consent_checked, order_created, cancelled, error
- `message`, optional TextField
- `metadata`, JSONField
- `created_at`, DateTimeField

Read-only Ablauf-Log fuer Checkout-Sessions.

## Legal

### LegalDocument

- `document_type`, CharField unique
- `target_group`: `b2c`, `b2b`, `all`
- `title`, CharField
- `slug`, SlugField unique
- `created_at`, `updated_at`

### LegalDocumentVersion

- `document`, ForeignKey auf LegalDocument
- `version`, CharField
- `status`: `draft`, `active`, `archived`
- `content`, TextField
- `summary`, optional TextField
- `effective_from`, optional DateTimeField
- `activated_at`, optional DateTimeField
- `created_at`, `updated_at`

Versionierte Rechtstexte (Terms, Privacy, Withdrawal, etc.). Checksummen/Hashes könnten später fuer Audit-Trail hinzukommen.

## Consent

### ConsentCategory

- `category_key`, CharField unique
- `display_name`, CharField
- `description`, optional
- `is_required`, BooleanField
- `sort_order`, default 0
- `created_at`, `updated_at`

Kategorienuebersicht (z.B. Newsletter, Analytics, Marketing).

### ConsentRecord

- `user`, optional ForeignKey auf `settings.AUTH_USER_MODEL`
- `session_key`, optional CharField (fuer anonyme)
- `category_key`, ForeignKey auf ConsentCategory
- `granted`, BooleanField
- `consent_version`, CharField (versioniert)
- `created_at`, `updated_at`

Zustimmungen pro Nutzer/Session und Kategorie.

## Auditlog

### AuditLogEntry

- `action`, CharField (z.B. created, updated, deleted)
- `entity_type`, CharField (ContentType name)
- `entity_id`, PositiveIntegerField
- `user`, optional ForeignKey auf `settings.AUTH_USER_MODEL`
- `changes`, JSONField (alte/neue Werte)
- `message`, optional TextField
- `ip_address`, optional GenericIPAddressField
- `created_at`, DateTimeField

Read-only Audit-Trail fuer Datenaenderungen. Keine Löschung.

## Shipping

### ShippingZone

- `name`, CharField
- `code`, CharField unique
- `countries`, ArrayField CharField (Liste der Laender, z.B. ['DE', 'AT', 'CH'])
- `is_active`, BooleanField, default True
- `sort_order`, default 0
- `created_at`, `updated_at`

Versandzonen nach Länder.

### ShippingMethod

- `zone`, ForeignKey auf ShippingZone (on_delete=PROTECT)
- `name`, CharField
- `code`, CharField unique
- `customer_group`: `all`, `b2c`, `b2b`
- `base_price`, DecimalField >= 0
- `currency`, default EUR
- `estimated_min_days`, optional PositiveIntegerField
- `estimated_max_days`, optional PositiveIntegerField
- `is_active`, BooleanField, default True
- `sort_order`, default 0
- `created_at`, `updated_at`

Versandmethoden pro Zone (Standard, Express, etc.). Keine DHL/Hermes/Warenpost-Integration, nur Metadaten.

### ShippingRateSnapshot

- `method`, optional ForeignKey auf ShippingMethod (SET_NULL)
- `method_code`, CharField
- `method_name`, CharField
- `zone_code`, CharField
- `zone_name`, CharField
- `customer_group`: `b2c`, `b2b`
- `amount`, DecimalField >= 0
- `currency`, default EUR
- `estimated_min_days`, optional PositiveIntegerField
- `estimated_max_days`, optional PositiveIntegerField
- `created_at`, DateTimeField

Audit-Trail fuer Versandsätze. Read-only Admin.

## Payments

### PaymentMethod

- `name`, CharField
- `code`, CharField unique
- `provider`: `manual`, `bank_transfer`, `invoice`, `paypal`, `stripe`, `other`
- `customer_group`: `all`, `b2c`, `b2b`
- `description`, optional
- `is_active`, BooleanField, default True
- `sort_order`, default 0
- `created_at`, `updated_at`

Verfügbare Zahlungsmethoden. Keine echte Stripe/PayPal-Integration, nur Metadaten.

### PaymentTransaction

- `order`, optional ForeignKey auf Order
- `method`, optional ForeignKey auf PaymentMethod
- `payment_reference`, CharField
- `provider_reference`, optional CharField
- `status`: `pending`, `authorized`, `paid`, `failed`, `cancelled`, `refunded`
- `amount`, DecimalField >= 0
- `currency`, default EUR
- `customer_group`: `b2c`, `b2b`
- `provider`, CharField
- `raw_response`, JSONField (keine Secrets)
- `metadata`, JSONField (keine Secrets)
- `paid_at`, optional DateTimeField
- `cancelled_at`, optional DateTimeField
- `refunded_at`, optional DateTimeField
- `created_at`, `updated_at`

Zahlungsvorgänge. Keine externe API-Integration, keine Kreditkartenspeicherung.

### PaymentMethodSnapshot

- `method`, optional ForeignKey auf PaymentMethod
- `method_code`, CharField
- `method_name`, CharField
- `provider`, CharField
- `customer_group`: `b2c`, `b2b`
- `created_at`, DateTimeField

Audit-Trail fuer Zahlungsmethoden-Änderungen.

## Zusammenfassung: Keine echten Integrationen

Alle Snapshots (Legal, Consent, Shipping, Payment, Checkout→Order) sind reine Metadaten, keine echten Provider-Anbindungen. Das System ist zur lokalen Entwicklung ausgelegt und später um echte Integrationen erweiterbar.

## Noch nicht gebaut

Diese Module und Datenmodelle kommen erst in spaeteren Arbeitsbloecken:

- cart / Warenkorb
- orders / Bestellungen
- payments / Zahlungen
- shipping / Versand
- legal / Rechtstexte
- consent / Zustimmung
- auditlog / Audit-Trail

Die frozen Module `accounts`, `customers`, `business` und `catalog` duerfen nur mit dokumentiertem Grund, Impact-Pruefung und Regressionstest geaendert werden.

## Catalog

### ProductCategory

- `name`
- `slug`, eindeutig
- `description`, optional
- `parent`, optionale Selbstreferenz fuer verschachtelte Kategorien
- `sort_order`, Standard `0`
- `is_active`, Standard `True`
- `created_at`
- `updated_at`

### Product

- `category`, ForeignKey auf `ProductCategory`
- `name`
- `slug`, eindeutig
- `short_description`, optional
- `description`, optional
- `collection_name`, optional
- `product_type`: `nail_polish`, `gel`, `care`, `accessory`, `set`, `other`
- `visibility`: `public`, `b2c_only`, `b2b_only`, `hidden`
- `is_active`, Standard `True`
- `is_featured`, Standard `False`
- `created_at`
- `updated_at`

Sichtbarkeitslogik:

- `public`: sichtbar fuer B2C und B2B
- `b2c_only`: sichtbar fuer B2C
- `b2b_only`: sichtbar fuer B2B
- `hidden`: nicht sichtbar im oeffentlichen Shop

Methoden/Properties:

- `is_visible_for_b2c`
- `is_visible_for_b2b`

### ProductVariant

- `product`, ForeignKey auf `Product`
- `name`
- `sku`, optional, eindeutig falls gesetzt
- `color_name`, optional
- `color_code`, optional
- `finish`, optional
- `size_label`, optional
- `is_default`, Standard `False`
- `is_active`, Standard `True`
- `sort_order`, Standard `0`
- `created_at`
- `updated_at`

### ProductImage

- `product`, ForeignKey auf `Product`
- `variant`, optionaler ForeignKey auf `ProductVariant`
- `image`, FileField mit Uploadpfad `products/`
- `alt_text`, optional
- `sort_order`, Standard `0`
- `is_primary`, Standard `False`
- `created_at`
- `updated_at`

Keine Preisfelder, keine Lagerbestandslogik, keine Checkout-Logik, keine Galerie-Logik und keine Videos in diesem Modulstand.

Catalog ist nach Arbeitsblock 03.1 `frozen`, aber nicht locked. Preise kommen spaeter im Modul `pricing`, Warenkorb kommt spaeter im Modul `cart`, Bestellungen kommen spaeter im Modul `orders`.

## Pricing

### ProductPrice

- `product`, ForeignKey auf `catalog.Product`
- `variant`, optionaler ForeignKey auf `catalog.ProductVariant`
- `customer_group`: `b2c` oder `b2b`
- `amount`, Dezimalbetrag
- `currency`, Standard `EUR`
- `tax_rate`, Standard `19.00`
- `price_includes_tax`, Standard `True`
- `valid_from`, optional
- `valid_until`, optional
- `is_active`, Standard `True`
- `created_at`
- `updated_at`

Regeln:

- `amount` darf nicht negativ sein.
- `tax_rate` darf nicht negativ sein.
- `valid_until` darf nicht vor `valid_from` liegen.
- Wenn `variant` gesetzt ist, muss sie zum angegebenen `product` gehoeren.
- Preise bleiben im Modul `pricing` und werden nicht in `catalog.Product` oder `catalog.ProductVariant` gespeichert.

Preisservice:

- `get_active_price(product, customer_group, variant=None, at=None)`
- `build_price_snapshot(price)`

Snapshot-Vorbereitung fuer spaetere Bestellungen:

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

Noch keine Warenkorb-, Checkout-, Bestell-, Payment- oder Versandlogik.

Pricing ist nach Arbeitsblock 04.1 `frozen`, aber nicht locked. Warenkorb kommt spaeter im Modul `cart`, Bestellungen kommen spaeter im Modul `orders`, Payment kommt spaeter im Modul `payments`.

## Cart

### Cart

- `user`, optionaler ForeignKey auf `accounts.User`
- `session_key`, optionales `CharField(max_length=80)` fuer anonyme Warenkoerbe
- `customer_group`: `b2c` oder `b2b`, Standard `b2c`
- `status`: `active`, `converted`, `abandoned`, Standard `active`
- `currency`, Standard `EUR`
- `created_at`
- `updated_at`

Regeln:

- `user` ODER `session_key` muss vorhanden sein.
- Pro `user` darf hoechstens ein aktiver Warenkorb existieren.
- Pro `session_key` darf hoechstens ein aktiver Warenkorb existieren.

### CartItem

- `cart`, ForeignKey auf `Cart`
- `product`, ForeignKey auf `catalog.Product`
- `variant`, optionaler ForeignKey auf `catalog.ProductVariant`
- `quantity`, `PositiveIntegerField`, Standard `1`
- `created_at`
- `updated_at`

Regeln:

- `quantity` muss groesser 0 sein.
- Wenn `variant` gesetzt ist, muss sie zum angegebenen `product` gehoeren.
- Kombination `cart`/`product`/`variant` ist eindeutig.
- Keine Preisfelder dauerhaft im `CartItem`. Aktuelle Preise kommen aus `pricing.services.get_active_price`.
- Keine Order-Snapshots im `CartItem`. Finale Snapshots kommen spaeter in `orders`.

Cart-Services nutzen den `pricing`-Service. Bestellungen, Checkout, Payment und Versand bleiben spaeteren Modulen vorbehalten.

Cart ist nach Arbeitsblock 05.1 `frozen`, aber nicht locked. Bestellungen kommen spaeter im Modul `orders`, Checkout folgt spaeter, Payment kommt spaeter im Modul `payments`, Versand kommt spaeter im Modul `shipping`.

## Orders

### Order

Bestellungsdatensatz mit echten Preis- und Adress-Snapshots.

Wichtige Felder:

- `order_number`, CharField unique max_length=32
- `user`, ForeignKey auf `settings.AUTH_USER_MODEL`
- `cart`, optionaler ForeignKey auf `cart.Cart`, nullable
- `customer_group`: `b2c` oder `b2b`, Standard `b2c`
- `status`: `draft`, `placed`, `cancelled`, `completed`, Standard `draft`
- `currency`, Standard `EUR`
- `subtotal_amount`, DecimalField
- `total_amount`, DecimalField
- `item_count`, PositiveIntegerField
- `billing_full_name`, `billing_company`, `billing_street`, `billing_postal_code`, `billing_city`, `billing_country` (Standard `DE`)
- `shipping_full_name`, `shipping_company`, `shipping_street`, `shipping_postal_code`, `shipping_city`, `shipping_country` (Standard `DE`)
- `placed_at`, optional
- `cancelled_at`, optional
- `created_at`
- `updated_at`

Regeln:

- `order_number` ist eindeutig und wird mit `generate_order_number()` erzeugt.
- `user` ist Pflicht.
- `subtotal_amount`, `total_amount`, `item_count` duerfen nicht negativ sein.
- Adress-Snapshots speichern die Bestell-Adressen dauerhaft; spaetere Aenderungen an Customer-Adressen aendern bestehende Orders nicht.
- `placed_at` wird beim Order-Status `placed` gesetzt.
- `cancelled_at` wird beim Cancel gesetzt.

### OrderItem

Bestellposition mit vollstaendigen Preis- und Produkt-Snapshots.

Wichtige Felder:

- `order`, ForeignKey auf `Order`
- `product`, optionaler ForeignKey auf `catalog.Product`, null=True
- `variant`, optionaler ForeignKey auf `catalog.ProductVariant`, null=True
- `price`, optionaler ForeignKey auf `pricing.ProductPrice`, null=True
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
- `currency`, Standard `EUR`
- `tax_rate`, DecimalField, Standard `0.00`
- `price_includes_tax`, BooleanField, Standard True
- `created_at`
- `updated_at`

Regeln:

- Snapshot-Felder (`product_id_snapshot`, `variant_id_snapshot`, `price_id_snapshot`, `product_name`, `variant_name`, `sku`) sind Pflicht und veraendernde sich nicht, wenn spaeter das Produkt, die Variante oder der Preis aktualisiert werden.
- `quantity` muss groesser 0 sein.
- `unit_amount`, `line_total` duerfen nicht negativ sein.
- Die Foreign Keys (`product`, `variant`, `price`) sind optional und dienen nur zur Referenzierung; die Snapshots sind die autoritative Quelle.

### Order-Services

Datei: `backend/apps/orders/services.py`

Bereitgestellt:

- `OrderError` Exception
- `generate_order_number()`: erzeugt eindeutige Bestellnummern im Format `AWN-YYYYMMDD-XXXXXX`
- `build_address_snapshot(address)`: erzeugt ein Dict mit Adressdaten; bei None werden Defaults (leere Werte, Land `DE`) zurueckgegeben
- `create_order_from_cart(cart, user=None, billing_address=None, shipping_address=None, status='placed')`: erstellt Order aus Cart mit vollstaendigen Snapshots, setzt `cart.status` auf `converted`, nutzt `pricing`-Service
- `recalculate_order_totals(order)`: berechnet Summen aus OrderItems neu
- `cancel_order(order)`: setzt Status auf `cancelled` und `cancelled_at`

### Grenzen

Orders speichert Bestellungen, Positionen und Snapshots. Es baut NICHT:

- Checkout
- Payment
- Versand
- Rechnungen
- E-Mail
- Legal-/Consent-Integration
- Frontend

Orders ist nach Arbeitsblock 06.1 `frozen`, aber nicht locked. Aenderungen nur mit dokumentiertem Grund, Impact-Pruefung und Regressionstest.

Checkout, Payment, Versand, Rechnungen, E-Mail und Legal-/Consent-Integration kommen in spaeteren Modulen.

## Legal

### LegalDocument

Rechtstexte und deren Versionen mit Versionskontrolle und Aktivierungsstatus.

Wichtige Felder:

- `document_type`: `imprint`, `privacy_policy`, `terms_b2c`, `terms_b2b`, `withdrawal_b2c`, `shipping_info`, `payment_info`, `cookie_policy`, `other`
- `title`, CharField
- `target_group`: `all`, `b2c`, `b2b` - Standard `all`
- `slug`, CharField unique
- `description`, optional TextField
- `is_required`, BooleanField, Standard True
- `created_at`
- `updated_at`

Ordering: by `document_type`, `target_group`, `title`

Szenario: Verwaltung von Rechtstexten wie Impressum, Datenschutz, AGB, Widerrufsrecht, etc. Unterschiedliche Versionen für B2C, B2B und allgemein.

### LegalDocumentVersion

Versionen von Rechtstexten mit Aktivierungs- und Archivierungsverwaltung.

Wichtige Felder:

- `document`, ForeignKey auf `LegalDocument` CASCADE
- `version`, CharField max_length=32
- `status`: `draft`, `active`, `archived`
- `content`, TextField (Rechtstext)
- `summary`, optional TextField
- `effective_from`, optional DateTimeField
- `activated_at`, optional DateTimeField
- `archived_at`, optional DateTimeField
- `created_by`, optional ForeignKey auf `settings.AUTH_USER_MODEL`
- `activated_by`, optional ForeignKey auf `settings.AUTH_USER_MODEL`
- `created_at`
- `updated_at`

Constraints:

- UniqueConstraint on (`document`, `version`)
- Clean(): wenn Status `active`, dann muss `content` non-empty sein

Regeln:

- Pro `LegalDocument` darf maximal eine Version `active` sein
- Nur aktive Versionen sind in der Website sichtbar
- Versionsverlauf ist zeitlich nachvollziehbar

### Legal-Services

Datei: `backend/apps/legal/services.py`

Bereitgestellt:

- `LegalDocumentError` Exception
- `get_active_document_version(document_type, target_group="all")`: Holt aktive Version, fallback zu `target_group="all"` falls spezifische nicht vorhanden, wirft LegalDocumentError wenn keine gefunden
- `activate_document_version(version, user=None)`: @transaction.atomic, archiviert alle anderen aktiven Versionen des Dokuments, setzt diese Version aktiv, setzt `activated_at` und `activated_by`
- `archive_document_version(version, user=None)`: Setzt Status auf `archived`, setzt `archived_at`

Grenzen: Legal speichert Rechtstexte und Versionen. Es baut NICHT:

- Frontend-Rendering
- Website-Integration
- Checkbox-Handling
- E-Mail-Templates
- Checkout-Integration

Legal ist nach Arbeitsblock 07.1 `frozen`. Review bestanden. Aenderungen nur mit dokumentiertem Grund, Impact-Pruefung und Regressionstest.

## Consent

### ConsentCategory

Kategorien von Benutzerzustimmungen (z.B. notwendig, Analytics, Marketing).

Wichtige Felder:

- `key`, CharField max_length=80 unique (empfohlen: `necessary`, `analytics`, `marketing`, `preferences`)
- `name`, CharField
- `description`, optional TextField
- `is_required`, BooleanField, Standard False - wenn True, dann gilt Zustimmung auch ohne explizite Bestätigung
- `is_active`, BooleanField, Standard True
- `sort_order`, IntegerField, Standard 0
- `created_at`
- `updated_at`

Ordering: by `sort_order`, `key`

Szenario: Definition welche Consent-Kategorien auf der Website verfügbar sind (z.B. "Analytics aktiv?" "Marketing-Cookies aktiv?")

### ConsentRecord

Einzelne Zustimmungs-Einträge von Benutzern oder anonymen Sessions.

Wichtige Felder:

- `user`, optional ForeignKey auf `settings.AUTH_USER_MODEL`
- `session_key`, optional CharField max_length=80
- `category`, ForeignKey auf `ConsentCategory`
- `granted`, BooleanField - True wenn Zustimmung erteilt, False wenn abgelehnt
- `consent_version`, CharField default="v1" - Zur Versionierung von Consent-Anforderungen
- `source`: `banner`, `account`, `admin`, `system` - Wo kam die Zustimmung her?
- `ip_address`, optional GenericIPAddressField
- `user_agent`, optional TextField
- `created_at`

Constraints:

- CheckConstraint: user ODER session_key muss vorhanden sein
- Clean(): Validiert dass user oder session_key vorhanden

__str__: Zeigt Format "user.email - category.key - Granted/Denied"

Regeln:

- Pro `user` oder `session_key` kann es mehrere ConsentRecords geben (für verschiedene Kategorien)
- Neueste ConsentRecord pro Kategorie ist die aktuelle Einstellung
- Anonyme Sessionen werden per `session_key` (Django-Session-ID-Format) getrackt

### Consent-Services

Datei: `backend/apps/consent/services.py`

Bereitgestellt:

- `ConsentError` Exception
- `record_consent(category, granted, user=None, session_key=None, source="banner", consent_version="v1", ip_address=None, user_agent=None)`: Erstellt neue ConsentRecord, akzeptiert ConsentCategory-Instanz oder `category_key` String, validiert user oder session_key vorhanden
- `get_latest_consent(user=None, session_key=None)`: Gibt Dict mit neuester ConsentRecord pro Kategorie zurück
- `has_consent(category_key, user=None, session_key=None)`: Gibt True zurück wenn Zustimmung erteilt, False wenn abgelehnt. Für erforderliche Kategorien ohne Record: gibt True zurück (implizite Zustimmung)

Grenzen: Consent speichert Zustimmungs-Einträge. Es baut NICHT:

- Frontend-Banner
- Cookie-Richtlinie-Tracking
- Automatisches GDPR-Auditing
- E-Mail-Benachrichtigungen
- Integration mit Payment/Checkout
- Automatisches Cookie-Löschen

Consent ist nach Arbeitsblock 07.1 `frozen`. Review bestanden. Aenderungen nur mit dokumentiertem Grund, Impact-Pruefung und Regressionstest.

## Auditlog

### AuditLogEntry

Audit-Log-Einträge für kritische Systemaktionen und Benutzeraktionen. Dient als unveränderliches Audit-Trail für Compliance und Debugging.

Wichtige Felder:

- `actor`, optional ForeignKey auf `settings.AUTH_USER_MODEL` - Wer hat das Ereignis ausgelöst (z.B. Admin-Benutzer)
- `action`, CharField mit 13 Choices: `created`, `updated`, `deleted`, `status_changed`, `activated`, `archived`, `approved`, `rejected`, `cancelled`, `converted`, `login`, `logout`, `system` - Die durchgeführte Aktion
- `entity_type`, CharField max_length=120 - Typ der betroffenen Entität (z.B. "orders.Order", "business.BusinessProfile")
- `entity_id`, optional CharField max_length=120 - ID der betroffenen Entität
- `entity_repr`, optional CharField max_length=255 - Lesbare Repräsentation (gekürzt auf 255 Zeichen)
- `message`, TextField (optional default "") - Zusätzlicher Kontext oder Grund
- `changes`, JSONField (default={}) - Format: {"field_name": {"old": old_value, "new": new_value}} für Änderungsfelder
- `metadata`, JSONField (default={}) - Strukturierte Zusatzdaten (z.B. approval_reason, price_category, batch_id)
- `ip_address`, optional GenericIPAddressField - IPv4/IPv6 Adresse der HTTP-Anfrage
- `user_agent`, optional TextField - Browser/Client-Informationen
- `created_at`, DateTimeField (auto_now_add) - Zeitstempel (UTC, unveränderlich)

Ordering: by `-created_at` (Neueste zuerst)

Indizes: auf [action], [entity_type], [-created_at]

Szenario: Protokollierung aller kritischen Systemaktionen für Compliance, Debugging, und Audit-Trails:
- Admin-Änderungen (Produktpreise aktualisiert, Benutzer-Status geändert, Business-Genehmigung erteilt)
- Geschäfts-Events (Bestellung erstellt, Status geändert, storniert)
- Zugriff/Auth (Benutzer angemeldet, abgemeldet, privilegierte Aktion)
- Compliance (Rechtsdokument aktiviert, Versione gewechselt)

__str__: Zeigt Format "{action} on {entity_type} ({entity_id}) at {created_at}"

Constraints:

- `actor` ist optional (System-Events haben actor=None)
- `action` ist Pflicht, leerer String nicht erlaubt
- `entity_type` ist Pflicht
- `entity_id` und `entity_repr` sind optional (für Compliance wo Entität gelöscht wurde)

### Auditlog-Services

Datei: `backend/apps/auditlog/services.py`

Bereitgestellt:

- `AuditLogError` Exception - Geworfen bei Validierungsfehlern (fehlende action oder entity_type)
- `create_audit_log(actor=None, action='system', entity=None, entity_type=None, entity_id=None, entity_repr=None, message='', changes=None, metadata=None, ip_address=None, user_agent=None)`: Erstellt Audit-Log-Eintrag. Wenn Django-Modell-Instanz als `entity` übergeben wird, auto-detected `entity_type` (app_label.model_name), `entity_id` (pk), `entity_repr` (str()[:255]). Wenn `entity` nicht übergeben wird, muss `entity_type` manuell gesetzt sein.
- `build_change_set(before: dict, after: dict, ignored_fields=None)`: Vergleicht before/after Dicts und gibt nur geänderte Felder zurück. Format: {"field": {"old": val1, "new": val2}}. Ignoriert Felder in `ignored_fields` Liste (z.B. ['password', 'token', 'updated_at'])

Grenzen: Auditlog speichert Audit-Logs und stellt Services bereit. Es baut NICHT:

- Automatische Signals oder Hooks (Services müssen manuell aufgerufen werden)
- Automatische Integration in bestehende Module
- Passwort/Token-Protokollierung (Security by Design)
- Automation von Compliance-Reports
- Integration mit Payment/Shipping/Checkout
- Frontend-Audit-Interface (nur Django Admin)

Auditlog ist nach Arbeitsblock 08 `tested`. Status: offen für Freeze-Decision in Arbeitsblock 08.1. Keine automatische Integration in frozen Module in diesem Arbeitsblock - Integration folgt nach Freeze-Decision.

## Shipping

Modul: `apps.shipping`

Status nach Arbeitsblock 09.1: **frozen**

### ShippingZone

Modell: `apps.shipping.ShippingZone`

- `name`: CharField(120) - Name der Versandzone (z.B. "Deutschland", "EU", "International")
- `code`: CharField(32, unique) - Eindeutiger Code (z.B. "DE", "EU", "INT")
- `countries`: ArrayField(CharField(max_length=3)) - ISO-Ländercodes als Liste (z.B. ["DE", "AT", "CH"])
- `is_active`: BooleanField(default=True) - Zone aktiv für Versandberechnung
- `sort_order`: PositiveIntegerField(default=0) - Sortierreihenfolge
- `created_at`: DateTimeField(auto_now_add=True)
- `updated_at`: DateTimeField(auto_now=True)

Constraints:

- `code` ist eindeutig
- Ordering: [sort_order, name]
- Indizes: [code], [is_active]

### ShippingMethod

Modell: `apps.shipping.ShippingMethod`

- `zone`: ForeignKey(ShippingZone, on_delete=PROTECT) - Versandzone dieser Methode
- `name`: CharField(120) - Name der Versandmethode (z.B. "Standardversand", "Expressversand")
- `code`: CharField(64, unique) - Eindeutiger Code (z.B. "standard_de", "express_de")
- `customer_group`: CharField(10, choices=['all', 'b2c', 'b2b'], default='all') - Kundengruppe
- `base_price`: DecimalField(10,2, default=0.00) - Basis-Versandkosten
- `currency`: CharField(3, default='EUR') - Währung (ISO 4217)
- `estimated_min_days`: PositiveIntegerField(null=True, blank=True) - Min. geschätzte Liefertage
- `estimated_max_days`: PositiveIntegerField(null=True, blank=True) - Max. geschätzte Liefertage
- `is_active`: BooleanField(default=True) - Methode aktiv
- `sort_order`: PositiveIntegerField(default=0) - Sortierreihenfolge
- `created_at`: DateTimeField(auto_now_add=True)
- `updated_at`: DateTimeField(auto_now=True)

Constraints:

- `code` ist eindeutig
- `base_price >= 0` (Check-Constraint)
- `estimated_max_days >= estimated_min_days` wenn beide gesetzt (Check-Constraint)
- `zone` ist mit PROTECT geschützt (Zone kann nicht gelöscht werden, wenn Methoden existieren)
- `customer_group='all'` bedeutet für B2C und B2B nutzbar
- Ordering: [sort_order, name]
- Indizes: [zone, is_active], [code], [customer_group]

### ShippingRateSnapshot

Modell: `apps.shipping.ShippingRateSnapshot`

Technische Snapshot-Vorbereitung für spätere Orders/Checkout. Speichert stabile Momentaufnahme einer Versandmethode und deren Kosten. Snapshots sind eigenständig stabil und werden später beim Checkout und in Orders referenziert.

- `method`: ForeignKey(ShippingMethod, on_delete=SET_NULL, null=True, blank=True) - Referenz zur Methode (optional)
- `method_code`: CharField(64) - Code der Versandmethode (Snapshot, unveränderlich)
- `method_name`: CharField(120) - Name der Versandmethode (Snapshot, unveränderlich)
- `zone_code`: CharField(32) - Code der Versandzone (Snapshot, unveränderlich)
- `zone_name`: CharField(120) - Name der Versandzone (Snapshot, unveränderlich)
- `customer_group`: CharField(10, choices=['b2c', 'b2b']) - Kundengruppe bei Snapshot-Erstellung
- `amount`: DecimalField(10,2) - Versandkosten-Betrag des Snapshots
- `currency`: CharField(3, default='EUR') - Währung
- `estimated_min_days`: PositiveIntegerField(null=True, blank=True) - Min. Liefertage (Snapshot)
- `estimated_max_days`: PositiveIntegerField(null=True, blank=True) - Max. Liefertage (Snapshot)
- `created_at`: DateTimeField(auto_now_add=True)

Constraints:

- `amount >= 0` (Check-Constraint)
- `method` kann NULL sein (Methoden-Löschung) – aber method_code/method_name bleiben erhalten
- Admin-Permissions: read-only (has_add=False, has_change=False, has_delete=False, Audit-Trail)
- Ordering: [-created_at] (Neueste zuerst)
- Indizes: [method_code], [customer_group], [-created_at]

### Shipping-Services

Datei: `backend/apps/shipping/services.py`

Bereitgestellt:

- `ShippingError` Exception - Geworfen bei Validierungsfehlern
- `get_available_shipping_methods(country_code="DE", customer_group="b2c")`: Findet verfügbare Versandmethoden für ein Land und Kundengruppe. Filtert aktive Zonen mit country_code, filtert aktive Methoden für Kundengruppe (all oder exakt), sortiert nach sort_order/name. QuerySet-Rückgabewert.
- `get_shipping_method(code, customer_group="b2c", country_code="DE")`: Findet spezifische Versandmethode. Prüft Kundengruppe-Zugang, prüft Zone/Land-Zugang, wirft ShippingError bei Fehler. ShippingMethod-Rückgabewert.
- `calculate_shipping_amount(method)`: Berechnet Versandkosten. Aktuell einfache Rückgabe von method.base_price (keine Gewichtslogik, Warenwertlogik, Rabatte, Versandkostenfrei-Regeln in diesem Block).
- `build_shipping_snapshot(method, customer_group="b2c")`: Erstellt stabilen Snapshot mit denormalisierten method/zone-Daten. Speichert in DB und gibt ShippingRateSnapshot zurück.

Grenzen: Shipping speichert Versandzonen und -methoden und stellt Services bereit. Es baut NICHT:

- DHL/Hermes/Warenpost-Anbindung
- Label-Erstellung
- Tracking-API
- Checkout-Integration
- Order-Integration
- Payment-Logik
- Rechnungslogik
- E-Mail-Versand
- automatische Signals/Hooks
- gewichtsabhängige Preisberechnung
- warenwertabhängige Preisberechnung
- Rabatte/Versandkostenfrei-Regeln

Shipping ist nach Arbeitsblock 09.1 `frozen`. Änderungen nur mit dokumentiertem Grund, Impact-Prüfung und Regressionstest.
## Payments

### PaymentMethod

Zahlungsart-Konfiguration.

Wichtige Felder:

- `name`, CharField max_length=120 - Anzeigename
- `code`, CharField max_length=64 unique - Eindeutiger Code
- `provider`, CharField choices - Klassifikation: `manual`, `bank_transfer`, `invoice`, `paypal`, `stripe`, `other`
- `customer_group`, CharField choices - Verfügbarkeit: `all` (B2C+B2B), `b2c`, `b2b`
- `description`, optional TextField
- `is_active`, BooleanField Standard True
- `sort_order`, PositiveIntegerField Standard 0
- `created_at`
- `updated_at`

Ordering: by `sort_order`, `name`

Szenario: Definition verfügbarer Zahlungsarten im Shop (z.B. "Vorkasse", "Rechnung", später "PayPal")

### PaymentTransaction

Zahlungstransaktion (technischer Datensatz für Checkout/Order).

Wichtige Felder:

- `order`, optional ForeignKey auf `orders.Order` (für spätere Checkout-Integration)
- `method`, optional ForeignKey auf `PaymentMethod`
- `payment_reference`, optional CharField max_length=120 - Externe Referenznummer
- `provider_reference`, optional CharField max_length=255 - Provider-Referenznummer
- `status`, CharField choices - `pending`, `authorized`, `paid`, `failed`, `cancelled`, `refunded`
- `amount`, DecimalField max_digits=10 decimal_places=2 - Zahlungsbetrag >= 0
- `currency`, CharField max_length=3 Standard "EUR"
- `customer_group`, CharField choices - `b2c`, `b2b`
- `provider`, CharField max_length=64 Standard "manual" - Provider-Klassifikation
- `raw_response`, JSONField Standard {} - Speichert nur unkritische Daten, KEINE Kreditkartendaten
- `metadata`, JSONField Standard {} - Speichert nur unkritische Metadaten
- `created_at`
- `updated_at`
- `paid_at`, optional DateTimeField - Zeitpunkt Bezahlung
- `cancelled_at`, optional DateTimeField - Zeitpunkt Stornierung
- `refunded_at`, optional DateTimeField - Zeitpunkt Erstattung

Constraints:

- CheckConstraint: amount >= 0
- amount ist erforderlich bei Erstellung

Regeln:

- `order` kann null sein (Transaktionen entstehen auch vor Order-Erstellung)
- `raw_response` und `metadata` dürfen KEINE Kreditkartendaten, Secrets oder sensiblen Daten enthalten
- Neuester Status ist aktuell
- Sortierung: nach -created_at (neueste zuerst)

Szenario: Alle Zahlungsvorgänge werden hier dokumentiert, Status-Änderungen getrackt

### PaymentMethodSnapshot

Snapshot einer Zahlungsart (denormalisiert für historische Konsistenz).

Wichtige Felder:

- `method`, optional ForeignKey auf `PaymentMethod` (denormalisiert)
- `method_code`, CharField max_length=64
- `method_name`, CharField max_length=120
- `provider`, CharField max_length=64
- `customer_group`, CharField choices - `b2c`, `b2b`
- `created_at`

Regeln:

- Snapshot ist eigenständig stabil (wird nicht mit PaymentMethod-Änderungen synchronisiert)
- Wird für Orders/Checkout verwendet um historische Zahlungsart-Informationen zu bewahren

Szenario: Snapshot-Vorbereitung für spätere Orders/Checkout Integration

### Payment-Services

Datei: `backend/apps/payments/services.py`

Bereitgestellt:

- `PaymentError` Exception
- `get_available_payment_methods(customer_group="b2c")`: Findet aktive Methoden für Kundengruppe (filtert `customer_group="all"` oder exakt), sortiert nach sort_order+name, wirft PaymentError bei ungültiger customer_group
- `get_payment_method(code, customer_group="b2c")`: Sucht aktive Methode nach code, prüft Kundengruppen-Kompatibilität, wirft PaymentError bei nicht gefunden oder ungültiger Kundengruppe
- `build_payment_method_snapshot(method, customer_group="b2c")`: Erstellt dict mit method_id, method_code, method_name, provider, customer_group (keine externe API)
- `create_payment_transaction(order=None, method=None, amount=None, currency="EUR", customer_group="b2c", payment_reference="", provider_reference="", metadata=None)`: Erstellt Transaction ohne externe API, amount erforderlich und >= 0, method optional (provider übernommen), wirft PaymentError bei ungültigen Daten
- `mark_payment_paid(transaction)`: Setzt status="paid", paid_at=now()
- `mark_payment_failed(transaction)`: Setzt status="failed"
- `cancel_payment(transaction)`: Setzt status="cancelled", cancelled_at=now()
- `refund_payment(transaction)`: Setzt status="refunded", refunded_at=now()

Grenzen: Payments speichert Zahlungsarten und Transaktionen. Es baut NICHT:

- echte Zahlungsanbieter-Anbindung (Stripe, PayPal, Klarna, Sofort, Bank-API)
- Webhooks oder externe Callbacks
- Kreditkartendatenspeicherung
- PCI-DSS-Compliance-Logik
- Checkout-Integration
- Order-Integration
- Rechnungslogik
- E-Mail-Versand
- automatische Signals/Hooks

Payments ist nach Arbeitsblock 10.1 `frozen` (nicht locked). Änderungen nur mit dokumentiertem Grund, Impact-Prüfung und Regressionstest.

## Checkout

### CheckoutSession

Technische Sitzung für einen Checkout-Vorgang (Arbeitsblock 11).

Felder:

- `user`, optional ForeignKey auf `settings.AUTH_USER_MODEL`
- `cart`, ForeignKey auf `cart.Cart` (Pflicht, PROTECT)
- `status`: choices: started, validated, order_created, cancelled, expired (default: started)
- `customer_group`: choices: b2c, b2b (default: b2c)
- `currency`: CharField (3, default: EUR)
- `shipping_method`, optional ForeignKey auf `shipping.ShippingMethod`
- `shipping_snapshot`: JSONField (Snapshot, keine Secrets)
- `shipping_amount`: DecimalField(10,2, >= 0)
- `payment_method`, optional ForeignKey auf `payments.PaymentMethod`
- `payment_snapshot`: JSONField (Snapshot, keine Secrets)
- `cart_subtotal`: DecimalField(10,2, >= 0)
- `order_total`: DecimalField(10,2, >= 0)
- `item_count`: PositiveIntegerField (>= 0)
- `legal_snapshot`: JSONField (Snapshot Rechtsvereinbarungen)
- `consent_snapshot`: JSONField (Snapshot Zustimmungen)
- `order`, optional OneToOneField auf `orders.Order`
- `started_at`, `validated_at`, `order_created_at`, `cancelled_at`, `expires_at`: DateTimeField
- `created_at`, `updated_at`: DateTimeField

Constraints:

- CheckConstraint: shipping_amount >= 0
- CheckConstraint: cart_subtotal >= 0
- CheckConstraint: order_total >= 0
- CheckConstraint: item_count >= 0

Regeln:

- `cart` ist Pflicht
- `user` ist optional
- Snapshots speichern keine Secrets
- Ordering: [-updated_at]
- Indizes: [status, -updated_at], [user, -created_at], [cart]

### CheckoutEvent

Einfache technische Ereignisse im Checkout-Ablauf (nicht Ersatz für auditlog).

Felder:

- `checkout`: ForeignKey auf CheckoutSession (CASCADE)
- `event_type`: choices: started, validated, shipping_selected, payment_selected, legal_checked, consent_checked, order_created, cancelled, error
- `message`: TextField (optional)
- `metadata`: JSONField (keine Secrets)
- `created_at`: DateTimeField

Regeln:

- `checkout` ist Pflicht
- Ordering: [-created_at]
- Indizes: [checkout, -created_at], [event_type]

### Checkout-Services

Datei: `backend/apps/checkout/services.py`

Bereitgestellt:

- `CheckoutError` Exception
- `start_checkout(cart, user, expires_at)`: Erstellt CheckoutSession mit status started
- `select_shipping_method(checkout, shipping_method_code, country_code)`: Nutzt shipping.services, setzt Methode, Snapshot, Betrag
- `select_payment_method(checkout, payment_method_code)`: Nutzt payments.services, setzt Methode, Snapshot
- `build_legal_snapshot(customer_group)`: Nutzt legal.services, wirft CheckoutError bei fehlenden Dokumenten
- `build_consent_snapshot(user, session_key)`: Nutzt consent.services, gibt dict zurück
- `validate_checkout(checkout)`: Prüft Cart/Shipping/Payment, berechnet Summen, setzt status validated
- `create_order_from_checkout(checkout)`: Nutzt orders.services, erzeugt Order (keine Modelländerungen in frozen Orders)
- `cancel_checkout(checkout, message)`: Setzt status cancelled
- `log_checkout_event(checkout, event_type, message, metadata)`: Erstellt CheckoutEvent

Grenzen: Checkout speichert Sitzungen und Events. Es baut NICHT:

- Frontend-Oberflächenlogik
- echte Payment-Ausführung
- echte Versand-Ausführung
- Rechnungslogik
- E-Mail-Versand
- Webhooks
- Checkout-APIs für externe Clients

Checkout ist nach Arbeitsblock 11 `tested` (noch nicht frozen). Review/Freeze folgt in Arbeitsblock 11.1. Änderungen nur mit dokumentiertem Grund, Impact-Prüfung und Regressionstest.

