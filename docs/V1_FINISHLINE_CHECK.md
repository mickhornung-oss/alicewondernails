# V1 Finishline Check - Alice Wonder Nails

## 1. Aktueller Stand

Die Landingpage ist als statische V1 unter `public/index.html` vorhanden, inklusive CSS/JS, Splashscreen, echter Bilder, echter Videos, Instagram-Link und Kontaktformular-Prototyp (ohne echten Versand). Technisch ist der Stand lokal startbar, aber inhaltlich und rechtlich noch nicht upload-fertig.

## 2. Was bereits fertig wirkt

- Grundstruktur der Seite ist vollstaendig vorhanden (Header, Hero, Inhalte, Galerie, Videos, Kontakt, Footer).
- Splashscreen mit echtem Logo ist eingebunden und wird per JS automatisch ausgeblendet.
- 5 echte Bilder sind im Galerie-Bereich eingebunden.
- 5 echte Videos sind im Video-Bereich eingebunden.
- Instagram-Link ist gesetzt (`https://www.instagram.com/alicewonder_nails/`) und oeffnet im neuen Tab.
- CTA-Buttons und Pill-/Kategorie-Buttons sind visuell einheitlich gestaltet.
- Relative Pfade werden genutzt; keine absoluten Windows-Pfade in HTML/CSS/JS gefunden.
- Keine externen CDN- oder Tracking-Skripte eingebunden.
- Keine Shop-/Login-/Admin-Funktionen live implementiert.

## 3. Was noch fehlt

- Finale inhaltliche Texte fuer mehrere Bereiche fehlen weiterhin.
- Bildtitel/-beschreibungen und Videotitel/-beschreibungen sind noch neutral/technisch.
- Rechtliche Seiten (Impressum, Datenschutz) fehlen als eigene Seiten.
- Footer enthaelt aktuell keine verlinkten Impressum-/Datenschutzseiten.
- Browser-Playback fuer `.mov`-Videos ist nicht final verifiziert (Codec-Risiko je Browser).
- Echte visuelle Endabnahme (Desktop + Mobile) vor Upload steht noch aus.

## 4. Offene Texte

| Bereich | Was fehlt | Wer liefert | Prioritaet |
|---|---|---|---|
| Hero-Hauptbereich | Finaler Claim + Einfuehrung (statt Platzhalter) | Frau/Tochter | Hoch |
| Markenvorstellung | Finaler Markentext | Frau/Tochter | Hoch |
| Designerin-Vorstellung | Finaler persoenlicher Vorstellungstext | Frau/Tochter | Hoch |
| Press-On/Modellarbeiten | Finaler Bereichstext | Frau/Tochter | Hoch |
| Galerie-Einleitung | Finaler Einleitungstext | Frau/Tochter | Mittel |
| Bildkarten (5) | Pro Bild: finaler Titel + Kurzbeschreibung + Kategorie | Frau/Tochter | Hoch |
| Video-Einleitung | Finaler Einleitungstext | Frau/Tochter | Mittel |
| Videokarten (5) | Pro Video: finaler Titel + Kurzbeschreibung | Frau/Tochter | Hoch |
| Social-Media-Text | Finaler Begleittext fuer Social-Bereich | Frau/Tochter | Mittel |
| Kontakt / Early Access | Finaler Hinweistext fuer Kontakt und Early Access | Frau/Tochter | Hoch |
| Shop kommt bald | Finaler Coming-Soon-Text | Frau/Tochter | Mittel |
| Haendler / Grosshandel | Finaler Teasertext | Frau/Tochter | Mittel |
| Footer-Kurztext | Finaler kurzer Markentext im Footer | Frau/Tochter | Niedrig |

## 5. Rechtliche offene Punkte

- **Impressum:** Seite fehlt.
- **Datenschutz:** Seite fehlt.
- **Footer-Links:** Keine echten Links auf Impressum/Datenschutz vorhanden.
- **Cookie-/Tracking-Hinweis:** Aktuell kein Tracking eingebunden; bei spaeterem Tracking ist ein entsprechender Hinweis erforderlich.
- **Kontaktformular/Early Access:** Derzeit nur Frontend-Prototyp ohne Versand; vor Livegang sind rechtlich gepruefte Hinweise/Einwilligungstexte noetig.

## 6. Upload-Check

- **Upload-Basis:** `public/`
- **Benoetigte Dateien/Ordner:**
  - `public/index.html`
  - `public/assets/css/style.css`
  - `public/assets/js/main.js`
  - `public/assets/logo/Logo fest.png`
  - `public/assets/images/Bilder Alice/*`
  - `public/assets/videos/Video Alice/*`
- **Relative Pfade:** in HTML/CSS/JS vorhanden und konsistent.
- **Medien vorhanden:** ja (5 Bilder, 5 Videos).
- **Open-in-file-Betrieb:** Seite laedt als lokale Datei grundsaetzlich; interaktive Bereiche laufen per lokalem JS.
- **Offene Risiken vor Upload:**
  - Fehlende Rechtsseiten/Links.
  - Noch offene Finaltexte.
  - `.mov`-Wiedergabe je Browser moeglicherweise eingeschraenkt.
  - Leerzeichen in Medienordnernamen sind technisch handhabbar, sollten aber vor Livebetrieb konsistent verwaltet bleiben.

## 7. Empfehlung fuer naechste Schritte

1. Finaltexte gemass `docs/CONTENT_BRIEFING_MODUL_1.md` liefern und in die Seite einsetzen.
2. Impressum- und Datenschutzseiten erstellen lassen (rechtlich geprueft) und im Footer verlinken.
3. Videoformate fuer breite Browser-Kompatibilitaet pruefen (ggf. MP4/H.264-Varianten bereitstellen).
4. Endabnahme im Browser durchfuehren (Desktop + Mobile, inklusive Video-Playback und Formularhinweise).
5. Danach `public/` als Upload-Paket verwenden und einen letzten Link-/Pfad-Check ausfuehren.
