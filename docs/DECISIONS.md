# DECISIONS

## Feste Projektentscheidungen

### Entscheidung 1

Projektordner ist:
`C:\Users\mickh\Desktop\alice-wondernails`

### Entscheidung 2

Alle Arbeiten ausschliesslich innerhalb dieses Ordners.

### Entscheidung 3

Farbkatalog Nr. 1 ist aktuelle Arbeitsbasis.

### Entscheidung 4

Rose-Gold-Variante bleibt Reserve, aber nicht Hauptbasis.

### Entscheidung 5

Modul 1 ist Vorstellungsseite + Early Access/Kontakt, kein kompletter Shop.

### Entscheidung 6

Mehrere Galeriebilder und mehrere Videos werden eingeplant.

### Entscheidung 7

Platzhalter muessen sprechend sein.
Keine Lorem-Ipsum-Blindtexte.

### Entscheidung 8

Jeder spaetere Auftrag arbeitet mit einem klar abgegrenzten Masterprompt.

### Entscheidung 9

`docs/PROGRESS.md` muss vor jedem Arbeitsschritt gelesen und nach jedem Arbeitsschritt aktualisiert werden.

## Entscheidung: Django + PostgreSQL + modularer Monolith

### Datum
2026-05-04

### Entscheidung
Das Projekt wird als Django-basierter modularer Monolith mit PostgreSQL aufgebaut.

### Begründung
- große Shopstruktur
- Admin-Funktionen nötig
- User/Rollen nötig
- PostgreSQL lokal nahe an späterer Online-Version
- Module sollen getrennt, aber nicht als Microservices gebaut werden
- stabile Modul-Freeze-Regel

### Konsequenzen
- Backend-first
- klare Modulgrenzen
- zentrale Datenbank
- zentrale Tests
- spätere Austauschbarkeit über Adapter/Services
- Module werden nach erfolgreichem Test eingefroren

## Entscheidung: Custom User Model ab Arbeitsblock 02

### Datum
2026-05-05

### Entscheidung
Das Projekt nutzt ab Arbeitsblock 02 ein eigenes User-Modell:

`accounts.User`

Basis ist `django.contrib.auth.models.AbstractUser`.

### Begruendung
- Das Projekt braucht dauerhaft B2C-/B2B-Statuslogik.
- Rollen, Profile und spaetere Account-Erweiterungen sollen auf einem stabilen User-Fundament aufbauen.
- Ein Custom User Model muss am Projektanfang gesetzt werden, bevor weitere Fachmodule darauf verweisen.

### Konsequenzen
- `AUTH_USER_MODEL = 'accounts.User'`
- `email` ist eindeutig.
- `customer_status` bildet `consumer`, `business_pending` und `business_approved` ab.
- Staff/Admin/Superadmin bleiben ueber Django-Felder wie `is_staff` und `is_superuser` abbildbar.

## Entscheidung: Lokaler Entwicklungsdatenbank-Reset fuer Custom User Model

### Datum
2026-05-05

### Entscheidung
Die lokale Projekt-Datenbank `alice_wonder_nails` wurde fuer den sauberen Start mit Custom User Model kontrolliert neu initialisiert.

### Begruendung
- Vor Arbeitsblock 02 waren bereits Standard-Django-Migrationen ohne Custom User Model gelaufen.
- Ein nachtraeglicher Wechsel auf `AUTH_USER_MODEL` ist auf einer bereits migrierten Datenbank riskant.
- Die Preflight-Pruefung ergab vorhandene Django-Tabellen, aber keine produktiven Userdaten.

### Grenzen
- Reset nur fuer die lokale Projekt-Datenbank `alice_wonder_nails`.
- Keine anderen Datenbanken angefasst.
- Keine Secrets dokumentiert.
- Kein produktiver Datenbestand geloescht.

### Konsequenzen
- Alle Migrationen wurden danach vollstaendig neu ausgefuehrt.
- `accounts.User` ist jetzt die saubere User-Basis.
- Der lokale Projektuser hat `CREATEDB`, damit pytest-django die Testdatenbank erstellen kann.

## Entscheidung: Freeze accounts, customers und business

### Datum
2026-05-05

### Entscheidung
Die Module `accounts`, `customers` und `business` werden nach Arbeitsblock 02.1 auf Freeze-Status `frozen` gesetzt.

