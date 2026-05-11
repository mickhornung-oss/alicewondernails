# Alice Wonder Nails – PROJECT_MASTER.md

Stand: 2026-05-04  
Zielpfad im Repo: `docs/PROJECT_MASTER.md`  
Fester Projektordner: `C:\Users\mickh\Desktop\alice-wondernails`  
Projektphase: Große lokale Shop-/Plattform-Version, Backend-first  
Architekturentscheidung: Django-basierter modularer Monolith mit PostgreSQL

---

## 1. Zweck dieser Datei

Diese Datei ist die zentrale Master-Datei für das Projekt **Alice Wonder Nails**.

Sie beschreibt nicht einzelne Arbeitsbefehle.  
Sie beschreibt den festen Zielzustand, die Architektur, die Projektgrenzen, die Modulstruktur, die Qualitätsregeln und die fachliche Richtung des Projekts.

Jede ausführende KI, jeder Entwickler und jede spätere Dokumentation muss diese Datei als oberste Projektwahrheit behandeln.

Diese Datei ist die Projekt-Verfassung.

Wenn spätere Prompts, Tickets oder Arbeitsblöcke dieser Datei widersprechen, gilt zuerst diese Datei, außer eine Änderung wird bewusst dokumentiert und in `docs/DECISIONS.md` begründet.

---

## 2. Aktueller Projektstand

Die kleine statische V1-/Uebergangsseite wurde extern gesichert und ist nicht mehr Teil dieses aktiven Projektordners.

Dieser Projektordner enthaelt ab Arbeitsblock 01.4 nur noch die neue grosse V2-Shop-/Plattform-Struktur.

Die lokale Neuaufbau-Phase laeuft backend-first mit Django und PostgreSQL.

---

## 3. Langfristiges Ziel

Alice Wonder Nails soll eine hochwertige Website- und Shop-Plattform werden.

Das System soll lokal entwickelt werden und technisch möglichst nah an der späteren Online-Version liegen.

Ziel ist kein Demo-Shop und keine Bastel-Landingpage, sondern ein sauber aufgebautes, wartbares, testbares und später deploybares Shop-System mit:

- öffentlicher Website
- Produktkatalog
- Shop-Funktion
- Warenkorb
- Checkout
- Bestellprozess
- Admin-Zugang
- User-Zugängen
- Endverbraucher-Strang
- Unternehmer-/Großhandels-Strang
- Rollen- und Rechteverwaltung
- Galerie
- Videos/Content
- spätere Bewertungen/Feedback-Funktionen
- rechtlicher Struktur
- Cookie-/Consent-Struktur
- dokumentierter Backend-Architektur
- nachvollziehbaren Tests
- späterer Hosting-/Deployment-Strategie

---

## 4. Fester Projektordner und harte Projektgrenzen

Fester Projektordner:

```text
C:\Users\mickh\Desktop\alice-wondernails
```

Es darf ausschließlich innerhalb dieses Ordners gearbeitet werden.

Nicht erlaubt:

- Dateien außerhalb dieses Ordners lesen, ändern, löschen oder anlegen
- Secrets oder echte Zugangsdaten in Git speichern
- globale Systemänderungen ohne ausdrückliche Freigabe
- wilde Refactorings ohne Dokumentation
- neue V2-Dateien blind loeschen
- Deployment-Entscheidungen erzwingen, bevor die lokale Architektur steht
- unfertige Features als fertig bezeichnen
- Fake-Tests oder unbewiesene Erfolgsmeldungen
- fertige Module ohne Notwendigkeit wieder anfassen
- mehrere Baustellen gleichzeitig halb beginnen
- stabile Module wegen optischer Kleinigkeiten beschädigen

---

## 5. Grundentscheidung: modularer Monolith statt Microservice-Chaos

Das Projekt wird als **modularer Monolith** gebaut.

Das bedeutet:

- eine Hauptanwendung
- ein Backend-Projekt
- eine PostgreSQL-Datenbank
- klar getrennte Django-Apps/Module
- klare Modulgrenzen
- klare Schnittstellen
- zentrale Tests
- zentrale Dokumentation
- später austauschbare Adapter für externe Dienste

Es wird **nicht** als Microservice-System gestartet.

Warum?

Weil ein Shop mit Produkten, Kunden, Bestellungen, Rollen, Rechtstexten und Adminbereich zwar groß ist, aber am Anfang keine verteilte Infrastruktur braucht. Microservices wären hier zu früh, zu teuer, zu fehleranfällig und würden nur neue Probleme erzeugen. Die Menschheit hat schon genug Wege erfunden, sich selbst zu quälen.

