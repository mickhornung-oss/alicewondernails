# DEPLOYMENT CHECK - Alice Wonder Nails V1

## AKTUELLE SITUATION

**V1-Architektur hat sich geändert:**
- ❌ **Früher:** Reine statische Webseite (`public/` allein)
- ✅ **Jetzt:** FastAPI-Backend + SQLite-Datenbank erforderlich

**Technische Anforderungen für V1:**
- **Backend:** Python FastAPI-Server (dauerhaft laufend)
- **Datenbank:** SQLite (Schreibzugriff erforderlich)
- **Dateisystem:** Ordner `data/` außerhalb öffentlicher Bereiche
- **Session-Management:** Server-seitige Sessions
- **Admin-Interface:** Web-basierte HTML-Templates

---

## STRATO-KOMPATIBILITÄT: UNKLAR

### **Bekannte STRATO-Webspace-Eigenschaften:**
- ✅ **Statische Dateien:** HTML, CSS, JS, Bilder ✅ Funktioniert
- ✅ **PHP-Anwendungen:** Unterstützt ✅ Funktioniert  
- ❓ **Python FastAPI:** **NICHT BESTÄTIGT**
- ❓ **Dauerhaft laufende Prozesse:** **UNKLAR**
- ❓ **Schreibbare Verzeichnisse:** **UNKLAR**

### **Kritische Prüfpunkte:**

**1. Python-Runtime verfügbar?**
```bash
# Prüfung erforderlich:
python --version
python3 --version
pip --version
```

**2. FastAPI/Uvicorn installierbar?**
```bash
# Prüfung erforderlich:
pip install fastapi uvicorn
```

**3. Dauerhafter Prozess möglich?**
```bash
# Prüfung erforderlich:
nohup python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 &
```

**4. Schreibrechte außerhalb public/?**
```bash
# Prüfung erforderlich:
mkdir ../data
touch ../data/test.db
```

**5. Port-Binding möglich?**
- Standard-Webports (80/443) vs. Custom-Ports (8000)
- Reverse-Proxy-Konfiguration nötig?

---

## DEPLOYMENT-ALTERNATIVEN

### **Option A: STRATO-Native (falls möglich)**

**Voraussetzungen:**
- Python-Runtime verfügbar
- Dauerhaft laufende Prozesse erlaubt  
- Schreibbare Verzeichnisse außerhalb DocumentRoot
- Port-Management oder Reverse-Proxy

**Deployment:**
```bash
# Upload-Struktur:
/html/public/          # Statische Dateien
../backend/            # Python-Code  
../data/              # Datenbank + Exports
../requirements.txt   # Dependencies
../start_production.sh # Startskript
```

**Status:** 🔴 **UNBESTÄTIGT** - Bedarf Tarif-Prüfung

---

### **Option B: Hybrid-Deployment (Empfohlung bei STRATO-Limitierung)**

**Frontend:** STRATO Webspace (statisch)
**Backend:** Externe Python-Hosting-Plattform

**Externe Backend-Optionen:**
- **Railway.app** (kostenlos bis $5/Monat)  
- **Render.com** (kostenlos mit Limits)
- **PythonAnywhere** (€4/Monat)
- **DigitalOcean App Platform** ($5/Monat)
- **Heroku** (€7/Monat)

**Konfiguration:**
```javascript
// Frontend: API-Calls zu externem Backend
const API_BASE = 'https://alice-backend.railway.app/api';
```

**Vorteile:**
- ✅ STRATO bleibt für Frontend
- ✅ Backend skalierbar
- ✅ Keine STRATO-Python-Abhängigkeit

**Status:** 🟢 **MACHBAR** - Backup-Plan

---

### **Option C: Vollständige Alternative (bei STRATO-Inkompatibilität)**

**Kompletter Wechsel zu Python-freundlichem Hosting:**

**Empfohlene Plattformen:**
- **Vercel** (Frontend) + **Railway** (Backend)
- **Netlify** (Frontend) + **Render** (Backend)  
- **GitHub Pages** (Frontend) + **PythonAnywhere** (Backend)

**Status:** 🟢 **MACHBAR** - Vollalternative

---

### **Option D: V1-Fallback (statisch ohne Backend)**

**Falls Backend-Hosting nicht sofort verfügbar:**
- Frontend auf STRATO hochladen
- Formular deaktivieren oder als "Kommt bald" markieren
- Später Backend nachrüsten

