# LOCAL_RUNBOOK

## Lokal starten

1. PowerShell im Projektordner `C:\Users\mickh\Desktop\alice-wondernails` öffnen.
2. Startskript ausführen:
   `powershell -ExecutionPolicy Bypass -File .\scripts\start_local.ps1`
3. Das Skript startet FastAPI auf `127.0.0.1:8000` und zeigt die URLs an.

## Lokal stoppen

Server sauber stoppen mit:
`powershell -ExecutionPolicy Bypass -File .\scripts\stop_local.ps1`

Das Skript beendet nur den Uvicorn-Prozess dieses Projekts (per PID-Datei).

## Lokale Tests ausführen

Schnelltest ausführen mit:
`powershell -ExecutionPolicy Bypass -File .\scripts\test_local.ps1`

Geprüft werden u. a.:
- `/health`
- Landingpage
- Admin-Login
- Admin-CSS
- Test-Lead via API
- Sichtbarkeit des Test-Leads in SQLite

## URLs

- Landingpage: `http://127.0.0.1:8000/public/index.html`
- Admin-Login: `http://127.0.0.1:8000/admin/login`
- Health: `http://127.0.0.1:8000/health`

## Admin-Zugang

Der Adminbereich wird nicht öffentlich auf der Startseite verlinkt.
Zugang nur direkt über:
`http://127.0.0.1:8000/admin/login`

Zugangsdaten kommen aus `.env`.
Keine Zugangsdaten in HTML, JS oder README hinterlegen.

## Datenablage

- SQLite-Datenbank: `data/db/alicewonder_v1.sqlite`
- CSV-Exporte: `data/exports/`
- Laufzeitdateien (PID/Logs): `data/runtime/`

Die Datenbank liegt absichtlich außerhalb von `public/` und ist nicht öffentlich ausgeliefert.

## Darf nicht ins Repo

- `.env`
- `data/`
- `*.sqlite`, `*.sqlite3`
- `data/exports/*.csv`
- `__pycache__/`, `*.pyc`
- Logs und lokale virtuelle Umgebungen

Regeln dafür sind in `.gitignore` gesetzt.

## Typische Fehler und Lösungen

1. **`start_local.ps1` meldet, dass Python fehlt**
   - Python installieren und prüfen mit `python --version`.

2. **Port 8000 bereits belegt**
   - `.\scripts\stop_local.ps1` ausführen.
   - Falls notwendig prüfen, ob ein anderer lokaler Dienst Port 8000 nutzt.

3. **Admin-Login funktioniert nicht**
   - Prüfen, ob `.env` vorhanden ist.
   - Prüfen, ob `ADMIN_USERNAME` und `ADMIN_PASSWORD_HASH` korrekt gesetzt sind.
   - Server neu starten.

4. **`test_local.ps1` schlägt fehl**
   - Zuerst `.\scripts\start_local.ps1` ausführen.
   - Danach `.\scripts\test_local.ps1` erneut ausführen.

5. **CSS im Admin lädt nicht**
   - Prüfen, ob `public/assets/css/admin.css` vorhanden ist.
   - Prüfen, ob die URL `http://127.0.0.1:8000/static/css/admin.css` erreichbar ist.
