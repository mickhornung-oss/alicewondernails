# V1 SICHERHEITSHINWEISE

## Lokale Entwicklung

Für die lokale Entwicklung ist die aktuelle Konfiguration ausreichend:
- `HTTPS_ONLY_SESSIONS=false` erlaubt HTTP für localhost
- Admin-Zugang nur direkt per URL, nicht öffentlich verlinkt
- SQLite-Datenbank außerhalb des public-Ordners

## KRITISCH FÜR PRODUKTION

Bevor das System produktiv geht, MÜSSEN folgende Sicherheitsmaßnahmen getroffen werden:

### 1. HTTPS erzwingen
```
HTTPS_ONLY_SESSIONS=true
```
**OHNE HTTPS sind Admin-Sessions kompromittierbar!**

### 2. Starke Secrets
- Neue `SESSION_SECRET` generieren:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(64))"
  ```
- Starkes Admin-Passwort setzen

### 3. CORS anpassen
- `CORS_ORIGIN_REGEX` auf produktive Domain setzen

### 4. Server-Konfiguration
- Reverse-Proxy (nginx) für TLS-Terminierung
- HSTS-Header aktivieren
- .env-Datei sicher ablegen (nicht im Webroot)

## Aktuelle Sicherheitsfunktionen

✅ **Implementiert:**
- CSRF-Schutz für alle Admin-Aktionen
- Rate Limiting (Login + Public API)
- Honeypot-Schutz im Formular
- Session-basierte Admin-Authentifizierung
- Passwort-Hashing (PBKDF2)
- SQL-Injection-Schutz (Parameterized Queries)

⚠️ **Für Produktion nötig:**
- HTTPS-Erzwingung (konfigurierbar)
- Audit-Logs für Admin-Aktionen (spätere Version)
- Backup-Strategie (spätere Version)
- Monitoring (spätere Version)

## .env-Datei Sicherheit

Die `.env`-Datei enthält sensitive Daten und ist in `.gitignore` aufgelistet.

**Für Produktion:**
- .env außerhalb des Web-Roots ablegen
- Dateiberechtigungen: nur Owner readable (600)
- Alternativ: Umgebungsvariablen direkt setzen