### Begruendung
- Code-Review der Modelle, Admins, App-Konfigurationen, Tests und Migrationen ergab keinen Blocker.
- Keine Shop-, Produkt-, Katalog-, Pricing-, Warenkorb-, Checkout-, Payment- oder Versandlogik wurde eingebaut.
- PostgreSQL-Check, Django-Systemcheck, Migrationen, Migration-Dry-Run und Backend-Pytest sind gruen.

### Konsequenzen
- Die Module sind nicht locked.
- Aenderungen bleiben moeglich, wenn spaetere Module zwingend saubere Schnittstellenanpassungen brauchen.
- Aenderungen brauchen ab jetzt dokumentierten Grund, Impact-Pruefung und Regressionstest.

## Entscheidung: Freeze catalog

### Datum
2026-05-05

### Entscheidung
Das Modul `catalog` wird nach Arbeitsblock 03.1 auf Freeze-Status `frozen` gesetzt.

### Begruendung
- Code-Review der Modelle, Admins, App-Konfiguration, Tests und Migration ergab keinen Blocker.
- Keine Preis-, Warenkorb-, Checkout-, Payment-, Versand-, Review-, Galerie-, Frontend-, Login-, Register- oder E-Mail-Logik wurde eingebaut.
- PostgreSQL-Check, Django-Systemcheck, Migrationen, Migration-Dry-Run und Backend-Pytest sind gruen.

### Konsequenzen
- Das Modul ist nicht locked.
- Aenderungen bleiben moeglich, wenn spaetere Module wie `pricing`, `cart` oder `orders` zwingend saubere Schnittstellenanpassungen brauchen.
- Aenderungen brauchen ab jetzt dokumentierten Grund, Impact-Pruefung und Regressionstest.

## Entscheidung: Kontrollierte Erweiterung des frozen orders-Moduls (Arbeitsblock 12)

### Datum
2026-05-05

### Entscheidung
Das frozen Modul `orders` wird in Arbeitsblock 12 kontrolliert erweitert um:
- `shipping_amount` DecimalField zur Speicherung der finalen Versandkosten
- `shipping_snapshot` JSONField zur Speicherung der Versandmethoden-Metadaten
- `payment_snapshot` JSONField zur Speicherung der Zahlungsmethoden-Metadaten
- `checkout_snapshot` JSONField zur Speicherung von Checkout-Kontext (customer_group, currency, item_count, Summen)

Zusätzlich wird `recalculate_order_totals()` erweitert, um `total_amount = subtotal_amount + shipping_amount` zu berechnen.

Ebenso wird eine neue Funktion `apply_checkout_snapshot_to_order()` hinzugefügt zur Übernahme dieser Daten aus CheckoutSession.

Das checkout-Modul wird ebenfalls kontrolliert angepasst, um diese Snapshots zu übergeben.

### Begründung
- checkout.CheckoutSession speichert Versand-/Zahlungs-Snapshots und die finale Gesamtsumme.
- Nach Order-Erzeugung haben Order und CheckoutSession unterschiedliche Quellen für Versand-/Zahlungsdaten.
- Ein sauberer Shopabschluss erfordert, dass die finale Order alle kaufrelevanten Daten dauerhaft speichert.
- Ohne diese Erweiterung können Order-Abrufgeräte/Reports nicht feststellen, welche Versand-/Zahlungsmethode final gewählt wurde.
- Die Snapshots enthalten keine Secrets und sind nur Metadaten, keine echten Zahlungs-/Versandvorgänge.
- Diese Erweiterung ist eine dokumentierte Ausnahme von der Frozen-Regel, da sie notwendig ist, um Checkout und Order kohärent zu halten.

### Grenzen
- Keine echte Payment-Ausführung.
- Keine echte Versand-Buchung.
- Keine Rechnungslogik.
- Keine E-Mail-Versand.
- Keine Webhook-Integration.
- Keine Anbieter-API-Integration.
- Keine Änderungen an OrderItem oder bestehenden Preis-Snapshots.
- Keine Checkout-FK erzwingen, um zyklische Dependencies zu vermeiden; Snapshots reichen.

### Konsequenzen
- order.Order hat 4 zusätzliche Felder, 1 neue Migration.
- orders.services hat 1 neue Funktion `apply_checkout_snapshot_to_order()`.
- checkout.services setzt diese neue Funktion nach `create_order_from_cart()` ein.
- Neue Tests für Order-Snapshots und Checkout→Order Übernahme.
- Regression-Tests bestätigen, dass bestehende Order-Logik nicht gebrochen ist.
- Impact-Prüfung: Bestandsorders bleiben unverändert (neue Felder default/null).
- Keine Breaking Changes für Clients, die orders-Services direkt aufrufen.

