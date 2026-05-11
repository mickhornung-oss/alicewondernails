# Alice Wonder Nails Frontend

Lokale Vite + React Frontend-Demo fuer die V2 Shop-Plattform.

## Stack

- Vite
- React
- React DOM
- React Router DOM
- `fetch()` fuer API-Aufrufe
- eigenes CSS ohne UI-Framework

## Voraussetzungen

- Backend separat starten:

```powershell
powershell -ExecutionPolicy Bypass -File ..\scripts\start_backend.ps1
```

- Demo-Daten lokal importieren, falls die Datenbank noch leer ist:

```powershell
cd ..
.venv\Scripts\python.exe backend\manage.py import_demo_csv --settings=config.settings.local
```

## Lokale Frontend-Befehle

```powershell
cd frontend
npm install --no-audit --no-fund
npm run build
npm run dev
```

Der Dev-Server ist fuer manuelle lokale Nutzung gedacht. Agenten sollen ihn nicht
dauerhaft starten.

## API Proxy

Vite leitet lokale Frontend-Anfragen weiter:

```text
/api -> http://127.0.0.1:8000
```

Der API-Client verwendet deshalb nur relative URLs wie `/api/v1/catalog/products/`.

## Seiten

- `/` - Startseite mit API-Status und Kategorie-Vorschau
- `/categories` - Kategorien
- `/products` - Produktliste mit B2C/B2B-Umschaltung
- `/products/:slug` - Produktdetail mit Pricing und Versandinfo
- `/info` - Legal-, Versand- und Zahlarten-Demo-Informationen

## Bewusste Nicht-Ziele

- Kein Warenkorb
- Kein Checkout
- Kein Payment-Flow
- Kein Login/Auth
- Keine Admin-Oberflaeche
- Keine echten Rechtstexte
- Keine echten Lieferantendaten
- Kein Live-Shop
- Kein Deployment

Status: Frontend-Foundation ready fuer lokale Entwicklung und weitere
Shop-Demo-Ausbaustufen.
