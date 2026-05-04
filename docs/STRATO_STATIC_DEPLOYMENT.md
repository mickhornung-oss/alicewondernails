# STRATO STATIC DEPLOYMENT - Alice Wonder Nails V1

## Status: Statische Version für STRATO erstellt

**Datum:** 2026-05-03  
**Version:** V1 Statisch  
**Upload-Paket:** `dist_strato/`

---

## Warum statisch?

**STRATO Hosting Basic unterstützt kein dauerhaftes FastAPI/Python-Backend.**

Das ursprünglich entwickelte FastAPI-Backend mit SQLite-Datenbank, Admin-Bereich und Lead-Management funktioniert perfekt lokal, kann aber nicht auf STRATO Basic gehostet werden, da:

- Keine dauerhaft laufenden Python-Prozesse unterstützt werden
- Kein uvicorn/FastAPI-Server verfügbar ist
- Nur statische Dateien und PHP unterstützt werden

**Lösung:** Statische V1-Version für STRATO-Upload mit E-Mail-Kontakt.

---

## Was ist in der statischen V1?

### ✅ **ENTHALTEN:**
- **Landingpage:** `index.html` mit allen finalen Texten
- **Rechtliche Seiten:** `impressum.html`, `datenschutz.html`
- **Echte Medien:** 5 Galerie-Bilder, 5 Videos, Logo
- **Kontakt:** E-Mail-Link (info@alicewondernails.de) und Instagram-Link
- **Navigation:** Alle Seiten verlinkt und funktional
- **Responsive Design:** Desktop + Mobile optimiert
- **Kartensymbole:** Schwarz mit lila Rahmen
- **Header-Layout:** Logo und Navigation nebeneinander

### ❌ **NICHT ENTHALTEN:**
- **Backend:** Kein FastAPI-Server
- **Datenbank:** Keine SQLite-Speicherung
- **Admin-Bereich:** Kein Login/Dashboard
- **Formular:** Keine Lead-Erfassung
- **CSV-Export:** Kein Lead-Management
- **Session-Management:** Keine serverseitige Logik

---

## Upload-Struktur

```
dist_strato/                    # Upload-Basis für STRATO
├── index.html                  # ✅ Startseite (Hero)
├── ueber-uns.html             # ✅ Markenvorstellung + Designerin + Designs
├── galerie.html               # ✅ 5 Bilder (2-2-1)
├── videos.html                # ✅ 5 Videos (2-2-1)
├── kontakt.html               # ✅ Kontakt / Early Access (mailto + Instagram)
├── shop.html                  # ✅ Shop kommt bald + Zusammenarbeit
├── impressum.html             # ✅ Rechtliche Seite
├── datenschutz.html           # ✅ Angepasst für statische Version
└── assets/                    # ✅ Alle Assets
    ├── css/
    │   └── style.css          # ✅ Angepasstes CSS
    ├── js/
    │   └── main.js            # ✅ Statische Version (kein API-Call)
    ├── logo/
    │   └── Logo fest.png      # ✅ Echtes Logo
    ├── images/
    │   └── Bilder Alice/      # ✅ 5 echte Galerie-Bilder
    └── videos/
        └── Video Alice/       # ✅ 5 Videos (.mov Format)
```

---

## Was wurde geändert für die statische Version?

### **1. Formular → E-Mail-Kontakt:**
**Vorher:** Aktives Kontaktformular mit API-Call zu `/api/lead`  
**Jetzt:** Statische Kontaktbox mit:
- E-Mail-Button: `mailto:info@alicewondernails.de`
- Instagram-Button: `https://www.instagram.com/alicewonder_nails/`
- Info-Text: "Kontakt und Early Access laufen aktuell über E-Mail oder Instagram."

### **2. JavaScript bereinigt:**
**Vorher:** Formular-Submit-Logic, Fetch-API, Error-Handling  
**Jetzt:** Nur Splashscreen und Animationen, Kommentar "Kontakt und Early Access laufen aktuell über E-Mail oder Instagram."

### **3. Datenschutz angepasst:**
**Vorher:** Beschreibung der Backend-Datenerfassung  
**Jetzt:** "Diese Webseite enthält aktuell keine aktive Datenerfassung über Formulare. Kontakt erfolgt über E-Mail oder Instagram."

### **4. Alle finalen Texte eingesetzt:**
- **Hero:** "Willkommen im kleinen Wunderland der Nägel" + vollständige Beschreibung
- **Markenvorstellung:** "Ein kleines Wunder entsteht" + Aufbau-Geschichte
- **Designerin:** Persönliche Vorstellung der jungen Designerin
- **Galerie/Videos:** Ansprechende Einleitungstexte
- **Kontakt:** "Sei von Anfang an dabei" + klare Kontaktangaben

