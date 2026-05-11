# Security Plan

## Ziel

Sicherheit ist von Anfang an ein Teil des Backend-Fundaments. Dieses Dokument beschreibt die Security-Strategie für alle Phasen: Local Development, Staging, Production.

## Fokus für Arbeitsblock 01–14

- `.env` nicht ins Git committen
- `.env.example` als Vorlage
- `.gitignore` schützt lokale Secrets
- Django SecurityMiddleware aktiviert
- Healthcheck ohne vertrauliche Daten
- CORS-Härtung
- HTTPS für Produktion (später)
- starke Passwortrichtlinien
- Admin-Zugriffsschutz
- sichere Datenhaltung für Kunden und Bestellungen

## Arbeitsblock 15: Production Security Readiness

### Security Layers in Settings (AB 15)

**base.py – Foundation Hardening (alle Umgebungen)**
- `X_FRAME_OPTIONS = 'DENY'` — Clickjacking-Schutz
- `SECURE_CONTENT_TYPE_NOSNIFF = True` — Content-Type-Sniffing verhindern
- `SESSION_COOKIE_HTTPONLY = True` — Session-Cookie vor JS-Zugriff geschützt (mandatory)
- `CSRF_COOKIE_HTTPONLY = False` — Frontend braucht CSRF-Token für Shop-Flows
- `SESSION_COOKIE_SAMESITE = 'Lax'` — CSRF-Protection (lokal permissiv)
- `CSRF_COOKIE_SAMESITE = 'Lax'` — CSRF-Protection (lokal permissiv)

**local.py – Development-Override (HTTP-freundlich)**
- `DEBUG = True` — Entwicklungsmodus
- `SECURE_SSL_REDIRECT = False` — Lokal HTTP erlaubt
- `SESSION_COOKIE_SECURE = False` — Nicht über HTTPS erzwungen
- `CSRF_COOKIE_SECURE = False` — Nicht über HTTPS erzwungen
- `SECURE_HSTS_SECONDS = 0` — HSTS deaktiviert für HTTP
- `ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'localhost:8000']`

**production.py – Production Hardening (HTTPS-only)**
- `DEBUG = False` — Production-Modus (zwingend)
- `SECURE_SSL_REDIRECT = True` — HTTPS erzwungen
- `SESSION_COOKIE_SECURE = True` — Nur über HTTPS
- `CSRF_COOKIE_SECURE = True` — Nur über HTTPS
- `SECRET_KEY` — Muss lang (50+), random und aus ENV kommen
- `ALLOWED_HOSTS` — Explizit aus ENV, kein Wildcard
- `CSRF_TRUSTED_ORIGINS` — Optional aus ENV, z.B. für Frontend-Subdomain

### HSTS Strategy (Conservative Approach, Phase 1: Pre-Live)

HTTP Strict Transport Security wird **konservativ in Phasen** konfiguriert:

**Phase 1: Pre-Live (AB 15 Status)**
- `DJANGO_SECURE_HSTS_SECONDS=3600` (1 Stunde) — ✅ aktiviert
- `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=False` — ⚠️ nicht aktiviert (W005, wird nach Subdomain-Audit True)
- `DJANGO_SECURE_HSTS_PRELOAD=False` — ⚠️ nicht aktiviert (W021, wird nach Domain-Setup True)

Rationale: HSTS ändert Browser-Verhalten dauerhaft und irreversibel. Falsche Konfiguration (z.B. Subdomains ohne HTTPS) führt zu unlösbaren HTTPS-Problemen. Daher: Erst mit konservativen Werten Pre-Live testen.

**Phase 2: Post-Live (nach 48h erfolgreicher Production)**
- Nach 48h ohne HSTS-Fehler: `DJANGO_SECURE_HSTS_SECONDS=31536000` (1 Jahr)
- Nach Subdomain-Audit: `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=True` (nur wenn ALL subdomains HTTPS)
- Nach Domain-DNS-Setup: `DJANGO_SECURE_HSTS_PRELOAD=True` (dann bei preload-list.com registrieren)

### SECRET_KEY Management

**Local Development:**
- `.env` hat Demo-Key (nicht commitet)
- Fallback in `base.py`: `'change-me'` (plaintext in base.py erlaubt, nur für Demo)

**Production:**
- MUSS aus `DJANGO_SECRET_KEY` ENV-Variable kommen
- MUSS 50+ Zeichen lang sein
- DARF NICHT mit `django-insecure-` beginnen (Auto-Generation erkannt)
- Generation: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

### ALLOWED_HOSTS Management

**Local Development:**
- Default: `['localhost', '127.0.0.1', 'localhost:8000']`
- Optional via ENV `DJANGO_ALLOWED_HOSTS=...` überschreibbar

**Production:**
- MUSS explizit aus `DJANGO_ALLOWED_HOSTS` ENV kommen
- Format: komma-separiert, keine Leerzeichen (z.B. `example.com,www.example.com`)
- Mindestens ein gültiger Hostname erforderlich
- Keine Wildcards erlaubt

### CSRF Protection

**base.py (Foundation):**
- `CSRF_COOKIE_HTTPONLY = False` — Frontend muss Token lesen können (für Shop-Flows)
- `CSRF_COOKIE_SAMESITE = 'Lax'` — Lokal CSRF-Protection

**production.py (Optional):**
- `CSRF_TRUSTED_ORIGINS` — Falls Frontend auf anderer Domain (z.B. `https://shop.example.com` vs `https://api.example.com`)
- Format: komma-separiert URLs (z.B. `https://example.com,https://www.example.com`)

### Validation & Checks

**Local Check:**
```bash
.venv\Scripts\python.exe backend\manage.py check --settings=config.settings.local
```

**Production Check (mit Dummy-ENV):**
```bash
powershell -ExecutionPolicy Bypass -File scripts\check_production_security.ps1
```

Dieses Script:
- Setzt temporäre sichere Dummy-Werte für ENV (nicht gespeichert)
- Führt `manage.py check --deploy` aus
- Zeigt alle Warnungen und nächste Schritte

## Späteren Phase: Production Deployment

- Echter Production-Domain und Zertifikat
- Echter SECRET_KEY (nicht demo)
- Echter ALLOWED_HOSTS
- Email-Provider konfiguriert
- Logging in Production-Service (z.B. ELK, CloudWatch)
- Error-Tracking (z.B. Sentry)
- Rate-Limiting
- DDoS-Protection
- WAF (Web Application Firewall)