Modularer Monolith heißt:

- sauber genug für große Entwicklung
- stabil genug für lokale Arbeit
- übersichtlich genug für Tests
- später erweiterbar
- ohne unnötigen Infrastruktur-Zirkus

---

## 6. Backend-first

Das Projekt startet mit dem Backend, nicht mit dem Frontend.

Der Grund:

User, Rollen, Produkte, Preise, Bestellungen, Warenkorb, Rechtstexte, Freigaben und Adminlogik müssen zuerst solide sitzen.

Ein schönes Frontend auf kaputtem Backend ist nur ein geschminkter Unfall.

---

## 7. Lokal zuerst, onlinefähig von Anfang an

Die lokale Version soll möglichst nah an der späteren Online-Version liegen.

Deshalb:

- PostgreSQL lokal
- Umgebungsvariablen über `.env`
- keine hart codierten lokalen Spezialpfade
- keine lokalen Sondertricks, die später online nicht funktionieren
- saubere Settings-Trennung
- dokumentierte Start-, Test- und Statuswege
- klare Medien-/Upload-Struktur
- saubere Migrationsstrategie
- spätere Hostingfähigkeit wird vorbereitet, aber noch nicht erzwungen

---

## 8. Empfohlener Hauptstack

### Backend

- Python
- Django
- Django REST Framework
- PostgreSQL
- Django Admin
- pytest / pytest-django
- django-environ oder vergleichbare `.env`-Konfiguration
- optional später: Celery/RQ für Hintergrundjobs
- optional später: Redis für Cache/Queue

### Frontend

Frontend wird später entschieden.

Mögliche Varianten:

- Django Templates für robuste erste Shop-Version
- React/Next.js für stärkere spätere UI
- Hybrid: Django Admin + API + separates Frontend

Für den Start gilt:

Frontend ist nicht Hauptfokus.  
Das Backend ist die tragende Struktur.

### Datenbank

- lokal: PostgreSQL
- später online: PostgreSQL-kompatible Hosting-Umgebung
- SQLite nur für Minimaltests oder sehr kleine Hilfsfälle, nicht als Hauptdatenbank

---

## 9. Zielstruktur im Repo

```text
alice-wondernails/
│
├─ backend/
│  ├─ config/
│  ├─ apps/
│  │  ├─ accounts/
│  │  ├─ customers/
│  │  ├─ business/
│  │  ├─ catalog/
│  │  ├─ pricing/
│  │  ├─ cart/
│  │  ├─ orders/
│  │  ├─ payments/
│  │  ├─ shipping/
│  │  ├─ content/
│  │  ├─ gallery/
│  │  ├─ reviews/
│  │  ├─ legal/
│  │  ├─ consent/
│  │  ├─ notifications/
│  │  └─ auditlog/
│  │
│  ├─ tests/
│  ├─ manage.py
│  ├─ requirements.txt
│  └─ .env.example
│
├─ docs/
│  ├─ PROJECT_MASTER.md
│  ├─ PROJECT_RULES.md
│  ├─ PROGRESS.md
│  ├─ DECISIONS.md
│  ├─ CLEANUP_PLAN.md
│  ├─ BACKEND_BLUEPRINT.md
│  ├─ MODULE_PLAN.md
│  ├─ MODULE_STATUS.md
│  ├─ DATA_MODEL.md
│  ├─ LEGAL_REQUIREMENTS.md
│  ├─ TESTING_RULES.md
│  ├─ DEPLOYMENT_PLAN.md
│  ├─ SECURITY_PLAN.md
│  ├─ ACCESSIBILITY_PLAN.md
│  ├─ API_CONTRACTS.md
│  ├─ ADMIN_PLAN.md
│  └─ SHOP_PROCESS.md
│
├─ docs/modules/
│  ├─ accounts.md
│  ├─ customers.md
│  ├─ business.md
│  ├─ catalog.md
│  ├─ pricing.md
│  ├─ cart.md
│  ├─ orders.md
│  ├─ payments.md
│  ├─ shipping.md
│  ├─ content.md
│  ├─ gallery.md
│  ├─ reviews.md
│  ├─ legal.md
│  ├─ consent.md
│  ├─ notifications.md
│  └─ auditlog.md
│
├─ scripts/
│  ├─ start_backend.ps1
│  ├─ stop_backend.ps1
│  ├─ status_backend.ps1
│  └─ test_backend.ps1
│
├─ .github/
│  └─ optional später CI, Templates, Security
│
├─ .gitignore
├─ README.md
└─ CHANGELOG.md
```

---

## 10. Modul-Freeze-Regel

Dieses Projekt wird in Modulen gebaut.

