# VIDEO-KOMPATIBILITÄTS-HINWEISE

## Aktueller Stand

Die V1 verwendet 5 Videos im .mov-Format:
- Video_1.mov bis Video_5.mov im Ordner `public/assets/videos/Video Alice/`

## Browser-Kompatibilitätsproblem

**.mov-Format (QuickTime) Unterstützung:**
- ✅ Chrome (Desktop): Ja
- ✅ Safari (Desktop/Mobile): Ja
- ❌ Firefox (alle Plattformen): Nein
- ❌ Edge Mobile: Eingeschränkt
- ❌ Android Chrome: Eingeschränkt

**Geschätzte Auswirkung:** 40-50% der Besucher können Videos nicht abspielen.

## Implementierte Verbesserungen

✅ **Für V1 umgesetzt:**
- Explizite MIME-Type-Deklaration (`type="video/quicktime"`)
- Verbesserte Fallback-Messages mit Download-Link
- HTML5-Video-Attribute für optimale Darstellung:
  - `controls` - Benutzer-Steuerung
  - `preload="metadata"` - Lädt nur Metadaten
  - `playsinline` - Mobile Optimierung

## Empfehlung für spätere Versionen

**Für bessere Browser-Kompatibilität:**
1. Videos zu MP4 (H.264) konvertieren:
   ```bash
   ffmpeg -i Video_1.mov -c:v libx264 -c:a aac -movflags +faststart Video_1.mp4
   ```
2. Mehrere Formate anbieten:
   ```html
   <video controls preload="metadata" playsinline>
     <source src="video.mp4" type="video/mp4">
     <source src="video.webm" type="video/webm">
     <source src="video.mov" type="video/quicktime">
     <p>Fallback...</p>
   </video>
   ```

**Warum nicht in V1:**
- ffmpeg nicht verfügbar auf Entwicklungsumgebung
- Keine Installation externer Tools gewünscht
- V1-Fokus auf Kern-Funktionalität

## Workaround für Benutzer

Benutzer mit inkompatiblen Browsern können:
1. Videos direkt herunterladen (Link in Fallback-Message)
2. In Safari/Chrome öffnen
3. QuickTime Player verwenden (Desktop)