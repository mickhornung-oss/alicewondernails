# Cleanup Plan

Dieser Plan dokumentiert den aktuellen Bereinigungs- und Neuaufbau-Prozess fuer die neue V2-Shop-Version.

## Grundsatz ab Arbeitsblock 01.4

Der Nutzer hat den kompletten Projektordner extern gesichert. Deshalb werden alte V1-, STRATO-, Archiv- und Legacy-Reste nicht mehr im aktiven Projektordner aufbewahrt.

Es werden keine neuen Archivordner im Projektordner angelegt. Nicht mehr verwenden:

- `public_v1_archive/`
- `backend_v1_archive/`
- `*_archive/`
- `legacy_archive/`
- `old/`
- `backup/`
- `strato_archive/`

## Durchgefuehrte harte Bereinigung

| Datei/Ordner | Bewertung | Aktion | Status |
|---|---|---|---|
| `backend_v1_archive/` | altes FastAPI-/SQLite-Backend | geloescht | abgeschlossen |
| `public_v1_archive/` | alte statische V1-Webseite | geloescht | abgeschlossen |
| `public/` | alte statische V1-Struktur | nicht mehr vorhanden | abgeschlossen |
| `dist_strato/` | altes STRATO-Uploadpaket | nicht mehr vorhanden | abgeschlossen |
| `modules/` | alte V1-Planungsplatzhalter | geloescht | abgeschlossen |
| `data/` | alte lokale Runtime-Daten, SQLite, Exporte, Logs | geloescht | abgeschlossen |
| `frontend/` | leerer Platzhalter ohne aktuellen V2-Nutzen | geloescht | abgeschlossen |
| `.codex/`, `.vscode/`, `cookies.txt` | lokale Hilfs-/Session-Artefakte | geloescht | abgeschlossen |
| `scripts/start_local.ps1`, `scripts/stop_local.ps1`, `scripts/test_local.ps1` | alte lokale V1/FastAPI-Skripte | geloescht | abgeschlossen |
| V1-/STRATO-/Video-Dokumente in `docs/` | nicht mehr V2-relevant | geloescht | abgeschlossen |
| Python- und pytest-Caches | generierte Artefakte | geloescht | abgeschlossen |

## Behaltene V2-Struktur

- `backend/` - neue Django-V2-Struktur
- `docs/` - V2-Dokumentation
- `docs/modules/` - Modul-Dokumentation fuer V2
- `scripts/` - V2-Skripte
- `.gitignore`
- `README.md`
- `CHANGELOG.md`
- `.env.example` und `backend/.env.example` mit Platzhaltern
- `.env` lokal, ignoriert
- `.venv/` lokal, ignoriert

## Offene Bereinigung

Keine bekannten V1-/STRATO-/Archivordner und keine leeren Platzhalterordner im aktiven Projektbaum.

PostgreSQL-Authentifizierung bleibt ein Infrastrukturthema und wird nicht durch die Bereinigung geloest.
