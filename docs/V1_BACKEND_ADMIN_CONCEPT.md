# V1 Backend-/Admin-Konzept - Alice Wonder Nails

## 1. Ziel der V1-Erweiterung

Die V1-Landingpage soll vor dem Upload um ein kleines, sicheres Backend erweitert werden.
Zweck: Kontaktanfragen und einmalige Start-Benachrichtigungen erfassen.

Nicht Bestandteil der V1-Erweiterung:
- kein Shop
- kein Kundenkonto
- kein dauerhafter Newsletter
- kein automatisierter Werbeversand
- kein Tracking
- kein Social-Media-Embed
- kein Produktverwaltungssystem
- kein Grosshandelssystem

## 2. Grundentscheidung

Backend:
Python FastAPI

Datenbank:
SQLite

Admin:
kleiner geschuetzter Adminbereich nur fuer Michael Hornung

Export:
CSV-Export fuer Excel-Auswertung

Wichtig:
Excel ist nur Exportformat, nicht Datenspeicher.

## 3. Zweck der Datenerfassung

Es gibt zwei getrennte Zwecke:

1. Kontaktanfrage
- Nutzer kann eine Anfrage stellen.
- Antwort erfolgt individuell/manuell.

2. Einmalige Start-Benachrichtigung
- Nutzer erlaubt ausdruecklich, genau eine E-Mail zu erhalten, sobald Alice Wonder Nails startet bzw. der Shop/die neue Webseite eroeffnet ist.
- Diese Einwilligung ist kein dauerhafter Newsletter.
- Nach Versand dieser einen Start-E-Mail werden die personenbezogenen Daten geloescht oder anonymisiert.
- Spaetestens nach 6 Monaten werden alle nicht mehr benoetigten Early-Access-Datensaetze automatisch geloescht.

## 4. Erfasste Daten im Formular

Pflicht:
- E-Mail-Adresse
- Datenschutz-Zustimmung

Optional:
- Name
- Interesse-Auswahl
- Nachricht
- Einwilligung zur einmaligen Start-Benachrichtigung

Interesse-Auswahl:
- Press-On-Anfrage
- Modellarbeit
- Shopstart / erste Boxen
- Haendler-/Studiointeresse
- Sonstiges

Technisch:
- Erfassungszeitpunkt
- Status
- interne Admin-Notiz
- Loeschfrist / delete_after
- Versandzeitpunkt der einmaligen Benachrichtigung, falls erfolgt

Nicht erfassen:
- Adresse
- Telefonnummer
- Geburtsdatum
- Zahlungsdaten
- Passwort
- Kundendaten
- Trackingdaten

## 5. Einwilligung / Start-Benachrichtigung

Klar festlegen:
- Kontaktanfrage und Start-Benachrichtigung muessen getrennt sein.
- Die Einwilligung zur Start-Benachrichtigung darf nicht vorausgewaehlt sein.
- Es wird kein dauerhafter Newsletter gebaut.
- Es wird keine automatische Newsletter-Serie gebaut.
- Es wird keine Werbung in Dauerschleife verschickt.
- Es geht nur um genau eine E-Mail: "Alice Wonder Nails ist gestartet / Shop ist eroeffnet."
- Danach werden die Daten geloescht oder anonymisiert.
- Spaetestens nach 6 Monaten automatische Loeschung.

Formulartext-Vorschlag:
[ ] Ich moechte einmalig per E-Mail informiert werden, wenn Alice Wonder Nails startet bzw. der Shop eroeffnet. Meine Daten werden ausschliesslich fuer diese Start-Benachrichtigung verwendet und anschliessend geloescht. Spaetestens nach 6 Monaten werden meine Daten automatisch geloescht.

Zusatzhinweis:
Die Einwilligung kann jederzeit per E-Mail widerrufen werden. Weitere Informationen stehen in der Datenschutzerklaerung.

Double-Opt-In:
- Fuer eine spaetere werbliche Start-Benachrichtigung soll Double-Opt-In vorgesehen oder als Sicherheitsanforderung dokumentiert werden.
- Falls Double-Opt-In in V1 noch nicht implementiert wird, darf kein automatischer Werbeversand erfolgen.
- Fuer produktiven Versand muss die Nachweisbarkeit der Einwilligung geklaert sein.

## 6. Datenmodell SQLite

Tabelle:
leads

Felder vorschlagen:
- id INTEGER PRIMARY KEY
- created_at TEXT NOT NULL
- email TEXT NOT NULL
- name TEXT NULL
- interest TEXT NULL
- message TEXT NULL
- privacy_accepted INTEGER NOT NULL
- one_time_notice_accepted INTEGER NOT NULL DEFAULT 0
- status TEXT NOT NULL DEFAULT 'neu'
- admin_note TEXT NULL
- notice_sent_at TEXT NULL
- exported_at TEXT NULL
- delete_after TEXT NOT NULL
- deleted_at TEXT NULL

Optional fuer spaeteres Double-Opt-In:
- double_opt_in_status TEXT NULL
- double_opt_in_token_hash TEXT NULL
- double_opt_in_sent_at TEXT NULL
- double_opt_in_confirmed_at TEXT NULL

Wichtig:
- keine unnoetigen personenbezogenen Daten
- keine Klartext-Passwoerter, weil keine Kundenkonten
- Loeschung/Soft-Delete oder echte Loeschung bewusst festlegen
- SQLite-Datei darf niemals im public/-Ordner liegen