Ein Modul wird nicht endlos wieder aufgerissen, sobald es einmal stabil ist.

Jedes Modul durchläuft feste Statusstufen:

```text
planned
in_progress
review
tested
frozen
locked
```

### planned

Das Modul ist geplant, aber noch nicht gebaut.

### in_progress

Das Modul wird aktiv gebaut.

### review

Das Modul ist technisch vorhanden und wird geprüft.

### tested

Das Modul hat Tests und diese Tests laufen erfolgreich.

### frozen

Das Modul gilt fachlich und technisch als stabil.

Ab diesem Zustand darf es nur noch geändert werden, wenn:

- ein klarer fachlicher Grund vorliegt
- ein anderes Modul zwingend eine Schnittstellenanpassung benötigt
- ein Fehler gefunden wurde
- eine Sicherheitskorrektur nötig ist
- eine dokumentierte Architekturentscheidung vorliegt

### locked

Das Modul gilt als abgeschlossen und darf nur noch in Ausnahmefällen verändert werden.

Änderungen an locked-Modulen brauchen:

- Eintrag in `docs/DECISIONS.md`
- Eintrag in `docs/MODULE_STATUS.md`
- Begründung
- Impact-Analyse
- Testplan
- erfolgreiche Regressionstests
- kurze Änderungsnotiz in `CHANGELOG.md`

---

## 11. Modul-Verträge

Jedes Modul bekommt eine eigene Dokumentation unter:

```text
docs/modules/<modulname>.md
```

Jede Moduldatei enthält mindestens:

- Zweck des Moduls
- fachliche Verantwortung
- Datenmodelle
- API-Endpunkte
- Admin-Funktionen
- erlaubte Abhängigkeiten
- verbotene Abhängigkeiten
- Tests
- aktueller Status
- bekannte offene Punkte
- Freeze-Status
- Änderungsregeln

Ein Modul darf nicht heimlich Verantwortung von anderen Modulen übernehmen.

Beispiel:

- `catalog` verwaltet Produkte
- `pricing` verwaltet Preislogik
- `orders` speichert Bestellungen
- `legal` verwaltet Rechtstextversionen
- `auditlog` protokolliert kritische Änderungen

Wenn ein Modul auf ein anderes zugreift, muss dieser Zugriff dokumentiert sein.

---

## 12. Austauschbarkeit von Modulen

Das System muss so gebaut werden, dass einzelne Bereiche später ausgetauscht oder erweitert werden können.

Nicht alles muss sofort austauschbar sein.  
Aber die Stellen, bei denen spätere Anbieter oder technische Lösungen realistisch wechseln können, müssen sauber gekapselt werden.

Besonders austauschbar vorbereiten:

- Payment-Anbieter
- Versanddienstleister
- E-Mail-Versand
- Medien-/Dateispeicher
- Frontend
- Consent-Banner/Consent-Logik
- Produktexport/-import
- spätere externe Warenwirtschaft
- Hosting-/Deployment-Umgebung

Dafür gelten Adapter-/Schnittstellen-Prinzipien:

- externe Dienste nicht direkt überall im Code verwenden
- Adapter/Service-Schichten nutzen
- API-Verträge dokumentieren
- keine Anbieterlogik quer durch alle Module verstreuen
- Tests gegen interne Schnittstellen schreiben, nicht nur gegen konkrete Anbieter

Beispiel:

Payment darf nicht überall direkt `Stripe`, `PayPal` oder einen anderen Anbieter kennen.

Stattdessen:

```text
orders -> payments service interface -> konkreter payment adapter
```

So kann der Anbieter später gewechselt werden, ohne dass der halbe Shop zerbricht wie ein schlecht verpacktes Nagelset.

---

## 13. Abhängigkeitsregeln zwischen Modulen

Grundregel:

Module dürfen voneinander wissen, aber nicht wild ineinander herumpfuschen.

### Erlaubt

- klar dokumentierte ForeignKeys
- klar dokumentierte Service-Funktionen
- klar dokumentierte API-Aufrufe
- gemeinsame Basisobjekte, wenn sinnvoll
- zentrale Utility-Funktionen, wenn sie wirklich allgemein sind

### Verboten

- direkte Datenmanipulation in fremden Modulen ohne Service/Vertrag
- Copy-Paste-Logik zwischen Modulen
- versteckte Seiteneffekte
- Import-Ketten, die zirkulär werden
- Businesslogik im Template verstecken
- Admin-Aktionen ohne Prüfung/Auditlog
- Preisberechnung direkt in mehreren Modulen duplizieren

---

## 14. Fachliche Hauptbereiche