## Entscheidung: Senior-Audit Critical Fixes – Arbeitsblock 13

### Datum
2026-05-05

### Auslöser
Ein Senior Backend Audit wurde durchgeführt und blockt Weiterbau Richtung API/Frontend mit ROT-Befunden:

1. `checkout.services.create_order_from_checkout()` ist nicht vollständig atomar
2. `production.py` besteht `check --deploy` nicht
3. Doku enthält falsche Zukunftsdaten und falsche "Git-Status sauber"-Aussagen

### Entscheidung
Arbeitsblock 13 behebt nur diese kritischen Sofort-Themen, bevor API/Frontend gebaut werden.

Dies ist KEIN Featureblock. Fokus: 4 ROT-Fixes + Admin-Immutability Härtung + Doku-Korrektionen.

### Behobene ROT-Themen

#### 1. Checkout → Order Atomarität
**Problem**: `create_order_from_checkout()` startet Order-Erstellung ohne vollständige transaktionale Absicherung.

**Fix**:
- Gesamte Checkout→Order-Sequenz mit `transaction.atomic()` absichern
- CheckoutSession per `select_for_update()` sperren
- Bei Fehler in Order-Erstellung: kompletter Rollback, keine halben Zuständnisse

**Grenzen**: Keine echte Payment/Versand-Ausführung; nur Snapshot-Transfer und Status-Änderungen sind transaktional.

#### 2. Admin-Immutability für finale Order-Snapshots
**Problem**: OrderAdmin und OrderItemAdmin erlauben Bearbeitung finaler Snapshots und Betragsfelder.

**Fix**:
- Setzen von `readonly_fields` für Order: `order_number`, `subtotal_amount`, `shipping_amount`, `total_amount`, `item_count`, `shipping_snapshot`, `payment_snapshot`, `checkout_snapshot`, Zeitstempel
- Setzen von `readonly_fields` für OrderItem: `product_id_snapshot`, `variant_id_snapshot`, `price_id_snapshot`, `product_name`, `variant_name`, `sku`, `customer_group`, `unit_amount`, `line_total`, `currency`, `tax_rate`, `price_includes_tax`, Zeitstempel

**Grenzen**: Nicht-Snapshot-Felder wie Status können noch ediert werden, falls nötig für Lifecycle-Steuerung.

#### 3. Doku-Fehler korrigieren
**Problem**: README.md, CHANGELOG.md, PROGRESS.md enthalten Zukunftsdaten (2026-05-06, 2026-05-07, 2026-05-08) und falsche Aussagen wie "Git-Status sauber".

**Fix**:
- Zukunftsdaten auf aktuelles Datum korrigieren (2026-05-05 oder rückwärts retrospektiv korrigieren)
- Falsche Git-Status-Aussagen entfernen oder konkretisieren
- Falsche Aussagen wie "Production-Ready" entfernen
- Englische Abschlussberichte aus deutscher Doku entfernen

**Grenzen**: Keine großen Umbauten, nur Fehlerkorrektur.

#### 4. Production-Settings Check & Minimal-Vorbereitung
**Problem**: `production.py` besteht `check --deploy` nicht.

**Fix**:
- Führe `check --deploy --settings=config.settings.production` aus
- Dokumentiere Befunde (auch wenn Warnings verbleiben)
- Vorbereitung für umgebungsvariablengesteuerte Settings (SECURE_SSL_REDIRECT, etc.)
- Keine echten Secrets erzeugen, nur Struktur vorbereiten

**Grenzen**: Ziel ist nicht "Production fertig", sondern "Production-Risiken sichtbar und Struktur vorbereitet".

### Behobene GELB-Themen

**OrderAdmin/OrderItemAdmin Immutability**: Siehe oben (auch bei ROT gelistet als notwendig).

**Weitere GELB-Themen** (Consent-Exceptions, Pricing-Überlappungen): Bleiben offen für spätere Blöcke.

### Entscheidung: Frozen Module ändern nur wegen Audit

`orders` und `checkout` sind frozen/re-frozen nach AB 12.1.

AB 13 ändert diese Module NUR wegen Senior-Audit-Befund (Atomarität, Admin-Schutz).

Jede Änderung wird dokumentiert:
- Grund (Audit-Befund Nr. X)
- Risiko (Transaktions-Isolation, Admin-Konsistenz)
- Impact (Datensicherheit, User-Experience)
- Testabsicherung (Regression + neue Atomarität-/Rollback-Tests)

### Konsequenzen