### **5. Header-Layout verbessert:**
**Vorher:** Logo und Navigation übereinander gestapelt  
**Jetzt:** Logo links, Navigation rechts daneben (Desktop), kompakter und professioneller

### **6. Kartensymbole korrigiert:**
**Vorher:** Lila Kartensymbole  
**Jetzt:** Schwarze Kartensymbole mit lila Rahmen (wie gewünscht)

---

## Deployment auf STRATO

### **Upload-Anweisungen:**
1. **FTP/SFTP:** Alle Dateien aus `dist_strato/` in das STRATO-Webverzeichnis hochladen
2. **Hauptdatei:** `index.html` als Startseite
3. **Pfade:** Alle relativen Pfade funktionieren automatisch
4. **Domain:** Nach Upload unter der Domain erreichbar

### **Test-Checklist nach Upload:**
- ✅ Startseite lädt (index.html)
- ✅ Logo wird angezeigt
- ✅ Navigation funktioniert (Impressum, Datenschutz)
- ✅ Bilder werden geladen (5 Galerie-Bilder)
- ✅ Videos werden geladen (Browser-abhängig, .mov Format)
- ✅ E-Mail-Link öffnet Mailprogramm
- ✅ Instagram-Link öffnet in neuem Tab
- ✅ Mobile Ansicht funktioniert
- ✅ Rechtliche Seiten erreichbar

---

## Video-Kompatibilität

**⚠️ BEKANNTES ISSUE:** Videos sind im .mov Format und haben **40-50% Browser-Inkompatibilität**.

**Status:**
- ✅ **Funktioniert:** Safari (Desktop/Mobile), Chrome Desktop
- ❌ **Problematisch:** Firefox, Edge Mobile, Chrome Mobile
- ✅ **Fallback:** Download-Links für alle Videos implementiert

**Für V2 empfohlen:** Konvertierung zu MP4/H.264 für bessere Browser-Kompatibilität.

---

## Keine Backend-Funktionen live

**Wichtig:** Alle Backend-Features sind **DEAKTIVIERT** für die statische Version:

| Feature | Status | Ersatz |
|---------|--------|---------|
| Lead-Erfassung | ❌ Deaktiviert | E-Mail-Kontakt |
| Admin-Login | ❌ Nicht verfügbar | - |
| CSV-Export | ❌ Nicht verfügbar | - |
| Datenbank | ❌ Nicht verfügbar | - |
| Session-Management | ❌ Nicht verfügbar | - |

**Kontakt erfolgt über:**
- E-Mail: info@alicewondernails.de
- Instagram: @alicewonder_nails

---

## Spätere Backend-Integration (V2/V3)

**Für zukünftige Versionen mit Backend-Funktionen:**

### **Option A: Hybrid-Deployment**
- **Frontend:** STRATO (statisch)
- **Backend:** Render/Railway/PythonAnywhere
- **API-Calls:** Von STRATO zu externem Backend

### **Option B: Vollständige Alternative**
- **Komplett-Umzug:** Vercel/Netlify + Backend-Service
- **Volle Funktionalität:** FastAPI + SQLite + Admin

### **Option C: STRATO + PHP**
- **Umbau:** Backend von Python auf PHP (falls STRATO PHP unterstützt)
- **Datenbank:** MySQL statt SQLite

---

## Aktueller Stand: UPLOAD-READY

**✅ ALLES BEREIT FÜR STRATO-UPLOAD:**

1. **dist_strato/** Paket vollständig
2. **Alle Pfade relativ** und funktional
3. **Finale Texte** eingesetzt
4. **Statische Version** funktionsfähig
5. **Rechtliche Seiten** angepasst
6. **E-Mail-Kontakt** implementiert
7. **Mobile responsive** optimiert

**Nächster Schritt:** Upload nach STRATO und Test der Live-Version.

---

## Backup der Backend-Version

**Das vollständige FastAPI-Backend bleibt erhalten in:**
- `backend/` (alle Python-Dateien)
- `data/` (SQLite-Datenbank)
- `scripts/` (lokale Start-Skripte)
- `.env` (lokale Konfiguration)

**Lokal weiter nutzbar:**
```bash
powershell -ExecutionPolicy Bypass -File .\scripts\start_local.ps1
```

---

**Statische V1 ist bereit für STRATO-Deployment! 🚀**