## 14.1 Öffentliche Website

Die öffentliche Website dient als Schaufenster.

Sie enthält später:

- Startseite
- Über uns
- Galerie
- Videos
- Produktvorschau
- Kontakt
- Early Access / Anfragebereich
- Shop-Einstieg
- Rechtstexte
- Cookie-/Consent-Banner

Die öffentliche Seite darf auch ohne Login nutzbar sein.

---

## 14.2 Shop

Der Shop ist der zentrale Zielbereich.

Er enthält:

- Produktkategorien
- Produktdetailseiten
- Produktbilder
- Varianten
- Preise
- Warenkorb
- Checkout
- Bestellungen
- Kundenkonto
- Versandinformationen
- Zahlungsinformationen
- B2C-/B2B-Unterscheidung

Der Shop muss von Anfang an so geplant werden, dass B2C und B2B sauber getrennt behandelt werden können.

---

## 14.3 Admin-Bereich

Der Admin-Bereich ist die Steuerzentrale.

Er enthält später:

- Produktverwaltung
- Kategorieverwaltung
- Preisverwaltung
- Bestellverwaltung
- Kundenverwaltung
- B2B-Freigaben
- Rollenverwaltung
- Galerieverwaltung
- Videoverwaltung
- Contentverwaltung
- Rechtstextverwaltung
- Consent-/Cookie-Konfiguration
- Audit-Log
- Systemstatus
- einfache Auswertungen

Django Admin darf als erste solide Admin-Basis genutzt werden.  
Eine eigene Admin-UI kann später folgen.

---

## 14.4 User-Bereich

Jeder registrierte User ist zunächst Endverbraucher.

User können später:

- eigenes Profil verwalten
- Lieferadressen verwalten
- Rechnungsadressen verwalten
- Bestellungen ansehen
- Favoriten oder Wunschlisten nutzen
- B2B-/Großhandelszugang beantragen

---

## 14.5 B2B-/Großhandel

B2B ist kein komplett getrenntes System.

Es ist eine Erweiterung des normalen User-Systems.

Ein User kann den Status `business_pending` erhalten.  
Ein Admin kann daraus `business_approved` machen.

B2B kann später erhalten:

- eigene Preise
- andere Produktfreigaben
- Mindestmengen
- eigene AGB
- andere Widerrufs-/Rückgabeinformationen
- eigene Zahlungsarten
- spätere Netto-/Brutto-Logik
- Firmenprofil
- Ansprechpartner
- USt-ID
- Nachweisprüfung

---

## 15. Rollenmodell

Vorgesehene Rollen/Stati:

```text
anonymous
consumer
business_pending
business_approved
staff
admin
superadmin
```

### anonymous

Nicht eingeloggter Besucher.

Darf:

- öffentliche Seiten sehen
- Produkte ansehen, sofern öffentlich
- ggf. Warenkorb starten
- sich registrieren

### consumer

Normaler Endverbraucher.

Darf:

- bestellen
- eigenes Konto verwalten
- eigene Bestellungen sehen
- B2B-Upgrade beantragen

### business_pending

User hat B2B beantragt, ist aber noch nicht freigegeben.

Darf:

- normales Consumer-Konto nutzen
- Status der Anfrage sehen
- ggf. Unterlagen nachreichen

### business_approved

Freigegebener Unternehmer-/Großhandelskunde.

Darf:

- B2B-Produkte sehen
- B2B-Preise sehen
- B2B-Konditionen nutzen
- B2B-Bestellungen auslösen

### staff

Interner Bearbeiter.

Darf:

- ausgewählte Admin-Funktionen nutzen
- Bestellungen bearbeiten
- Content pflegen

### admin

Voller fachlicher Admin.

Darf:

- Produkte verwalten
- Kunden verwalten
- Rollen vergeben
- B2B freigeben
- Rechtstexte aktivieren
- Shop-Konfiguration pflegen

### superadmin

Technische höchste Rolle.

Nur für System-/Owner-Zugriff.

---

## 16. Backend-Module

## 16.1 accounts

Zweck:

- User-System
- Login
- Registrierung
- Rollen
- Rechte
- Accountstatus
- Passwortprozesse
- spätere 2FA-Vorbereitung

Wichtig:

- ein zentrales User-System
- keine getrennten B2C-/B2B-Usertabellen
- Rollen und Profile sauber getrennt

Statusziel:

- nach Fertigstellung frozen
- nur noch Änderungen über dokumentierten Modul-Change-Prozess

---

## 16.2 customers

Zweck:

- Endverbraucherprofil
- Name
- Kontakt
- Lieferadressen
- Rechnungsadressen
- Kundenhistorie