- `checkout.services.create_order_from_checkout()` ist transaktional absichert
- `OrderAdmin` und `OrderItemAdmin` haben erweiterte `readonly_fields`
- Neue Rollback-Tests bestätigen atomare Fehlerbehandlung
- Admin-Tests bestätigen Immutability
- Doku ist korrigiert (Datums- und Status-Fehler)
- Production-Settings: Check-Befunde dokumentiert, Struktur vorbereitet
- Keine Breaking Changes zu existierenden Services
- Regression-Tests: 262+ (erwartet: 265-270 mit neuen AB 13 Tests)

## Entscheidung: REST API Modul mit Django REST Framework – Arbeitsblock 14

### Datum
2026-05-05

### Entscheidung
Die neue `apps.api` Anwendung wird als DRF-basiertes, **read-only** REST API Modul (v1) gebaut mit den folgenden Grundprinzipien:

1. **Read-Only Scope**: Nur GET-Anfragen; POST/PUT/PATCH/DELETE sind nicht implementiert
2. **7 Endpoints** für Grunddaten-Abruf (Katalog, Versand, Zahlungen, Rechtsdokumente, Gesundheit)
3. **DRF Serializers** für Modellliste/Detail-Konvertierung
4. **Standardisierte Response**: success/error Struktur für alle Endpoints
5. **Customer Group Filtering**: b2c/b2b Unterscheidung auf Datenebene
6. **Keine Geheimnisse**: Keine API-Keys, Session-Cookies, oder sensitive Daten in Responses
7. **Frozen Status**: Keine neuen Endpoints bis Phase 2; Änderungen nur mit dokumentiertem Business-Grund

### Begründung
- Künftige Frontend-Clients (SPA, Mobile) benötigen standardisiertes Read-only API
- DRF ist Industrie-Standard für Django REST APIs
- Früher API-Start ermöglicht paralleles Frontend-Development in Phase 2
- Read-only Scope begrenzt Sicherheitsrisiken (keine Transaktionen, keine Bezahlung)
- Frozen-Status verhindert Feature-Creep und unkontrollierte API-Wucherung
- 7 Endpoints decken 80% der häufigsten Daten-Anfragen ab (Produkte, Versandoptionen, etc.)

### Konsequenzen
- `apps.api` neu angelegt mit urls.py, views.py, serializers.py
- `rest_framework` zu INSTALLED_APPS hinzugefügt
- `config/urls.py` routing `api/` URLs ein
- 33 Comprehensive Tests für alle Endpoints + Boundaries (POST-Ablehnung)
- 7 Endpunkte:
  1. `GET /api/v1/health/` – Status (ok, version, environment)
  2. `GET /api/v1/catalog/categories/` – Produktkategorien
  3. `GET /api/v1/catalog/products/` – Produktliste (b2c/b2b filtering)
  4. `GET /api/v1/catalog/products/<slug>/` – Produktdetail
  5. `GET /api/v1/shipping/methods/` – Versandmethoden (b2c/b2b)
  6. `GET /api/v1/payments/methods/` – Zahlungsmethoden (b2c/b2b)
  7. `GET /api/v1/legal/active/` – Aktive Rechtsdokumente (b2c/b2b)
- Standardisierte Response-Struktur: `{success: true, data: {...}}` oder `{success: false, error: {code, message}}`
- Keine Preis-Informationen in Responses (absichtlich für Phase 1)
- Keine Checkout/Order/Payment Endpoints
- Keine Login/Register Endpoints
- Keine Admin-API

### Änderungsregeln
Künftige Änderungen an der API erfordern:
1. Dokumentierte Business-Rationale
2. Impact-Analyse: Welche existierenden Endpoints sind betroffen?
3. Test-Regression: Alle 304+ Tests müssen grün sein
4. Aktualisierung von `docs/modules/api.md`
5. Eintrag in DECISIONS.md + PROGRESS.md

### Out of Scope (Absichtlich)
- User-Authentifizierung / Login
- Order-Erstellung
- Payment-Verarbeitung
- Versand-Buchung
- E-Mail-Versand
- Admin-Endpoints
- Webhooks / Event-Systeme
- Externe Anbieter-Integration (Payment, Shipping, etc.)
- Staging/Production Deployment (Local/Dev only)

### Kommentare
Diese Entscheidung friert das API-Modul auf einem stabilen, minimalen Grundgerüst ein. Künftige Erweiterungen (Authentifizierung, Warenkorb-Verwaltung, Checkout-Submission) sind möglich, aber müssen explizit geplant und dokumentiert werden. Das Read-only Grundgerüst bleibt unverändert.
