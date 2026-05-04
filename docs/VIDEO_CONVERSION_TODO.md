# VIDEO CONVERSION TODO - Alice Wonder Nails

## AKTUELLE SITUATION

**Problem:** 5 Videos im MOV-Format mit 40-50% Browser-Inkompatibilität
**Betroffene Dateien:**
- `public/assets/videos/Video Alice/Video_1.mov`
- `public/assets/videos/Video Alice/Video_2.mov`
- `public/assets/videos/Video Alice/Video_3.mov`
- `public/assets/videos/Video Alice/Video_4.mov`
- `public/assets/videos/Video Alice/Video_5.mov`

**Browser-Kompatibilität:**
- ✅ Chrome (Desktop): Ja
- ✅ Safari (Desktop/Mobile): Ja
- ❌ Firefox (alle Plattformen): Nein
- ❌ Edge Mobile: Eingeschränkt
- ❌ Android Chrome: Eingeschränkt

---

## LÖSUNG: MANUELLE MP4-KONVERTIERUNG

### Option A: ffmpeg (Empfohlen für beste Qualität)

**Installation:**
```bash
# Windows (via Chocolatey)
choco install ffmpeg

# Windows (via Winget)
winget install Gyan.FFmpeg

# Manueller Download: https://ffmpeg.org/download.html#build-windows
```

**Konvertierung (alle 5 Videos):**
```bash
# Im Projektordner ausführen
cd "C:\Users\mickh\Desktop\alice-wondernails\public\assets\videos\Video Alice"

# Video 1
ffmpeg -i "Video_1.mov" -c:v libx264 -c:a aac -movflags +faststart "Video_1.mp4"

# Video 2
ffmpeg -i "Video_2.mov" -c:v libx264 -c:a aac -movflags +faststart "Video_2.mp4"

# Video 3
ffmpeg -i "Video_3.mov" -c:v libx264 -c:a aac -movflags +faststart "Video_3.mp4"

# Video 4
ffmpeg -i "Video_4.mov" -c:v libx264 -c:a aac -movflags +faststart "Video_4.mp4"

# Video 5
ffmpeg -i "Video_5.mov" -c:v libx264 -c:a aac -movflags +faststart "Video_5.mp4"
```

**Optimierte Einstellungen für Web:**
```bash
ffmpeg -i "Video_1.mov" -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -movflags +faststart "Video_1.mp4"
```

### Option B: HandBrake (GUI-Alternative)

1. **Download:** https://handbrake.fr/downloads.php
2. **Pro Video:** Source → MOV-Datei, Preset → "Web/General"
3. **Format:** MP4, Video Codec: H.264, Audio Codec: AAC
4. **Start Encoding** für alle 5 Videos

### Option C: Online-Konverter (für Tests)

**CloudConvert.com:**
1. Upload MOV → Konvertiere zu MP4 (H.264/AAC)
2. **VORSICHT:** Nicht für finale/sensitive Videos verwenden

---

## HTML-ANPASSUNG NACH KONVERTIERUNG

**Aktuell (nur MOV):**
```html
<video controls preload="metadata" playsinline>
  <source src="assets/videos/Video%20Alice/Video_1.mov" type="video/quicktime">
  <p>Dein Browser unterstützt dieses Videoformat nicht. 
     <a href="assets/videos/Video%20Alice/Video_1.mov" download>Video direkt herunterladen</a> 
     oder in einem anderen Browser versuchen.</p>
</video>
```

**Nach MP4-Konvertierung (Optimal):**
```html
<video controls preload="metadata" playsinline>
  <source src="assets/videos/Video%20Alice/Video_1.mp4" type="video/mp4">
  <source src="assets/videos/Video%20Alice/Video_1.mov" type="video/quicktime">
  <p>Dein Browser unterstützt dieses Videoformat nicht. 
     <a href="assets/videos/Video%20Alice/Video_1.mp4" download>Video (MP4) herunterladen</a> 
     oder <a href="assets/videos/Video%20Alice/Video_1.mov" download>Original (MOV) herunterladen</a>.</p>
</video>
```

---

## ERGEBNIS NACH KONVERTIERUNG

**Neue Browser-Kompatibilität:**
- ✅ Chrome (Desktop/Mobile): Ja
- ✅ Safari (Desktop/Mobile): Ja  
- ✅ Firefox (alle Plattformen): Ja
- ✅ Edge (Desktop/Mobile): Ja
- ✅ Android Chrome: Ja

**Upload-Größe:**
- MOV-Originale behalten (Backup)
- MP4 als primäre Quelle verwenden
- Geschätzte Größenreduktion: 15-30%

---

## AKZEPTANZKRITERIEN

✅ **Fertig wenn:**
- Alle 5 MP4-Dateien existieren neben MOV-Originalen
- HTML nutzt MP4 als erste `<source>`
- MOV bleibt als Fallback erhalten
- Videos starten in Firefox/Edge ohne Probleme
- Download-Links auf MP4 und MOV verfügbar

---

## ZEITAUFWAND

- **ffmpeg-Installation:** 5-10 Min
- **Konvertierung (5 Videos):** 10-20 Min
- **HTML-Update:** 5 Min
- **Test in Browsern:** 10 Min

**Gesamt:** ~30-45 Minuten

---

## WARUM NICHT AUTOMATISCH GEMACHT?

- ffmpeg nicht auf Entwicklungsumgebung installiert
- Keine Installation externer Tools ohne Genehmigung
- V1-Fokus auf Kern-Funktionalität
- Fallbacks bereits implementiert

## NÄCHSTER SCHRITT

1. **Entscheidung:** Videos konvertieren ODER mit MOV-Fallbacks live gehen
2. **Bei Konvertierung:** Obige Anweisungen befolgen
3. **Bei Fallbacks:** Status in V1_RELEASE_STATUS.md als bekanntes Risiko dokumentieren