---

## 16.3 business

Zweck:

- Firmenprofil
- B2B-Antrag
- Freigabestatus
- Admin-Prüfung
- USt-ID optional
- Nachweis optional
- B2B-Konditionen

---

## 16.4 catalog

Zweck:

- Produkte
- Kategorien
- Produktbilder
- Varianten
- Sichtbarkeit
- Lagerstatus
- Tags
- Produktstatus

Da es im Kern um Nagelprodukte geht, muss das System besonders gut mit Farben, Serien, Varianten, Sets und Bildern umgehen können.

Beispiele für mögliche Produktmerkmale:

- Farbe
- Farbcode
- Serie/Kollektion
- Finish
- Inhalt/Menge
- Set/Einzelartikel
- Anwendungshinweise
- Inhaltsstoffe optional
- Warnhinweise optional
- Produktbilder
- Swatches/Farbmuster

---

## 16.5 pricing

Zweck:

- B2C-Preis
- B2B-Preis
- Aktionspreise
- Staffelpreise später
- Preisgültigkeit
- Steuer-/Brutto-/Netto-Vorbereitung

Wichtig:

Preise müssen bei Bestellungen als Snapshot gespeichert werden.

Preislogik darf nicht verteilt werden.

Nicht erlaubt:

- Preisberechnung direkt in `orders`, `cart`, Templates oder Admin-Aktionen duplizieren
- B2B-Preise ohne Rollenprüfung anzeigen
- historische Bestellpreise nachträglich verändern

---

## 16.6 cart

Zweck:

- Warenkorb
- Warenkorbpositionen
- anonymer Warenkorb optional
- eingeloggter Warenkorb
- Preisprüfung
- Verfügbarkeitsprüfung

Der Warenkorb darf Preise anzeigen, aber die zentrale Preislogik kommt aus `pricing`.

---

## 16.7 orders

Zweck:

- Bestellungen
- Bestellpositionen
- Bestellstatus
- Zahlungsstatus
- Versandstatus
- Storno
- Widerruf/Rückgabe
- Rechnungsbezug später

Wichtig:

Bestellungen müssen historische Werte speichern:

- Produktname zum Kaufzeitpunkt
- Preis zum Kaufzeitpunkt
- Steuersatz zum Kaufzeitpunkt
- Kundentyp zum Kaufzeitpunkt
- AGB-/Widerrufs-/Rechtstextversion zum Kaufzeitpunkt
- Versandart zum Kaufzeitpunkt
- Zahlungsart zum Kaufzeitpunkt

---

## 16.8 payments

Zweck:

- Zahlungsarten vorbereiten
- Zahlungsstatus
- Zahlungsreferenzen
- später Anbindung an Zahlungsanbieter

Am Anfang nur strukturell vorbereiten.  
Keine echte Zahlungsintegration im Startblock.

Payment muss als austauschbarer Adapter geplant werden.

---

## 16.9 shipping

Zweck:

- Versandarten
- Versandkosten
- Versandstatus
- Sendungsnummer
- Versandländer
- Lieferzeiten
- Versandregeln

Shipping muss als austauschbarer Adapter geplant werden, falls später DHL, Hermes, Warenpost oder ein anderer Anbieter angebunden wird.

---

## 16.10 content

Zweck:

- Seiteninhalte
- Startseite
- Über uns
- Kontakt
- Early Access
- Landingpage-Blöcke

---

## 16.11 gallery

Zweck:

- Galerie-Bilder
- Kategorien
- Reihenfolge
- Sichtbarkeit
- Highlights
- spätere Verknüpfung mit Produkten

---

## 16.12 reviews

Zweck:

- Bewertungen
- Galerie-/Produktfeedback
- Moderation
- Freigabe durch Admin
- Sterne/Text/Bild optional

Dieses Modul wird vorbereitet, aber nicht sofort komplex gebaut.

Später möglich:

- Produktbewertungen
- Galerie-Likes
- „Gut gemacht“-Feedback
- Vorher/Nachher-Galerie
- Admin-Moderation
- Missbrauchsschutz
- Freigabe-Workflow

---

## 16.13 legal

Zweck:

- Impressum
- Datenschutz
- AGB B2C
- AGB B2B
- Widerrufsbelehrung B2C
- Versandinformationen
- Zahlungsinformationen
- Rechtstextversionen
- aktive/archivierte Versionen

Keine finalen Rechtstexte erfinden.  
Das Modul stellt die technische Struktur bereit.

---

## 16.14 consent

Zweck:

- Cookie-Consent
- notwendige Cookies
- Statistik optional
- Marketing optional
- Consent-Version
- Zeitstempel
- User oder anonyme Session

---

## 16.15 notifications

Zweck:

- Systemmails vorbereiten
- Registrierungsbestätigung
- Bestellbestätigung
- B2B-Antragsstatus
- Passwortprozesse
- Admin-Benachrichtigungen

Am Anfang strukturell vorbereiten.  
Echter Mailversand später.

Notifications muss als austauschbarer Adapter geplant werden.

---

## 16.16 auditlog

Zweck:

- wichtige Admin-Aktionen protokollieren
- Rollenänderungen
- B2B-Freigaben
- Produktänderungen
- Preisänderungen
- Rechtstext-Aktivierungen
- Bestellstatusänderungen

Ein Shop ohne Auditlog ist wie ein Kassenbuch mit Radiergummi.

---

## 17. Produktlogik

Das Sortiment ist thematisch fokussiert auf Nagelprodukte.

Das System muss trotzdem sauber genug sein für:

- mehrere Kategorien
- viele Farben
- Produktserien
- Produktvarianten
- Bilder pro Produkt
- ggf. Set-Angebote
- B2C/B2B-Sichtbarkeit
- B2C/B2B-Preise
- aktive/inaktive Produkte
- Sortierung
- Filterung
- Suche

Mögliche Kategorien:

- Nagellacke
- UV-/Gel-Produkte
- Farben
- Sets
- Zubehör
- Pflege
- Aktionen
- Neuheiten
- Business/Großhandel

Die endgültigen Kategorien hängen von den später gelieferten Produktdaten ab.

---

## 18. Datenmodell-Grundideen

Kernobjekte:

- User
- UserRole / UserStatus
- CustomerProfile
- BusinessProfile
- Address
- ProductCategory
- Product
- ProductVariant
- ProductImage
- Price
- Cart
- CartItem
- Order
- OrderItem
- PaymentStatus
- ShippingMethod
- ShippingStatus
- LegalDocument
- LegalDocumentVersion
- ConsentRecord
- GalleryItem
- VideoItem
- Review
- AuditLogEntry

---

## 19. Rechtliche Struktur

Das System muss rechtlich sauber vorbereitet werden.

Wichtig:

- Impressum
- Datenschutzerklärung
- Cookie-/Consent-Verwaltung
- B2C-Widerrufsbelehrung
- B2C-AGB
- B2B-AGB
- Versandinformationen
- Zahlungsinformationen
- Preisangaben
- Buttonlösung / klare Bestellübersicht
- Barrierefreiheit für B2C-Shop mitdenken
- Rechtstextversionen speichern
- Zustimmung/Bestellkontext nachvollziehbar speichern

Diese Datei liefert keine Rechtsberatung.  
Finale Rechtstexte müssen später durch seriöse Quelle, Generator oder Fachprüfung erstellt werden.

---

## 20. B2C/B2B-Trennung

B2C und B2B müssen fachlich klar getrennt sein, aber technisch nicht als zwei völlig getrennte Systeme gebaut werden.

Empfohlen:

Ein User-System mit Rollen und Profilen.

B2C:

- Verbraucherrechte
- Widerruf
- Brutto-Preise
- verbraucherfreundliche Pflichtinformationen
- Barrierefreiheit besonders wichtig
- klare Bestellbuttons
- AGB/Widerruf sichtbar im Checkout

B2B:

- Freigabe durch Admin
- Firmenprofil
- ggf. andere Preise
- ggf. Netto-/Brutto-Logik
- eigene AGB
- andere Konditionen
- ggf. Mindestmengen
- eingeschränkter Zugang

---

## 21. Sicherheit

Sicherheitsgrundlagen:

- keine Secrets in Git
- `.env.example`, aber keine echte `.env`
- sichere Passwortspeicherung über Framework
- CSRF-Schutz
- XSS-Schutz
- Berechtigungsprüfung
- Admin-Zugänge nur für berechtigte Rollen
- Dateiuploads validieren
- keine beliebigen Dateitypen erlauben
- Auditlog für kritische Aktionen
- spätere Backup-Strategie
- später Rate-Limiting/Login-Schutz prüfen

---

## 22. Medien und Uploads

Geplante Medien:

- Produktbilder
- Galeriebilder
- Videos
- Logos
- Contentgrafiken
- ggf. B2B-Nachweise

Regeln:

- Uploads in separatem Media-Bereich
- lokale Uploads nicht versehentlich ins Git
- Dateitypen begrenzen
- Bildgrößen prüfen
- spätere Thumbnail-Generierung vorbereiten
- Original und Web-Version unterscheiden