## 7. Loeschkonzept

Festlegen:
- Daten werden nur so lange gespeichert, wie sie fuer Kontakt oder Start-Benachrichtigung benoetigt werden.
- Nach Versand der einmaligen Start-Benachrichtigung:
  - Datensatz loeschen oder personenbezogene Daten anonymisieren.
- Spaetestens nach 6 Monaten:
  - automatische Loeschung oder Admin-Wartungsfunktion zur Loeschung.
- Adminbereich muss Loeschstatus anzeigen.
- CSV-Export darf keine bereits geloeschten/anonymisierten Datensaetze unnoetig enthalten.
- Geloeschte Datensaetze duerfen nicht mehr aktiv genutzt werden.

## 8. Adminbereich V1

Admin darf:
- einloggen
- Leads ansehen
- Lead-Status aendern:
  - neu
  - gesehen
  - beantwortet
  - erledigt
  - Startmail gesendet
  - geloescht
- Admin-Notiz setzen
- CSV exportieren
- einzelne Leads loeschen oder anonymisieren
- abgelaufene Datensaetze loeschen
- Datensatz als "Start-Benachrichtigung gesendet" markieren

Admin darf NICHT:
- Newsletter verschicken, sofern nicht ausdruecklich spaeter gebaut
- Kundenkonten verwalten
- Shop verwalten
- Produkte verwalten
- Medien hochladen
- Rollen/Grosshandel verwalten

## 9. Admin-Sicherheit

Festlegen:
- Admin-Zugang nicht offen bewerben
- Admin-Passwort nicht im Code
- Secrets ueber .env
- Passwort-Hash verwenden
- Session sicher konfigurieren
- CSRF-Schutz fuer Admin-Aktionen
- Rate-Limit fuer Login und Formular
- Honeypot im Formular
- keine sensiblen Daten in Logs
- SQLite-Datei ausserhalb oeffentlich auslieferbarer Ordner speichern
- CSV-Export nur nach Login
- HTTPS im Livebetrieb Pflicht

## 10. Geplante Projektstruktur

Vorschlag:

backend/
  app.py
  config.py
  database.py
  models.py
  schemas.py
  security.py
  routes/
    public.py
    admin.py
  services/
    export_service.py
    lead_service.py
    cleanup_service.py
  templates/
    admin_login.html
    admin_dashboard.html

data/
  db/
    alicewonder_v1.sqlite
  exports/

public/
  index.html
  impressum.html
  datenschutz.html
  assets/

docs/
  V1_BACKEND_ADMIN_CONCEPT.md

Wichtig:
- data/ darf niemals oeffentlich hochgeladen werden, wenn Webserver direkt public/ ausliefert.
- SQLite-Datei darf nicht unter public/ liegen.

## 11. Datenschutz-Anpassungen bei produktivem Formular

Datenschutz muss spaeter ergaenzen:
- Zweck der Verarbeitung:
  Kontaktanfrage und einmalige Start-Benachrichtigung
- Art der Daten:
  E-Mail, optional Name, Interesse, Nachricht, Zeitpunkt, Einwilligungsstatus
- Rechtsgrundlage
- Speicherdauer:
  Loeschung nach Zweckerfuellung, spaetestens nach 6 Monaten
- Widerrufsmoeglichkeit
- Loeschmoeglichkeit
- Hosting/Serverlogs
- keine Weitergabe ausser technisch notwendige Dienstleister
- kein Tracking
- kein dauerhafter Newsletter
- keine automatische Werbeserie
- Start-Benachrichtigung nur einmalig nach Einwilligung

## 12. Upload-/Deployment-Hinweis

Festlegen:
- Statische public/-Dateien allein reichen dann nicht mehr.
- Fuer FastAPI wird ein Python-faehiges Hosting oder ein geeigneter Server/Deployment-Weg benoetigt.
- Vor Implementierung pruefen:
  - ob aktueller STRATO-Tarif Python/FastAPI dauerhaft ausfuehren kann
  - falls nicht: V1 entweder statisch live lassen oder Backend separat hosten
- Keine Annahmen treffen, sondern Deployment-Faehigkeit pruefen.

## 13. Umsetzungsreihenfolge

Empfohlene naechste Auftraege:

1. Backend-Ordnerstruktur und lokale FastAPI-App erstellen
2. SQLite-Datenmodell und Init-Skript bauen
3. Formular an Backend anschliessen
4. Adminlogin bauen
5. Admin-Dashboard Leads
6. CSV-Export
7. Loesch-/Cleanup-Funktion
8. Datenschutzseite an produktive Funktion anpassen
9. Sicherheits-/Spamtests
10. Deployment-Pruefung
11. Upload/Livegang

## 14. Akzeptanzkriterien fuer spaetere Implementierung

GRUEN erst wenn:
- Formular speichert korrekt in SQLite
- Datenschutz-Haken Pflicht ist
- Einwilligung zur einmaligen Start-Benachrichtigung optional und nicht vorausgewaehlt ist
- Adminlogin funktioniert
- Passwort nicht im Code steht
- Leads sichtbar sind
- Status/Notiz aenderbar ist
- CSV-Export funktioniert
- Loeschfunktion vorhanden ist
- automatische/administrative Loeschung nach spaetestens 6 Monaten beruecksichtigt ist
- Datenbank nicht oeffentlich erreichbar ist
- keine Trackingtools eingebaut wurden
- Impressum/Datenschutz angepasst sind
- lokale Tests dokumentiert sind
