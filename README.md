# Alice Wonder Nails

Statische V1-Mehrseiten-Webseite für Alice Wonder Nails mit lokalem FastAPI/SQLite-Backend als Entwicklungsbasis für spätere Ausbaustufen.

## Aktueller Status

* V1 statisch für STRATO vorbereitet
* Backend ist lokal vorhanden, aber nicht live auf STRATO Basic
* Kein fertiger Shop und kein produktives Backend-Live-System in dieser V1

## Features

* Statische Mehrseiten-Webseite
* Galerie
* Videos
* Kontaktlinks
* Impressum und Datenschutz
* Lokales Backend/Admin als spätere V2-Grundlage

## Tech Stack

* HTML
* CSS
* JavaScript
* Python mit FastAPI (lokal)
* SQLite (lokal)

## Lokaler Start

* Statisch: `dist_strato/index.html` direkt im Browser öffnen
* Backend lokal: siehe `docs/LOCAL_RUNBOOK.md`

## Deployment

* STRATO Upload über den Inhalt von `dist_strato/`
* Hintergrund und Grenzen: `docs/STRATO_STATIC_DEPLOYMENT.md`

## Sicherheit

Folgende Inhalte werden nicht versioniert:

* `.env`
* `data/`
* `*.sqlite`, `*.sqlite3`
* `*.csv`
* Caches, Logs und lokale Entwicklungsartefakte

Siehe dazu auch `.gitignore` und `docs/GITHUB_READINESS.md`.

## Wichtige Hinweise

* Keine echten Kundendaten im Repository speichern
* Keine Zugangsdaten, Session-Secrets oder Exportdateien committen

## Pflichtdokumente

* Oberste Regeln: `docs/PROJECT_RULES.md`
* Laufendes Arbeitsprotokoll: `docs/PROGRESS.md`
* STRATO Upload Check: `docs/STRATO_UPLOAD_FINAL_CHECK.md`