---

## 23. API-Strategie

API nicht wild wachsen lassen.

Geplante API-Bereiche:

- `/api/health/`
- `/api/auth/`
- `/api/account/`
- `/api/products/`
- `/api/categories/`
- `/api/pricing/`
- `/api/cart/`
- `/api/orders/`
- `/api/gallery/`
- `/api/content/`
- `/api/legal/`
- `/api/consent/`
- `/api/admin/...` nur falls eigene Admin-API nötig

Für jeden API-Bereich sollen später in `docs/API_CONTRACTS.md` Zweck, Request, Response und Rechte dokumentiert werden.

---

## 24. Admin-Strategie

Start:

- Django Admin als robuste Admin-Basis

Später:

- eigene Admin-Oberfläche möglich

Admin-Funktionen müssen schrittweise entstehen:

1. User anzeigen
2. Kundenprofile anzeigen
3. B2B-Anfragen prüfen
4. Produkte pflegen
5. Preise pflegen
6. Kategorien pflegen
7. Bilder pflegen
8. Bestellungen bearbeiten
9. Rechtstexte versionieren
10. Content pflegen
11. Auditlog prüfen

---

## 25. Teststrategie

Jedes Modul braucht Tests.

Mindesttests:

- Projekt startet
- Django System Check läuft
- Migrationen sind konsistent
- Modelle funktionieren
- Admin-Registrierung funktioniert
- Rollenrechte funktionieren
- API-Endpunkte liefern erwartete Statuscodes
- Bestelllogik speichert Preis-Snapshots
- B2C/B2B-Sichtbarkeit funktioniert
- Rechtstextversion wird bei Bestellung referenziert
- Consent wird gespeichert
- Uploadvalidierung funktioniert

Skripte:

- `scripts/start_backend.ps1`
- `scripts/stop_backend.ps1`
- `scripts/status_backend.ps1`
- `scripts/test_backend.ps1`

---

## 26. Regression-Regel

Wenn ein Modul `frozen` oder `locked` ist und ein anderes Modul später darauf aufbauen muss, gilt:

1. Erst prüfen, ob die bestehende Schnittstelle reicht.
2. Wenn nicht, Änderungsvorschlag dokumentieren.
3. Auswirkungen auf abhängige Module prüfen.
4. Tests für altes und neues Verhalten schreiben.
5. Änderung durchführen.
6. Regressionstests ausführen.
7. Status in `docs/MODULE_STATUS.md` aktualisieren.
8. Änderung in `docs/DECISIONS.md` begründen.

Kein Modul wird „mal eben“ angepasst.  
„Mal eben“ ist der natürliche Feind funktionierender Software.

---

## 27. Dokumentationsstruktur

Pflichtdokumente:

- `docs/PROJECT_MASTER.md`
- `docs/PROJECT_RULES.md`
- `docs/PROGRESS.md`
- `docs/DECISIONS.md`
- `docs/CLEANUP_PLAN.md`
- `docs/BACKEND_BLUEPRINT.md`
- `docs/MODULE_PLAN.md`
- `docs/MODULE_STATUS.md`
- `docs/DATA_MODEL.md`
- `docs/LEGAL_REQUIREMENTS.md`
- `docs/TESTING_RULES.md`
- `docs/DEPLOYMENT_PLAN.md`
- `docs/SECURITY_PLAN.md`
- `docs/ACCESSIBILITY_PLAN.md`
- `docs/API_CONTRACTS.md`
- `docs/ADMIN_PLAN.md`
- `docs/SHOP_PROCESS.md`

`PROGRESS.md` wird fortlaufend gepflegt.

`DECISIONS.md` enthält Architekturentscheidungen mit Begründung.

`CLEANUP_PLAN.md` enthält Bereinigungen, bevor gelöscht wird.

`MODULE_STATUS.md` enthält den aktuellen Status jedes Moduls.

---

## 28. Hosting-/Deployment-Grundhaltung

Noch keine finale Hosting-Entscheidung.

Später zu prüfen:

- Strato mit passendem Paket
- anderer Hoster mit Python/Django/PostgreSQL
- Managed PostgreSQL
- VPS
- PaaS
- Backup-Möglichkeiten
- E-Mail-Versand
- SSL
- Datenschutzstandort
- Kosten
- Wartbarkeit

Wichtig:

Das lokale System darf nicht so gebaut werden, dass es nur auf einem Spezialsetup funktioniert.

---

## 29. Projektphasen

### Phase 0 – Wahrheit herstellen

