# Deployment Plan

## Ziel

Langfristig soll das Backend onlinefähig deploybar werden. Diese Datei beschreibt die Phasen und Anforderungen.

## Phase 1: Local Development (✅ Arbeitsblock 01–14 GRÜN)

- Django-Projekt lokal startbar ✅
- `.env.example` vorbereitet ✅
- `backend/requirements.txt` erstellt ✅
- Statusskripte für Backend verfügbar ✅
- PostgreSQL lokal configured ✅
- Testlauf 304/304 grün ✅
- API v1 frozen und deployed (lokal) ✅

## Phase 2: Production Readiness (⚠️ Arbeitsblock 15: PRE-LIVE READY)

**Status nach AB 15:**

5 kritische Warnungen behoben (✅):
- ✅ W004 (SECURE_HSTS_SECONDS): 3600 aktiviert
- ✅ W008 (SECURE_SSL_REDIRECT): True in production.py
- ✅ W009 (SECRET_KEY): Env-Validierung 50+ chars
- ✅ W012 (SESSION_COOKIE_SECURE): True in production.py
- ✅ W016 (CSRF_COOKIE_SECURE): True in production.py

2 akzeptierte Pre-Live-HSTS-Warnungen (⚠️, werden Post-Live aktiviert):
- ⚠️ W005 (SECURE_HSTS_INCLUDE_SUBDOMAINS): False — wird nach Subdomain-Audit True
- ⚠️ W021 (SECURE_HSTS_PRELOAD): False — wird nach Domain-Setup True

Grund für W005/W021 Pre-Live: HSTS ist browser-seitig irreversibel. Erst nach vollem HTTPS-Testing und Subdomain-Audit aktivieren.

**Security Settings:**
- ✅ `base.py` — Foundation Hardening (X-Frame, Content-Type, Cookies)
- ✅ `local.py` — HTTP-freundliche Entwicklung
- ✅ `production.py` — HTTPS-only Härtung, ENV-basiert
- ✅ `SECRET_KEY` Management (env-basiert, 50+ chars)
- ✅ `ALLOWED_HOSTS` Management (explizit, komma-sep)
- ✅ `CSRF_TRUSTED_ORIGINS` Optional für Frontend-Domain
- ✅ HSTS Phase 1: 3600 default, W005/W021 Pre-Live

**Validation:**
- ✅ `.env.example` mit Production-Variablen dokumentiert
- ✅ `scripts/check_production_security.ps1` für Validierung
- ✅ Django `check --deploy` integriert
- ✅ 5 kritische Security-Warnungen adressiert
- ✅ 2 Pre-Live-HSTS-Warnungen dokumentiert

**Status nach AB 15:**
- ✅ Local: GRÜN (HTTP entwicklerfreundlich)
- ⚠️ Staging: GELB (HTTPS-ready mit Pre-Live-HSTS)
- ⚠️ Production: GELB (HTTPS ready, braucht echte Domain/Secrets)

## Phase 3: Staging Deployment (Future)

- Hosting auf Plattform mit PostgreSQL
- Test-Domain oder Subdomain
- Echte HTTPS/SSL-Zertifikat
- Production-ähnliche Umgebung
- E-Mail konfiguriert (Test-Provider)
- Logging/Monitoring aktiviert
- Smoke-Tests gegen Staging-URL

## Phase 4: Production Deployment (Future)

- Hosting auf Production-Plattform
- Production-Domain
- Production-SSL-Zertifikat
- Production-Secrets (KEY, Hosts, etc.)
- E-Mail von echtem Provider
- Production-Datenbank mit Backups
- Logging/Monitoring im Produktivmodus
- Error-Tracking (Sentry o.ä.)
- Rate-Limiting
- WAF / DDoS-Protection
- Disaster Recovery Plan

## Checkliste vor Deployment

### Local (AB 15 ⚠️ PRE-LIVE READY)
- ✓ `manage.py check --settings=config.settings.local` = 0 issues
- ✓ `manage.py check --deploy --settings=config.settings.production` = 2 warnings (W005, W021 Pre-Live)
  - W005 (HSTS_INCLUDE_SUBDOMAINS): Expected - aktiviert nach Subdomain-Audit
  - W021 (HSTS_PRELOAD): Expected - aktiviert nach Domain-DNS-Setup
- ✓ `pytest backend` = 304/304 PASS
- ✓ Migrations up to date
- ✓ `scripts/check_production_security.ps1` = bestanden
- ✓ 5 kritische Warnungen behoben (W004, W008, W009, W012, W016)

### Staging (Before Phase 3)
- [ ] Staging-Domain verfügbar
- [ ] SSL-Zertifikat provisioned
- [ ] PostgreSQL gehostet und erreichbar
- [ ] `DJANGO_SECRET_KEY` generiert und secure gespeichert
- [ ] `DJANGO_ALLOWED_HOSTS` auf Staging-Domain gesetzt
- [ ] E-Mail Provider konfiguriert
- [ ] Logging/Monitoring aktiviert
- [ ] Environment-Variablen gesetzt (nicht in Code)
- [ ] Production-Settings erfolgreich geladen
- [ ] smoke test bestanden (Health-Check, API-Endpoints)

### Production (Before Phase 4)
- [ ] Production-Domain registriert
- [ ] SSL-Zertifikat für Production
- [ ] PostgreSQL Production-ready (Backups, Monitoring)
- [ ] `DJANGO_SECRET_KEY` neu generiert für Production
- [ ] `DJANGO_ALLOWED_HOSTS` Production-Domain(s)
- [ ] HSTS erhöht nach vollem HTTPS-Testing (31536000 + Subdomains + Preload)
- [ ] E-Mail aus Production Provider
- [ ] Logging/Monitoring auf Production
- [ ] Error-Tracking (Sentry)
- [ ] Disaster Recovery Plan
- [ ] Security Audit bestanden
- [ ] Smoke Tests bestanden
- [ ] Rollback Plan bereit