**Einschränkungen:**
- ❌ Kein Lead-Management
- ❌ Kein Admin-Interface
- ❌ Nur statische Präsentation

**Status:** 🟡 **NOTLÖSUNG** - Temporärer Plan

---

## STRATO-TARIFPRÜFUNG ERFORDERLICH

### **Zu klären vor Deployment:**

**1. Aktueller STRATO-Tarif:**
- Welcher Webspace-Tarif ist aktiv?
- Welche Sprachen/Technologien sind erlaubt?
- Dokumentation: Support-Anfrage oder Tarif-Details prüfen

**2. Python-Support:**
```bash
# Via SSH/Shell (falls verfügbar):
ssh username@strato-server.de
python --version
which python3
pip --version
```

**3. Prozess-Management:**
```bash
# Dauerhaft laufende Prozesse testen:
nohup python3 -c "print('Test')" &
ps aux | grep python
```

**4. Dateisystem-Rechte:**
```bash
# Außerhalb DocumentRoot schreibbar?
cd ..
mkdir test_data
echo "test" > test_data/test.txt
```

**5. Port-Management:**
- Welche Ports sind verfügbar?
- Reverse-Proxy-Konfiguration möglich?
- Custom-Domain-Routing verfügbar?

---

## EMPFOHLENES VORGEHEN

### **Phase 1: STRATO-Fähigkeiten klären (KRITISCH)**
1. **Support-Anfrage an STRATO:**
   - Python-Runtime verfügbar?
   - Dauerhaft laufende Python-Prozesse erlaubt?
   - FastAPI-Deployment möglich?

2. **Tarif-Dokumentation prüfen:**
   - Aktuelle Tarif-Features checken
   - Python/CGI-Support dokumentiert?

3. **Test-Deployment (falls SSH möglich):**
   - Kleines Python-Script hochladen
   - FastAPI minimal-setup testen

### **Phase 2: Deployment-Strategie wählen**
**Falls STRATO Python-kompatibel:**
- ✅ Native Deployment (Option A)

**Falls STRATO nur statisch/PHP:**  
- ✅ Hybrid-Deployment (Option B) - **EMPFOHLEN**

**Falls kompletter Wechsel nötig:**
- ✅ Alternative Plattform (Option C)

### **Phase 3: Fallback bereithalten**
- Statische Version auf STRATO (Option D)
- Backend später nachrüsten

---

## RISIKOBEWERTUNG

### 🔴 **KRITISCHE RISIKEN:**
- **STRATO-Inkompatibilität:** FastAPI möglicherweise nicht unterstützt
- **Deployment-Verzögerung:** Zusätzliche Plattform-Setup nötig
- **Kosten:** Externes Backend-Hosting ($0-15/Monat)

### 🟡 **MODERATE RISIKEN:**
- **Komplexität:** Hybrid-Setup erfordert CORS-Konfiguration
- **Wartung:** Zwei getrennte Deployments
- **Performance:** Zusätzliche API-Latenz bei externem Backend

### 🟢 **LÖSBARE HERAUSFORDERUNGEN:**
- **Backup-Optionen verfügbar:** Mehrere funktionsfähige Alternativen
- **Skalierbarkeit:** Externe Backends oft besser skalierbar
- **Kosten kontrollierbar:** Kostenlose/günstige Optionen verfügbar

---

## STATUS: ROT - DEPLOYMENT-BLOCKER

**Problem:** STRATO-Kompatibilität für FastAPI **NICHT BESTÄTIGT**

**Nächste kritische Schritte:**
1. **SOFORT:** STRATO-Tarif auf Python-Support prüfen
2. **Bei Inkompatibilität:** Hybrid-Deployment vorbereiten
3. **Backup:** Statische Version als Notlösung bereithalten

**Upload kann erst erfolgen nach:**
- ✅ STRATO-Fähigkeiten geklärt ODER
- ✅ Alternative Deployment-Strategie implementiert

**Zeitaufwand geschätzt:**
- STRATO-Klärung: 1-2 Tage (Support-Antwort)
- Hybrid-Setup: 2-4h (technische Umsetzung)
- Statische Fallback: 30 Min (Formular deaktivieren)

---

## KEINE ANNAHMEN GETROFFEN

**Wichtig:** Diese Analyse macht **KEINE** Annahmen über STRATO-Fähigkeiten.  
Deployment-Fähigkeit muss durch **konkrete Tests** oder **Support-Anfrage** geklärt werden.

FastAPI ist **NICHT** garantiert kompatibel mit Standard-Webspace-Hosting.