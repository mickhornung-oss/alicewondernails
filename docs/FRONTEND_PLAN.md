# Frontend Plan

## Status

AB 21 stellt die lokale Frontend-Foundation fuer Alice Wonder Nails bereit.
Der Stand ist eine lokale Shop-Demo auf Basis der vorhandenen read-only API.
Das Projekt ist weiterhin nicht live-ready.

## Tech-Stack

- Vite
- React
- React DOM
- React Router DOM
- `fetch()` API-Client
- eigenes CSS
- Vite Proxy fuer `/api` auf `http://127.0.0.1:8000`

Keine UI-Frameworks, kein Axios und keine Frontend-Tests in AB 21.

## Ordnerstruktur

```text
frontend/
|-- package.json
|-- vite.config.js
|-- index.html
|-- README.md
`-- src/
    |-- main.jsx
    |-- App.jsx
    |-- api/
    |   `-- client.js
    |-- components/
    |   |-- Header.jsx
    |   |-- Footer.jsx
    |   |-- ProductCard.jsx
    |   |-- PriceBox.jsx
    |   |-- LoadingState.jsx
    |   `-- ErrorState.jsx
    |-- pages/
    |   |-- Home.jsx
    |   |-- Categories.jsx
    |   |-- Products.jsx
    |   |-- ProductDetail.jsx
    |   |-- Info.jsx
    |   `-- NotFound.jsx
    `-- styles/
        `-- global.css
```

## Seiten

- `/`: Startseite mit Hero, Demo-Hinweis, Healthcheck und Kategorie-Vorschau.
- `/categories`: Kategorie-Karten aus der API.
- `/products`: Produktliste mit B2C/B2B-Umschaltung.
- `/products/:slug`: Produktdetail mit Varianten, Pricing und Versandinfo.
- `/info`: Legal-Metadaten, Zahlarten und Versandmethoden als lokale Demo-Info.
- `*`: einfache 404-Seite.

## Genutzte API-Endpunkte

- `GET /api/v1/health/`
- `GET /api/v1/catalog/categories/`
- `GET /api/v1/catalog/products/?customer_group=b2c|b2b`
- `GET /api/v1/catalog/products/<slug>/?customer_group=b2c|b2b`
- `GET /api/v1/pricing/products/<slug>/prices/?customer_group=b2c|b2b`
- `GET /api/v1/shipping/methods/?customer_group=b2c|b2b&country=DE`
- `GET /api/v1/payments/methods/?customer_group=b2c`
- `GET /api/v1/legal/active/?customer_group=b2c`

Alle URLs werden relativ ueber den Vite-Proxy angesprochen. Es ist keine
Backend-CORS-Aenderung vorgesehen.

## Demo-Hinweise

Die UI kennzeichnet den Stand als lokale Demo mit Demo-/Placeholder-Daten.
Es werden keine echten Rechtstexte, keine echten Lieferantendaten und keine
Live-Shop-Versprechen angezeigt.

## Nicht-Ziele in AB 21

- Kein Warenkorb
- Kein Checkout
- Kein Login/Auth
- Kein Payment-Flow
- Keine Admin-Oberflaeche
- Keine Backend-Aenderungen
- Keine API-Vertragsaenderungen
- Kein Deployment
- Keine echten Rechtstexte

## Spaetere Ausbauphasen

1. Frontend-Tests mit Vitest und React Testing Library.
2. Saubere Empty States und erweiterte Filter fuer den Produktkatalog.
3. Produktbilder und Medienstrategie, sobald Backend/Import dafuer bereit sind.
4. Warenkorb- und Checkout-UI erst nach ausdruecklicher Freigabe.
5. Auth/Login und B2B-Konto-Flows erst nach eigener Planung.

## Manueller lokaler Start

Terminal 1 - Backend:

```powershell
cd C:\Users\mickh\Desktop\alice-wondernails
.venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000 --settings=config.settings.local
```

Terminal 2 - Frontend:

```powershell
cd C:\Users\mickh\Desktop\alice-wondernails\frontend
npm run dev
```

Browser:

```text
http://127.0.0.1:3000
```

Agenten sollen den Dev-Server nicht dauerhaft blockierend starten.

## Browser-Checkliste AB 22

- Home: Seite laedt, Demo-Hinweis sichtbar, Backend/API-Status sichtbar, Kategorien-Vorschau laedt.
- Kategorien: Kategorien werden angezeigt, Karten sehen ordentlich aus, mobile Ansicht grob pruefen.
- Produkte: Produkte werden angezeigt, B2C/B2B-Umschaltung funktioniert, keine Warenkorb- oder Kaufbuttons sichtbar.
- Produktdetail: Details, Varianten, Preise und Versandinfo laden; B2C/B2B-Umschaltung pruefen.
- Fehlerfall: Nicht sichtbares Produkt oder unbekannter Slug zeigt eine verstaendliche Fehlermeldung.
- Info: Legal-Demo-Dokumente, Demo-/Placeholder-Hinweis, Versand- und Zahlarten-Infos erscheinen.
- 404: Unbekannte Route zeigt die NotFound-Seite.

## Browser-Befunde AB 23

- Home, Kategorien, Produkte, Produktdetail, Info und 404 wurden lokal im Browser gegen Backend und Vite-Proxy geprueft.
- API-Requests laufen ueber relative `/api/...` Pfade und den Vite-Proxy.
- Normale Seiten zeigten nach Favicon-Fix keine Console-Errors.
- Der absichtliche Fehlerfall fuer ein nicht sichtbares Produkt erzeugt erwartete 404-Netzwerkantworten und zeigt eine verstaendliche Error-State-Seite.
- Lokale Datenbank enthaelt zusaetzliche `Test-*` Kategorien/Produkte aus frueheren Tests oder lokalen Datenlaeufen. Nicht im Frontend bereinigt.
- Shipping-API liefert bei `country=DE` auch EU-Methoden. Frontend-Label wurde deshalb neutral auf "Versand Demo" geaendert; Backend/API wurde nicht geaendert.

## Naechste UI-Fix-Liste

- Lokale Demo-Daten bereinigen oder klaeren, warum `Test-*` Datensaetze in der lokalen DB sichtbar sind.
- Shipping-Country-Verhalten fachlich klaeren: API filtert aktuell nicht sichtbar nach Land.
- Optional: Empty States fuer leere Produktlisten und leere Versand-/Zahlartenlisten schaerfen.
- Optional: Mobile Header nach manuellem Feinschliff kompakter gestalten, falls gewuenscht.