- Repo pruefen
- V1-/Strato-/Legacy-Reste wegen externem Backup aus dem aktiven Projektordner entfernen
- Dokumentation aktualisieren
- Cleanup-Plan erstellen
- Zielstruktur festhalten

### Phase 1 – Backend-Fundament

- Django-Projekt
- PostgreSQL-Konfiguration
- Settings
- `.env.example`
- Healthcheck
- erste Tests
- Start-/Testskripte

### Phase 2 – Accounts/Rollen/Profile

- User-System
- Rollen
- CustomerProfile
- BusinessProfile
- B2B-Antrag/Freigabe
- Tests
- Modul danach frozen

### Phase 3 – Katalog/Produkte

- Kategorien
- Produkte
- Varianten
- Bilder
- Produktstatus
- Tests
- Modul danach frozen

### Phase 4 – Pricing

- B2C-Preise
- B2B-Preise
- Aktionspreise vorbereitet
- Preisservice
- Tests
- Modul danach frozen

### Phase 5 – Warenkorb/Bestellung

- Warenkorb
- Bestellpositionen
- Preis-Snapshots
- B2C/B2B-Kontext
- Bestellstatus
- Tests
- Modul danach frozen

### Phase 6 – Legal/Consent

- Rechtstextversionen
- Consent-Struktur
- Checkout-Rechtsbezug
- Tests
- Modul danach frozen

### Phase 7 – Admin-Funktionen

- Produktpflege
- Preisverwaltung
- Bestellpflege
- B2B-Freigaben
- Rechtstextpflege
- Auditlog

### Phase 8 – Content/Galerie/Videos/Reviews

- Contentseiten
- Galerie
- Videos
- spätere Bewertungen/Feedback

### Phase 9 – Frontend/Shop-UI

- öffentliche Seite
- Produktseiten
- Warenkorb
- Checkout
- Konto
- B2B-Bereich

### Phase 10 – Deployment-Vorbereitung

- Hoster-Entscheidung
- Produktionssettings
- Backup
- SSL
- Medienstrategie
- E-Mail
- Datenschutz-/Rechtstexte final

---

## 30. Qualitätsdefinition

Ein Bereich gilt erst als fertig, wenn:

- Code vorhanden ist
- Doku aktualisiert wurde
- Tests vorhanden sind
- Tests grün laufen
- keine Secrets im Repo sind
- Startweg dokumentiert ist
- Fehlerfälle bedacht wurden
- keine alten falschen Projektstände in README/Doku stehen
- Modulstatus aktualisiert wurde
- Schnittstellen dokumentiert wurden
- Folgeauswirkungen geprüft wurden

---

## 31. Was bewusst noch nicht entschieden ist

Noch offen:

- finaler Hoster
- finales Frontend-Framework
- Zahlungsanbieter
- Versanddienstleister
- finale Rechtstexte
- Produktdatenmodell im Detail
- genaue B2B-Preislogik
- Newsletter/Marketing
- Bewertungslogik im Detail
- KI-/Designer-Sandbox später

Diese Punkte werden nicht ignoriert.  
Sie werden bewusst später entschieden, wenn das Backend-Fundament steht.

---

## 32. Harte Verbote

Nicht erlaubt:

- direkt Payment einbauen, bevor Produkte/Warenkorb/Bestellung sauber stehen
- Rechtstexte frei erfinden und als final speichern
- B2B und B2C vermischen
- Preise ohne Snapshot in Bestellungen speichern
- alte Bestellungen durch spätere Produktänderungen verändern
- Uploads ohne Validierung erlauben
- Adminrechte unsauber prüfen
- Tests überspringen
- Dokumentation vergessen
- lokale Sonderlösungen bauen, die später online nicht tragfähig sind
- Repo außerhalb des Projektordners anfassen
- frozen/locked Module ohne dokumentierten Grund ändern
- Anbieterlogik quer durch das System verstreuen
- ein Modul als fertig markieren, wenn Tests oder Doku fehlen

---

## 33. Zielbild in einem Satz

Alice Wonder Nails wird eine lokal sauber entwickelte, dokumentierte, testbare und später online deploybare Shop-Plattform für Nagelprodukte mit öffentlicher Website, Admin-System, B2C/B2B-Kundenlogik, Produktkatalog, Preisen, Warenkorb, Bestellungen, Galerie, Content, rechtlicher Struktur, modularer Architektur und professioneller Erweiterbarkeit.

---

## 34. Wichtigste Projektregel

Stabilität vor Geschwindigkeit.

Lieber ein Modul sauber fertig, dokumentiert, getestet und eingefroren als fünf halbe Baustellen, die später niemand mehr anfassen möchte, ohne vorher einen Priester für Legacy-Code zu rufen.
