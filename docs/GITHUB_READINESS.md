# GITHUB READINESS - Alice Wonder Nails V1

## Ziel

Dieses Dokument beschreibt, was fuer ein sicheres GitHub-Repository freigegeben ist und was lokal bleiben muss.

## Was ins Repository darf

- `README.md`
- `public/`
- `dist_strato/`
- `docs/`
- `backend/` (als lokaler Entwicklungsstand ohne Secrets und ohne Laufzeitdaten)
- `scripts/`
- `.gitignore`
- `backend/requirements.txt`

## Was NICHT ins Repository darf

- `.env` und weitere `.env.*` Dateien (ausser `.env.example`)
- `data/`
- `*.sqlite`, `*.sqlite3`
- `*.csv`
- `__pycache__/`, `*.pyc`
- `.venv/`, `venv/`
- lokale Logs und temporaere Dateien
- Session-/Cookie-Dateien wie `cookies.txt`
- echte Leads, Exportdateien und echte Kundendaten
- Zugangsdaten, Passwoerter, Session-Secrets, API-Secrets

## Aktueller Status (V1)

- Statische Mehrseiten-Version fuer STRATO ist vorbereitet.
- Das FastAPI/SQLite-Backend ist lokal verfuegbar.
- Backend/Admin ist auf STRATO Basic nicht live.
- Kein fertiger Shop und kein produktives Backend-Live-System in V1.

## Bekannte Grenzen

- STRATO Basic hostet die statische Version, nicht das Python-Backend.
- Lead-Erfassung, Admin-Login, CSV-Export und Session-Logik sind in der statischen V1 nicht aktiv.
- Medien- und Inhaltspflege bleibt manuell.

## Deployment-Hinweis

- Fuer STRATO nur den Inhalt von `dist_strato/` hochladen.
- Referenz: `docs/STRATO_STATIC_DEPLOYMENT.md` und `docs/STRATO_UPLOAD_FINAL_CHECK.md`.

## V2-Ausblick

- Reaktivierung des lokalen Backends in einem geeigneten Hosting-Setup.
- Wiederanbindung von Lead-Erfassung und Admin-Funktionen in einer serverfaehigen Umgebung.
- Erweiterte Betriebs- und Release-Prozesse (z. B. CI, strukturierte Release-Checks).

## Push-Regel

- Kein Push ohne explizite Freigabe.